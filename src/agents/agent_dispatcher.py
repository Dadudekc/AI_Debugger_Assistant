# -------------------------------------------------------------------
# File Path: C:\Projects\AI_Debugger_Assistant\src\agents\agent_dispatcher.py
#
# Project: AI_Debugger_Assistant
#
# Description:
# This file defines the `AgentDispatcher` class, responsible for managing 
# and dispatching tasks to the appropriate agent within the AI_Debugger_Assistant
# project. It acts as a centralized coordinator for task distribution, utilizing 
# specific agent instances based on task requirements.
#
# Classes:
# - AgentDispatcher: The main dispatcher class that selects and assigns tasks 
#   to agents based on keywords or task type.
#
# Usage:
# Instantiated by the main application to delegate incoming tasks to the 
# relevant agents (e.g., JournalAgent, DebuggerAgent, etc.).
# -------------------------------------------------------------------

import logging
from src.agents.tasks.journal_agent import JournalAgent
from src.agents.tasks.debugger_agent import DebuggerAgent
from src.agents.tasks.custom_agent import CustomAgent  # Placeholder for additional agents

class AgentDispatcher:
    """
    Central dispatcher for managing and assigning tasks to specialized agents.
    
    Attributes:
        agents (dict): Dictionary of initialized agents, accessible by name.
    """

    def __init__(self):
        """
        Initializes the AgentDispatcher, sets up available agents, 
        and configures the task assignment.
        """
        self.logger = logging.getLogger(__name__)
        self.agents = {
            "journal": JournalAgent(),
            "debugger": DebuggerAgent(),
            # Add other agents here as needed
        }
        self.logger.info("AgentDispatcher initialized with available agents.")

    def add_agent(self, agent_name: str, agent_instance):
        """
        Adds a new agent to the dispatcher.
        
        Args:
            agent_name (str): The name to reference the agent.
            agent_instance (object): The agent instance to add.
        """
        self.agents[agent_name] = agent_instance
        self.logger.info(f"Added new agent '{agent_name}' to dispatcher.")

    def dispatch_task(self, task_description: str, task_data=None) -> str:
        """
        Assigns a task to the appropriate agent based on task description or keyword.

        Args:
            task_description (str): Description or keyword indicating the task type.
            task_data (any): Additional data required by the agent to execute the task.

        Returns:
            str: Result or response from the agent handling the task.
        """
        self.logger.info(f"Dispatching task: '{task_description}'")

        # Identify the appropriate agent by task keyword
        agent_name = self.identify_agent(task_description)
        
        if agent_name in self.agents:
            agent = self.agents[agent_name]
            self.logger.info(f"Assigned '{task_description}' to agent '{agent_name}'")
            return agent.perform_task(task_data)
        else:
            error_msg = f"No agent found for task '{task_description}'"
            self.logger.error(error_msg)
            return error_msg

    def identify_agent(self, task_description: str) -> str:
        """
        Determines the appropriate agent to handle a given task based on keywords.

        Args:
            task_description (str): Description of the task.

        Returns:
            str: The name of the agent responsible for the task.
        """
        # Simple keyword matching for agent selection
        task_description = task_description.lower()
        if "journal" in task_description:
            return "journal"
        elif "debug" in task_description:
            return "debugger"
        # Extendable: Add more conditions for different agent keywords
        else:
            self.logger.warning(f"No matching agent for task '{task_description}'")
            return None

    def list_available_agents(self) -> list:
        """
        Lists all available agents within the dispatcher.

        Returns:
            list: Names of all agents currently available.
        """
        agent_names = list(self.agents.keys())
        self.logger.info(f"Available agents: {agent_names}")
        return agent_names


# Example usage (testing purposes)
if __name__ == "__main__":
    dispatcher = AgentDispatcher()
    dispatcher.add_agent("custom", CustomAgent())  # Add a custom agent for example purposes
    print(dispatcher.list_available_agents())
    result = dispatcher.dispatch_task("debugging", {"error": "Syntax Error"})
    print("Dispatch Result:", result)


# -------------------------------------------------------------------
# Value-Adding Improvements
# -------------------------------------------------------------------
# 1. **Intelligent Agent Selection**: Implement NLP or ML-based analysis
#    for more accurate task-agent matching, beyond simple keyword matching.
#
# 2. **Agent Prioritization**: Introduce a priority mechanism where agents 
#    are chosen based on task complexity, urgency, or agent availability.
#
# 3. **Dynamic Agent Loading**: Add support for dynamically loading agents 
#    from external modules to accommodate new functionalities without 
#    requiring code changes within the dispatcher.
# -------------------------------------------------------------------
