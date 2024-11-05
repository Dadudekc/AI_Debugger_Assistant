# Path: ai_agent_project/src/core/agent_dispatcher.py

import importlib
import logging
import os
import sys
import asyncio
from typing import Any, Dict, Optional, Callable
from pathlib import Path
from aio_limiter import AsyncLimiter
import time

# Add the project root directory to the system path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from utilities.ai_agent_utils import PerformanceMonitor, MemoryManager
from utilities.ChainOfThoughtReasoner import ChainOfThoughtReasoner
from plugins.plugin_interface import AgentPlugin
from db.database import async_session
from db.models import Agent, Task
from sqlalchemy.future import select
from utilities.ai_cache import AICache

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Prevent duplicate handlers
if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# Metrics placeholders (implement with your preferred metrics library, e.g., Prometheus)
# Example:
# from prometheus_client import Counter, Histogram

# TASK_SUBMITTED = Counter('tasks_submitted_total', 'Total tasks submitted')
# TASK_COMPLETED = Counter('tasks_completed_total', 'Total tasks completed')
# TASK_FAILED = Counter('tasks_failed_total', 'Total tasks failed')
# TASK_DURATION = Histogram('task_duration_seconds', 'Duration of task execution')
# TASK_IN_PROGRESS = Counter('tasks_in_progress', 'Tasks currently in progress')


