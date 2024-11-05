# File Path: C:\Projects\AI_Debugger_Assistant\ai_agent_project\src\agents\core\AgentDispatcher.py

import logging
import os
import sys
import asyncio
from typing import Any, Dict, Optional, Callable
import importlib
from utilities.ai_agent_utils import PerformanceMonitor, MemoryManager
from utilities.ChainOfThoughtReasoner import ChainOfThoughtReasoner

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Set to DEBUG for detailed logs

# Prevent adding multiple handlers if already present
if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)


class AgentDispatcher:
    """
    Dispatches tasks to the appropriate agent, supporting chain-of-thought reasoning
    and dynamic agent loading. Utilizes asynchronous execution for improved performance.
    """

    def __init__(
        self,
        agents_directory: str,
        model_name: str = "mistral-model",
        ollama_url: str = "http://localhost:11434",
    ):
        """
        Initializes the AgentDispatcher with necessary utilities and dynamically loads agents.

        Args:
            agents_directory (str): The directory where agent modules are located.
            model_name (str): The name of the Mistral model configured in Ollama.
            ollama_url (str): The base URL for the Ollama API.
        """
        self.memory_manager = MemoryManager()
        self.performance_monitor = PerformanceMonitor()
        self.agents = {}
        self.task_queue = asyncio.PriorityQueue()
        self.loop = asyncio.get_event_loop()
        self.chain_of_thought_reasoner = ChainOfThoughtReasoner(
            agent_dispatcher=self,
            model_name=model_name,
            ollama_url=ollama_url,
        )
        self.agents = self.load_agents(agents_directory)
        logger.info("AgentDispatcher initialized with dynamically loaded agents.")

    async def dispatch_task(
        self,
        task: str,
        agent_name: str,
        priority: int = 1,
        use_chain_of_thought: bool = False,
        **kwargs
    ) -> Optional[Any]:
        """
        Dispatches a task to the specified agent.

        Args:
            task (str): The task description.
            agent_name (str): The agent assigned to the task.
            priority (int): Priority level for the task (lower numbers indicate higher priority).
            use_chain_of_thought (bool): Whether to use chain-of-thought reasoning.
            **kwargs: Additional keyword arguments for the agent.

        Returns:
            Optional[Any]: Returns task result immediately if CoT is used, else None.
        """
        logger.debug(f"Preparing to dispatch task '{task}' for agent '{agent_name}' with priority '{priority}'.")

        # Validate agent existence
        if agent_name not in self.agents:
            logger.error(f"Agent '{agent_name}' not found. Available agents: {list(self.agents.keys())}")
            return "Error: Specified agent does not exist."

        agent = self.agents[agent_name]

        # Chain-of-Thought Reasoning Execution
        if use_chain_of_thought:
            logger.info(f"Dispatching task '{task}' to '{agent_name}' with Chain-of-Thought reasoning.")
            try:
                result = await self.chain_of_thought_reasoner.solve_task_with_reasoning(task, agent_name)
                logger.info(f"CoT Task '{task}' completed with result: {result}")
                return result
            except Exception as e:
                logger.exception(f"Error during Chain-of-Thought reasoning for task '{task}': {e}")
                return f"Error during CoT execution: {str(e)}"

        # Standard Task Execution
        else:
            logger.info(f"Dispatching task '{task}' to agent '{agent_name}' with priority {priority}")
            try:
                result = await agent.solve_task(task, **kwargs)
                self.performance_monitor.log_performance(agent_name, task, result)
                logger.info(f"Task '{task}' completed by '{agent_name}' with result: {result}")
                return result
            except Exception as e:
                logger.error(f"Error executing task '{task}' for agent '{agent_name}': {e}")
                return f"Error executing task: {str(e)}"

    def load_agents(self, agents_directory: str) -> Dict[str, Any]:
        """
        Dynamically loads agents from the specified agents directory,
        with configurable initialization parameters for each agent.

        Args:
            agents_directory (str): Path to the directory containing agent modules.

        Returns:
            Dict[str, Any]: Dictionary of loaded agent instances.
        """
        agents = {}
        
        # Validate if the agents directory exists
        if not os.path.isdir(agents_directory):
            logger.error(f"Agents directory '{agents_directory}' does not exist. Please check the path.")
            return agents

        logger.info(f"Loading agents from directory: {agents_directory}")
        
        agent_configs = {
            'aiwithmemory': {
                'class': 'AIAgentWithMemory',
                'params': {
                    'name': 'Jarvis',
                    'project_name': 'HomeAutomation',
                    'memory_manager': self.memory_manager,
                    'performance_monitor': self.performance_monitor,
                    'dispatcher': self
                }
            }
            # Add additional agent-specific configurations as needed
        }
        
        for filename in os.listdir(agents_directory):
            # Skip `AgentDispatcher.py` to prevent recursive loading
            if filename == "AgentDispatcher.py" or not filename.endswith(".py") or filename.startswith("__"):
                continue

            module_name = filename[:-3]  # Remove .py extension
            agent_name = module_name.replace('Agent', '').lower()
            
            try:
                # Construct the full path for the agent module
                module_path = os.path.join(agents_directory, filename)
                spec = importlib.util.spec_from_file_location(module_name, module_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Determine the class name based on config or default to module name
                agent_class_name = agent_configs.get(agent_name, {}).get('class', module_name)
                agent_class = getattr(module, agent_class_name, None)

                if agent_class is None:
                    logger.warning(f"Module '{module_name}' does not define a class '{agent_class_name}'. Skipping.")
                    continue

                # Initialize the agent if init parameters exist
                init_params = agent_configs.get(agent_name, {}).get('params', {})
                agents[agent_name] = agent_class(**init_params) if init_params else agent_class()
                logger.info(f"Successfully loaded agent '{agent_name}' from '{module_path}'.")

            except ImportError as e:
                logger.error(f"Failed to import module '{module_name}'. Error: {e}")
            except AttributeError as e:
                logger.error(f"Attribute error loading '{agent_name}'. Class may not match filename. Error: {e}")
            except TypeError as e:
                logger.error(f"Initialization error for agent '{agent_name}': {e}")
            except Exception as e:
                logger.exception(f"Unexpected error loading agent '{agent_name}': {e}")
        
        if agents:
            logger.info(f"Total loaded agents: {len(agents)} - {list(agents.keys())}")
        else:
            logger.warning("No agents were loaded. Verify the agents directory and structure.")
        
        return agents


    def add_agent(self, agent_name: str, agent_instance: Any):
        """
        Adds a new agent to the dispatcher and logs registration.

        Args:
            agent_name (str): The name of the agent.
            agent_instance (Any): The agent instance.
        """
        self.agents[agent_name] = agent_instance
        logger.info(f"Added new agent '{agent_name}' to AgentDispatcher.")

    def remove_agent(self, agent_name: str):
        """
        Removes an agent from the dispatcher if it exists.

        Args:
            agent_name (str): The name of the agent.
        """
        if agent_name in self.agents:
            del self.agents[agent_name]
            logger.info(f"Removed agent '{agent_name}' from AgentDispatcher.")
        else:
            logger.warning(f"Tried to remove non-existent agent '{agent_name}'.")

    def list_agents(self) -> list:
        """
        Lists all registered agents with their capabilities.

        Returns:
            list: Names of all agents currently available.
        """
        agent_names = list(self.agents.keys())
        logger.info("Listing all registered agents and their capabilities:")
        for name, agent in self.agents.items():
            capabilities = agent.describe_capabilities() if hasattr(agent, 'describe_capabilities') else "No description available."
            logger.info(f"Agent '{name}': {capabilities}")
        return agent_names

    async def run(self):
        """
        Starts the task execution process.
        """
        await self.execute_tasks()

    async def execute_tasks(self):
        """
        Executes tasks from the priority queue asynchronously.
        """
        logger.info("Starting task execution loop.")
        while not self.task_queue.empty():
            priority, task, agent_name, kwargs = await self.task_queue.get()
            agent = self.agents.get(agent_name)
            if agent:
                logger.info(f"Executing queued task '{task}' for agent '{agent_name}' with priority {priority}")
                try:
                    result = await agent.solve_task(task, **kwargs)
                    self.performance_monitor.log_performance(agent_name, task, result)
                    logger.info(f"Queued task '{task}' completed by '{agent_name}' with result: {result}")
                except Exception as e:
                    logger.error(f"Error executing queued task '{task}' for agent '{agent_name}': {e}")
            else:
                logger.error(f"Agent '{agent_name}' not found for queued task '{task}'")

    def shutdown(self):
        """
        Shuts down the dispatcher gracefully.
        """
        logger.info("Shutting down AgentDispatcher.")
        # No need to shut down the executor since we removed ThreadPoolExecutor
        logger.info("AgentDispatcher shut down successfully.")
