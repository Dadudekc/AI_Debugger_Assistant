# -------------------------------------------------------------------
# File Path: C:\Projects\AI_Debugger_Assistant\ai_agent_project\src\agents\core\utilities\agent_base.py
#
# Project: AI_Debugger_Assistant
#
# Description:
# Defines the `AgentBase` abstract class, which serves as a versatile
# foundational layer for agents within the project. This class provides
# essential functionalities including task scheduling, structured logging,
# dynamic error handling, persistent task state tracking, and automated
# retry mechanisms, making it extensible and robust for complex workflows.
#
# Classes:
# - AgentBase: An abstract base class designed for agents, equipping them 
#   with core methods for task scheduling, error handling, logging, task 
#   persistence, and performance tracking.
#
# Usage:
# Agents inheriting from `AgentBase` should implement the `solve_task` method,
# defining their unique task-solving logic. The base class handles logging, 
# scheduling, and persistent state management to ensure task reliability and 
# consistency.
# -------------------------------------------------------------------

import abc
import logging
import json
from typing import Any, Callable, Optional
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import traceback
from sqlalchemy import create_engine, Column, Integer, String, Enum, DateTime, Text
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
import enum
import time

# Database Model Setup
Base = declarative_base()

class TaskState(enum.Enum):
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"
    retrying = "retrying"

class Task(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True)
    type = Column(String, nullable=False)
    status = Column(Enum(TaskState), default=TaskState.pending)
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime)
    result = Column(Text)  # Text to allow for larger outputs
    retry_count = Column(Integer, default=0)

