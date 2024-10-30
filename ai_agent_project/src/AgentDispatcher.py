# ------------------------
# Enhanced AgentDispatcher Class
# C:\Projects\AI_Debugger_Assistant\ai_agent_project\src\AgentDispatcher.py
# ------------------------

import logging
from queue import PriorityQueue
from typing import Any
from ai_agent_utils import PerformanceMonitor, MemoryManager
from ChainOfThoughtReasoner import ChainOfThoughtReasoner
from AgentPlanner import AgentPlanner
from agent_actor import AgentActor

class AgentDispatcher:
    """
    Dispatches tasks to the appropriate agent, supporting chain-of-thought reasoning.
    """
    
    def __init__(self):
        self.memory_manager = MemoryManager()
        self.performance_monitor = PerformanceMonitor()
        self.chain_of_thought_reasoner = ChainOfThoughtReasoner(self)  # Integrate CoT reasoner
        self.agents = {
            'planner': AgentPlanner(),
            'actor': AgentActor(),
            'ai_agent': AIAgentWithMemory("Jarvis", "HomeAutomation", self.memory_manager, self.performance_monitor, self)
        }
        logger.info("AgentDispatcher initialized with agents: planner, actor, ai_agent.")
    
    def dispatch_task(self, task: str, agent_name: str, use_chain_of_thought: bool = False, **kwargs) -> Any:
        """
        Dispatches a task to the specified agent with an option for chain-of-thought reasoning.

        Args:
            task (str): The task to be executed.
            agent_name (str): The name of the agent to handle the task.
            use_chain_of_thought (bool): Whether to use chain-of-thought reasoning.
            **kwargs: Additional keyword arguments for the agent.

        Returns:
            Any: The result of the agent's task execution.
        """
        if agent_name not in self.agents:
            error_msg = f"Agent '{agent_name}' not found!"
            logger.error(error_msg)
            return error_msg
        
        if use_chain_of_thought:
            logger.info(f"Dispatching task to '{agent_name}' with chain-of-thought reasoning.")
            return self.chain_of_thought_reasoner.solve_task_with_reasoning(task, agent_name)
        else:
            logger.info(f"Dispatching task to agent '{agent_name}': {task}")
            return self.agents[agent_name].solve_task(task, **kwargs)
    
    def execute_tasks(self):
        """
        Executes tasks in the order of priority.
        """
        while not self.task_queue.empty():
            priority, task, agent_name, kwargs = self.task_queue.get()
            agent = self.agents.get(agent_name)
            
            if agent:
                try:
                    logger.info(f"Dispatching task '{task}' to agent '{agent_name}' with priority {priority}")
                    result = agent.solve_task(task, **kwargs)
                    
                    # Track performance if applicable
                    self.performance_monitor.log_performance(agent_name, task, result)
                    logger.info(f"Task '{task}' completed by '{agent_name}' with result: {result}")
                except Exception as e:
                    logger.error(f"Error executing task '{task}' for agent '{agent_name}': {e}")
            else:
                logger.error(f"Agent '{agent_name}' could not be found for task '{task}'")

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

    def list_agents(self):
        """
        Lists all registered agents with their capabilities.
        """
        logger.info("Listing all registered agents and their capabilities:")
        for name, agent in self.agents.items():
            logger.info(f"Agent '{name}': {agent.describe_capabilities()}")

