import abc
import logging
import json
from typing import Any, Callable
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import traceback

class AgentBase(metaclass=abc.ABCMeta):
    """
    Abstract base class for all agents in the AI_Debugger_Assistant project.
    """

    def __init__(self, name: str, description: str, log_to_file: bool = False):
        self.name = name
        self.description = description
        self.logger = logging.getLogger(self.name)
        self._setup_logger(log_to_file)
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()
        self.logger.info(f"{self.name} initialized with description: {self.description}")

    def _setup_logger(self, log_to_file: bool):
        """Sets up the logging configuration for the agent."""
        if not self.logger.hasHandlers():
            handler = logging.StreamHandler() if not log_to_file else logging.FileHandler(f"{self.name}.log")
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def log(self, message: str, level=logging.INFO):
        """
        Logs a message at the specified logging level.

        Args:
            message (str): The message to log.
            level (int): The logging level (default is logging.INFO).
        """
        self.logger.log(level, message)

    def log_json(self, message: str, data: dict, level=logging.INFO):
        """
        Logs a message along with structured data in JSON format.

        Args:
            message (str): The log message.
            data (dict): Additional data to log in JSON format.
            level (int): The logging level.
        """
        log_entry = {
            "message": message,
            "data": data
        }
        self.logger.log(level, json.dumps(log_entry))

    @abc.abstractmethod
    def solve_task(self, task: str, **kwargs) -> Any:
        """
        Abstract method for executing the agent's main function, to be implemented by subclasses.

        Args:
            task (str): The main task description.
            **kwargs: Additional data required for the task.

        Returns:
            Any: Outcome of the task as defined by the subclass.
        """
        pass

    def log_error(self, error: Exception):
        """
        Logs an error with traceback and provides user-friendly error information.

        Args:
            error (Exception): The exception to log.
        """
        error_details = {
            "error_message": str(error),
            "traceback": traceback.format_exc()
        }
        self.log_json("Error encountered", error_details, level=logging.ERROR)

    def handle_task_with_error_handling(self, task_data: dict) -> str:
        """
        Executes a task with error handling, providing fallback on failure.

        Args:
            task_data (dict): Data necessary for task execution.

        Returns:
            str: Outcome of the task or error message.
        """
        try:
            result = self.solve_task(task_data)
            self.logger.info("Task executed successfully.")
            return result
        except Exception as e:
            self.log_error(e)
            fallback_message = "An error occurred while processing the task. Please try again or check the logs."
            self.logger.warning("Fallback mechanism triggered.")
            return fallback_message

    def introduce(self) -> str:
        """
        Introduces the agent by providing its name and description.

        Returns:
            str: An introduction string including the agent's name and description.
        """
        introduction = f"I am {self.name}. {self.description}"
        self.logger.info("Introduction called.")
        return introduction

    def describe_capabilities(self) -> str:
        """
        Describes the capabilities of the agent.

        Returns:
            str: A description of the agent's capabilities.
        """
        capabilities_description = f"{self.name} can execute tasks related to {self.description}."
        self.logger.info("Capabilities described.")
        return capabilities_description

    def schedule_task(self, cron_expression: str, task_callable: Callable, task_data: dict):
        """
        Schedules a recurring task based on a cron expression.

        Args:
            cron_expression (str): A cron expression string defining the task schedule.
            task_callable (Callable): The function to call for the task.
            task_data (dict): Data to pass to the task function.
        """
        try:
            cron_trigger = CronTrigger.from_crontab(cron_expression)
            self.scheduler.add_job(task_callable, cron_trigger, kwargs=task_data)
            self.logger.info(f"Scheduled task with cron expression: {cron_expression}")
        except Exception as e:
            self.log_error(e)
            self.logger.error(f"Failed to schedule task with cron expression: {cron_expression}")
    
    def shutdown(self):
        """
        Shuts down the scheduler gracefully, ensuring all scheduled tasks are stopped.
        """
        self.scheduler.shutdown()
        self.logger.info("Scheduler shut down successfully.")


# Example usage of AgentBase (this part can be removed or modified for actual subclassing)
if __name__ == "__main__":
    class SampleAgent(AgentBase):
        def solve_task(self, task: str, **kwargs):
            self.log("Performing a sample task.")
            return "Sample task completed successfully."

    # Sample usage with logging to file
    agent = SampleAgent(name="SampleAgent", description="This is a test agent for demonstration.", log_to_file=True)
    print(agent.introduce())
    print(agent.solve_task("Test Task"))
    agent.log("This is a test log message.", logging.DEBUG)

    # Example of scheduling a sample task with error handling
    agent.schedule_task("*/1 * * * *", agent.handle_task_with_error_handling, {"task": "Sample scheduled task"})