# Database Connection
engine = create_engine('sqlite:///tasks.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

class AgentBase(metaclass=abc.ABCMeta):
    """
    Abstract base class for agents in the AI_Debugger_Assistant project.
    Offers core functionalities for task execution, structured logging, 
    scheduling, error handling, and persistent task state management.
    """

    MAX_RETRIES = 3  # Max retries for task failure

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
        """Logs a message at the specified logging level."""
        self.logger.log(level, message)

    def log_json(self, message: str, data: dict, level=logging.INFO):
        """Logs a structured message with additional data in JSON format."""
        log_entry = {
            "message": message,
            "data": data
        }
        self.logger.log(level, json.dumps(log_entry))

    @abc.abstractmethod
    def solve_task(self, task: str, **kwargs) -> Any:
        """Abstract method for executing the agent's main function."""
        pass

    def log_error(self, error: Exception, context: Optional[dict] = None):
        """Logs an error with traceback and provides user-friendly error information."""
        error_details = {
            "error_message": str(error),
            "traceback": traceback.format_exc(),
            "context": context or {}
        }
        self.log_json("Error encountered", error_details, level=logging.ERROR)

    def handle_task_with_error_handling(self, task_data: dict, fallback: Optional[Callable] = None) -> str:
        """Executes a task with error handling, including retry support and fallback."""
        task_id = self.save_task_state("task_execution", TaskState.pending)
        try:
            result = self._execute_with_retry(task_id, task_data)
            self.update_task_state(task_id, TaskState.completed, result=result)
            return result
        except Exception as e:
            self.log_error(e, {"task_data": task_data})
            self.update_task_state(task_id, TaskState.failed)
            return fallback() if fallback else "An error occurred while processing the task."

    def _execute_with_retry(self, task_id: int, task_data: dict) -> str:
        """
        Executes a task with retry logic, using exponential backoff.
        Retries up to `MAX_RETRIES` if exceptions are raised.
        """
        attempt = 0
        while attempt < self.MAX_RETRIES:
            try:
                self.update_task_state(task_id, TaskState.running)
                result = self.solve_task(**task_data)
                self.logger.info("Task executed successfully.")
                return result
            except Exception as e:
                attempt += 1
                self.log_error(e, {"attempt": attempt})
                self.update_task_state(task_id, TaskState.retrying)
                if attempt < self.MAX_RETRIES:
                    backoff = 2 ** attempt
                    self.logger.info(f"Retrying task in {backoff} seconds (Attempt {attempt}/{self.MAX_RETRIES})")
                    time.sleep(backoff)
                else:
                    raise

    def introduce(self) -> str:
        """Provides a brief introduction of the agent, including name and description."""
        introduction = f"I am {self.name}. {self.description}"
        self.logger.info("Introduction called.")
        return introduction

    def describe_capabilities(self) -> str:
        """Returns a description of the agent's capabilities."""
        capabilities_description = f"{self.name} can execute tasks related to {self.description}."
        self.logger.info("Capabilities described.")
        return capabilities_description

    def schedule_task(self, cron_expression: str, task_callable: Callable, task_data: dict, task_id: Optional[str] = None):
        """Schedules a recurring task based on a cron expression."""
        try:
            cron_trigger = CronTrigger.from_crontab(cron_expression)
            self.scheduler.add_job(task_callable, cron_trigger, kwargs=task_data, id=task_id)
            self.logger.info(f"Scheduled task '{task_id or task_callable.__name__}' with cron expression: {cron_expression}")
        except Exception as e:
            self.log_error(e)
            self.logger.error(f"Failed to schedule task with cron expression: {cron_expression}")

    def update_scheduled_task(self, task_id: str, new_cron_expression: str):
        """Updates an existing scheduled task with a new cron expression."""
        try:
            job = self.scheduler.get_job(task_id)
            if job:
                new_trigger = CronTrigger.from_crontab(new_cron_expression)
                job.reschedule(trigger=new_trigger)
                self.logger.info(f"Updated scheduled task '{task_id}' with new cron expression: {new_cron_expression}")
            else:
                self.logger.warning(f"Task '{task_id}' not found.")
        except Exception as e:
            self.log_error(e, {"task_id": task_id, "new_cron_expression": new_cron_expression})
            self.logger.error(f"Failed to update scheduled task '{task_id}'.")

    def remove_scheduled_task(self, task_id: str):
        """Removes a scheduled task by its task_id."""
        job = self.scheduler.get_job(task_id)
        if job:
            job.remove()
            self.logger.info(f"Removed scheduled task '{task_id}'.")
        else:
            self.logger.warning(f"Task '{task_id}' not found for removal.")

    def save_task_state(self, task_type: str, initial_status: TaskState) -> int:
        """Saves a new task state to the database for fault tolerance."""
        session = Session()
        task = Task(type=task_type, status=initial_status)
        session.add(task)
        session.commit()
        self.logger.info(f"Task '{task_type}' saved with state '{initial_status.name}' and ID {task.id}.")
        return task.id

    def update_task_state(self, task_id: int, new_status: TaskState, result: Optional[str] = None):
        """Updates the status and result of a task in the database."""
        session = Session()
        task = session.query(Task).filter(Task.id == task_id).one()
        task.status = new_status
        if result:
            task.result = result
        task.end_time = datetime.utcnow()
        session.commit()
        self.logger.info(f"Task ID {task_id} updated to status '{new_status.name}' with result: {result}")

    def shutdown(self):
        """Gracefully shuts down the scheduler and database session."""
        self.scheduler.shutdown()
        self.logger.info("Scheduler shut down successfully.")

# -------------------------------------------------------------------
# Example Usage
# -------------------------------------------------------------------
# Demonstrates subclassing, task execution, logging, and scheduling.

if __name__ == "__main__":
    class SampleAgent(AgentBase):
        def solve_task(self, task: str, **kwargs):
            self.log("Performing a sample task.")
            return "Sample task completed successfully."

    # Instantiate an agent with file-based logging
    agent = SampleAgent(name="SampleAgent", description="A test agent for demonstration.", log_to_file=True)
    print(agent.introduce())
    print(agent.solve_task("Test Task"))
    agent.log("This is a test log message.", logging.DEBUG)

    # Schedule a task and set up fallback handling
    agent.schedule_task("*/1 * * * *", agent.handle_task_with_error_handling, {"task": "Sample scheduled task"})

# -------------------------------------------------------------------
# Future Improvements
# -------------------------------------------------------------------
# 1. Dynamic Logger Configurations: Allow more dynamic configurations, such as setting
#    log levels based on the environment.
# 2. Enhanced Error Notifications: Integrate with notification services like Slack or
#    email for error alerts.
# 3. Task Retry Mechanism: Include task retry functionality with exponential backoff.
# 4. Extensible Scheduler Options: Enable more complex scheduling options like intervals
#    and custom triggers.
# 5. Memory and Performance Tracking: Integrate memory and performance tracking,
#    particularly for long-running tasks.
# 6. Persistent Task Management: Add functionality to save and retrieve task state for
#    fault tolerance.