class AgentDispatcher:
    """
    Dispatches tasks to agents, supporting chain-of-thought reasoning,
    dynamic agent loading via plugins, and persistent task management.
    """

    def __init__(
        self,
        agents_directory: str,
        model_name: str = "mistral-model",
        ollama_url: str = "http://localhost:11434",
        max_retries: int = 3,
    ):
        """
        Initializes the AgentDispatcher with necessary utilities and dynamically loads agents.

        Args:
            agents_directory (str): The directory where agent plugin modules are located.
            model_name (str): The name of the Mistral model configured in Ollama.
            ollama_url (str): The base URL for the Ollama API.
            max_retries (int): Maximum number of retries for task execution.
        """
        self.memory_manager = MemoryManager()
        self.performance_monitor = PerformanceMonitor()
        self.max_retries = max_retries
        self.agents = self.load_agents(agents_directory)
        self.task_queue = asyncio.PriorityQueue()
        self.dead_letter_queue = asyncio.Queue()
        self.chain_of_thought_reasoner = ChainOfThoughtReasoner(
            agent_dispatcher=self,
            model_name=model_name,
            ollama_url=ollama_url,
        )
        self.rate_limiters = {
            agent_name: AsyncLimiter(10, 60) for agent_name in self.agents.keys()
        }  # Example: 10 tasks per 60 seconds per agent
        self.ai_cache = AICache("ai_cache.json")
        logger.info("AgentDispatcher initialized with dynamically loaded agents.")

    def load_agents(self, agents_directory: str) -> Dict[str, AgentPlugin]:
        """
        Loads agent plugins from the specified directory.

        Args:
            agents_directory (str): Directory containing agent plugin modules.

        Returns:
            Dict[str, AgentPlugin]: Loaded agent instances.
        """
        agents = {}
        if not os.path.isdir(agents_directory):
            logger.error(f"Agents directory '{agents_directory}' does not exist.")
            return agents

        logger.info(f"Loading agent plugins from directory: {agents_directory}")

        for filename in os.listdir(agents_directory):
            if not filename.endswith(".py") or filename.startswith("__"):
                continue

            module_name = filename[:-3]  # Remove .py extension
            try:
                module_spec = importlib.util.spec_from_file_location(
                    module_name, os.path.join(agents_directory, filename)
                )
                module = importlib.util.module_from_spec(module_spec)
                module_spec.loader.exec_module(module)

                # Find classes inheriting from AgentPlugin
                for attribute_name in dir(module):
                    attribute = getattr(module, attribute_name)
                    if (
                        isinstance(attribute, type)
                        and issubclass(attribute, AgentPlugin)
                        and attribute is not AgentPlugin
                    ):
                        agent_instance = attribute(
                            name=attribute_name.lower(),
                            memory_manager=self.memory_manager,
                            performance_monitor=self.performance_monitor,
                            dispatcher=self,
                        )
                        agents[agent_instance.name] = agent_instance
                        logger.info(f"Loaded agent plugin: {agent_instance.name}")
            except Exception as e:
                logger.exception(f"Failed to load agent plugin '{module_name}': {e}")

        logger.info(f"Total agents loaded: {len(agents)} - {list(agents.keys())}")
        return agents

    async def dispatch_task(
        self,
        task: str,
        agent_name: str,
        priority: int = 1,
        use_chain_of_thought: bool = False,
        **kwargs
    ) -> Optional[Any]:
        """
        Dispatches a task to an agent, with optional Chain-of-Thought reasoning.

        Args:
            task (str): Task description.
            agent_name (str): Target agent name.
            priority (int): Task priority; lower numbers are higher priority.
            use_chain_of_thought (bool): Whether to use CoT reasoning.
            **kwargs: Additional arguments for the agent.

        Returns:
            Optional[Any]: Task result if CoT is used, else None.
        """
        logger.debug(
            f"Dispatching task '{task}' to agent '{agent_name}' with priority '{priority}'."
        )

        # Persist task to the database
        async with async_session() as session:
            stmt = select(Agent).where(Agent.name == agent_name)
            result = await session.execute(stmt)
            agent_record = result.scalars().first()
            if not agent_record:
                error_message = f"Agent '{agent_name}' not found in database."
                logger.error(error_message)
                # TASK_FAILED.inc()
                return error_message

            new_task = Task(
                description=task,
                agent_id=agent_record.id,
                priority=priority,
                use_chain_of_thought=use_chain_of_thought,
                status="queued",
            )
            session.add(new_task)
            await session.commit()
            logger.info(
                f"Task '{task}' persisted to database with ID {new_task.id}."
            )

        if use_chain_of_thought:
            return await self._execute_with_chain_of_thought(task, agent_name)
        else:
            # Enqueue the task
            await self.task_queue.put((priority, task, agent_name, kwargs))
            logger.info(
                f"Task '{task}' enqueued for agent '{agent_name}' with priority '{priority}'."
            )
            return None

    async def _execute_with_chain_of_thought(
        self, task: str, agent_name: str
    ) -> Optional[str]:
        """
        Executes a task using Chain-of-Thought reasoning.

        Args:
            task (str): Task description.
            agent_name (str): Target agent name.

        Returns:
            Optional[str]: Result from CoT reasoning.
        """
        logger.info(
            f"Executing task '{task}' with Chain-of-Thought for agent '{agent_name}'."
        )
        try:
            result = await self.chain_of_thought_reasoner.solve_task_with_reasoning(
                task, agent_name
            )
            logger.info(f"CoT task '{task}' completed with result: {result}")
            # Update task status in the database
            await self._update_task_status(task, agent_name, "completed", result)
            return result
        except Exception as e:
            error_message = f"Error during CoT reasoning for task '{task}': {str(e)}"
            logger.exception(error_message)
            # Update task status as failed
            await self._update_task_status(task, agent_name, "failed", error_message)
            return error_message

    async def _execute_standard_task(
        self,
        priority: int,
        task: str,
        agent_name: str,
        kwargs: Dict[str, Any],
        retry_count: int = 0,
    ) -> Optional[str]:
        """
        Executes a standard task asynchronously with retry logic and rate limiting.

        Args:
            priority (int): Task priority.
            task (str): Task description.
            agent_name (str): Target agent name.
            kwargs (Dict[str, Any]): Additional arguments for the agent.
            retry_count (int): Current retry attempt.

        Returns:
            Optional[str]: Result from the task execution.
        """
        agent = self.agents.get(agent_name)
        if not agent:
            error_message = f"Agent '{agent_name}' not found."
            logger.error(error_message)
            # TASK_FAILED.inc()
            return error_message

        # Rate limiting
        rate_limiter = self.rate_limiters.get(agent_name)
        if rate_limiter:
            await rate_limiter.acquire()

        # Persist task status as running
        async with async_session() as session:
            stmt = select(Task).where(
                Task.description == task,
                Task.agent_id == agent.id,
                Task.status == "queued",
            ).order_by(Task.created_at.desc())
            result = await session.execute(stmt)
            current_task = result.scalars().first()

            if not current_task:
                error_message = f"No matching queued task found for '{task}' and agent '{agent_name}'."
                logger.error(error_message)
                # TASK_FAILED.inc()
                return error_message

            # Update task status to running
            current_task.status = "running"
            await session.commit()

        # Metrics placeholders (implement counters)
        # TASK_SUBMITTED.inc()
        # TASK_IN_PROGRESS.inc()
        start_time = time.time()

        try:
            result = await agent.solve_task(task, **kwargs)
            self.performance_monitor.log_performance(agent_name, task, result)
            # TASK_COMPLETED.inc()
            logger.info(
                f"Task '{task}' executed by agent '{agent_name}' with result: {result}"
            )

            # Update task status to completed
            async with async_session() as session:
                stmt = select(Task).where(Task.id == current_task.id)
                result = await session.execute(stmt)
                task_record = result.scalars().first()
                if task_record:
                    task_record.status = "completed"
                    task_record.result = result
                    await session.commit()

            return result
        except Exception as e:
            # TASK_FAILED.inc()
            logger.exception(
                f"Error executing task '{task}' for agent '{agent_name}': {e}"
            )
            if retry_count < self.max_retries:
                backoff = 2 ** retry_count
                logger.info(
                    f"Retrying task '{task}' for agent '{agent_name}' in {backoff} seconds (Attempt {retry_count + 1}/{self.max_retries})"
                )
                await asyncio.sleep(backoff)
                return await self._execute_standard_task(
                    priority, task, agent_name, kwargs, retry_count + 1
                )
            else:
                logger.error(
                    f"Task '{task}' for agent '{agent_name}' failed after {self.max_retries} attempts. Moving to dead-letter queue."
                )
                await self.dead_letter_queue.put((priority, task, agent_name, kwargs))
                self._send_alert(
                    f"Task '{task}' for agent '{agent_name}' failed after {self.max_retries} attempts."
                )
                # Update task status as failed
                async with async_session() as session:
                    stmt = select(Task).where(Task.id == current_task.id)
                    result = await session.execute(stmt)
                    task_record = result.scalars().first()
                    if task_record:
                        task_record.status = "failed"
                        task_record.result = str(e)
                        await session.commit()
                return f"Error executing task: {e}"
        finally:
            duration = time.time() - start_time
            # TASK_DURATION.observe(duration)
            # TASK_IN_PROGRESS.dec()
            logger.debug(f"Task '{task}' duration: {duration} seconds.")
            if rate_limiter:
                rate_limiter.release()

    async def execute_tasks(self):
        """
        Executes tasks from the priority queue asynchronously.
        """
        logger.info("Starting task execution loop.")
        while True:
            if not self.task_queue.empty():
                priority, task, agent_name, kwargs = await self.task_queue.get()
                logger.debug(
                    f"Dequeuing task '{task}' for agent '{agent_name}' with priority '{priority}'."
                )
                asyncio.create_task(
                    self._execute_standard_task(priority, task, agent_name, kwargs)
                )
            else:
                await asyncio.sleep(1)  # Adjust sleep time as needed

    async def run(self):
        """
        Starts the dispatcher and begins processing tasks.
        """
        logger.info("AgentDispatcher is running.")
        await asyncio.gather(
            self.execute_tasks(),
            self.monitor_dead_letter_queue(),
        )

    async def monitor_dead_letter_queue(self):
        """
        Monitors the dead-letter queue for failed tasks.
        """
        while True:
            if not self.dead_letter_queue.empty():
                priority, task, agent_name, kwargs = await self.dead_letter_queue.get()
                logger.warning(
                    f"Dead-letter task '{task}' for agent '{agent_name}' detected. Manual intervention required."
                )
                # Implement alerting or logging mechanisms here
            else:
                await asyncio.sleep(5)  # Adjust sleep time as needed

    def add_agent(self, agent_instance: AgentPlugin):
        """
        Adds a new agent to the dispatcher dynamically.

        Args:
            agent_instance (AgentPlugin): The agent instance to add.
        """
        self.agents[agent_instance.name] = agent_instance
        self.rate_limiters[agent_instance.name] = AsyncLimiter(10, 60)  # Example rate limit
        logger.info(f"Added agent '{agent_instance.name}' dynamically.")

    def remove_agent(self, agent_name: str):
        """
        Removes an agent from the dispatcher.

        Args:
            agent_name (str): The name of the agent to remove.
        """
        if agent_name in self.agents:
            del self.agents[agent_name]
            del self.rate_limiters[agent_name]
            logger.info(f"Removed agent '{agent_name}' from dispatcher.")
        else:
            logger.warning(f"Attempted to remove non-existent agent '{agent_name}'.")

    def list_agents(self) -> list:
        """
        Lists all registered agents.

        Returns:
            list: Names of all agents currently available.
        """
        agent_names = list(self.agents.keys())
        logger.info("Registered agents:")
        for name in agent_names:
            capabilities = (
                self.agents[name].describe_capabilities()
                if hasattr(self.agents[name], "describe_capabilities")
                else "No description available."
            )
            logger.info(f" - {name}: {capabilities}")
        return agent_names

    async def _update_task_status(
        self, task: str, agent_name: str, status: str, result: Optional[str]
    ):
        """
        Updates the status and result of a task in the database.

        Args:
            task (str): Task description.
            agent_name (str): Target agent name.
            status (str): New status ('completed', 'failed', etc.).
            result (Optional[str]): Result or error message.
        """
        async with async_session() as session:
            stmt = select(Agent).where(Agent.name == agent_name)
            result_agent = await session.execute(stmt)
            agent_record = result_agent.scalars().first()

            if not agent_record:
                logger.error(
                    f"Agent '{agent_name}' not found in database while updating task '{task}'."
                )
                return

            stmt = select(Task).where(
                Task.description == task,
                Task.agent_id == agent_record.id,
                Task.status.in_(["running", "queued"]),
            ).order_by(Task.created_at.desc())
            result_task = await session.execute(stmt)
            task_record = result_task.scalars().first()

            if task_record:
                task_record.status = status
                task_record.result = result
                await session.commit()
                logger.info(
                    f"Task '{task}' for agent '{agent_name}' updated to status '{status}'."
                )
            else:
                logger.error(
                    f"No matching task found in database for task '{task}' and agent '{agent_name}'."
                )

    def _send_alert(self, message: str):
        """
        Sends an alert for critical failures.

        Args:
            message (str): Alert message.
        """
        # Implement alerting mechanisms (e.g., email, Slack)
        logger.error(f"ALERT: {message}")
