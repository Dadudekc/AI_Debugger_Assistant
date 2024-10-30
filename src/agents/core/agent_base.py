# -------------------------------------------------------------------
# File Path: C:\Projects\AI_Debugger_Assistant\src\agents\core\agent_base.py
#
# Project: AI_Debugger_Assistant
#
# Description:
# This module defines the foundational `AgentBase` class, an abstract base
# class providing core properties and methods that all AI agents in the 
# AI_Debugger_Assistant project inherit. It standardizes task execution,
# logging, and agent identification, setting up a framework for more 
# specialized agents.
#
# Classes:
# - AgentBase: The foundational class for all agents, defining essential
#              attributes and methods required across agent types.
#
# Usage:
# This module is imported by specialized agents (e.g., debugging, 
# journaling, data-fetching agents) that extend the `AgentBase` class
# to inherit basic functionalities while adding task-specific logic.
#
# -------------------------------------------------------------------

import abc
import logging


class AgentBase(metaclass=abc.ABCMeta):
    """
    Abstract base class for all agents in the AI_Debugger_Assistant project.
    
    Provides:
    - A unified structure for defining different agents by encapsulating
      shared properties (e.g., name, description) and methods (e.g., logging, 
      task execution).
    - Ensures that every agent adheres to a standard interface for performing 
      tasks and introducing itself.

    Attributes:
        name (str): The name of the agent.
        description (str): A short description of the agent's purpose.
    """

    def __init__(self, name: str, description: str):
        """
        Initializes the AgentBase with a name, description, and logging setup.

        Args:
            name (str): The agent's name (e.g., "DebuggerAgent").
            description (str): Brief description of the agent's role.
        """
        self.name = name
        self.description = description
        self.logger = logging.getLogger(self.name)
        self._setup_logger()
        self.logger.info(f"{self.name} initialized with description: {self.description}")

    def _setup_logger(self):
        """Sets up the logging configuration for the agent."""
        if not self.logger.hasHandlers():
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    @abc.abstractmethod
    def perform_task(self, task_data: dict) -> str:
        """
        Abstract method for executing the agent's main function, to be 
        implemented by subclasses.

        Args:
            task_data (dict): Information necessary for the task execution.

        Returns:
            str: Outcome of the task, as implemented by the subclass.
        """
        pass

    def log(self, message: str, level=logging.INFO):
        """
        Logs a message at the specified logging level.

        Args:
            message (str): The message to log.
            level (int): The logging level (default is logging.INFO).
        """
        self.logger.log(level, message)

    def introduce(self) -> str:
        """
        Introduces the agent by providing its name and description.

        Returns:
            str: An introduction string including the agent's name and description.
        """
        introduction = f"I am {self.name}. {self.description}"
        self.logger.info("Introduction called.")
        return introduction


# Example usage and testing for AgentBase (remove after subclassing).
if __name__ == "__main__":
    class SampleAgent(AgentBase):
        def perform_task(self, task_data):
            self.log("Performing a sample task.")
            return "Sample task completed successfully."

    agent = SampleAgent(name="SampleAgent", description="This is a test agent for demonstration.")
    print(agent.introduce())
    print(agent.perform_task({}))
    agent.log("This is a test log message.", logging.DEBUG)


# -------------------------------------------------------------------
# Value-Adding Improvements
# -------------------------------------------------------------------
# 1. **Enhanced Logging**: Expand logging to include structured logging levels
#    and external log storage (e.g., JSON format logs or database) for long-term analysis.
#
# 2. **Task Scheduling**: Integrate task scheduling (e.g., using `APScheduler`)
#    to allow agents to perform tasks autonomously at predefined intervals or based on events.
#
# 3. **Error Handling and Reporting**: Add robust error-handling routines with
#    automated feedback mechanisms. This could involve notifying the user of critical
#    errors, generating detailed error reports, or triggering fallback mechanisms.
#
# -------------------------------------------------------------------
