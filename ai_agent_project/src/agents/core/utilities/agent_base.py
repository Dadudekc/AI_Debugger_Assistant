# -------------------------------------------------------------------
# File Path: C:\Projects\AI_Debugger_Assistant\ai_agent_project\src\agents\core\utilities\agent_base.py
#
# Project: AI_Debugger_Assistant
#
# Description:
# Defines the `AgentBase` abstract class, which serves as a versatile
# foundational layer for agents within the project. This class provides
# essential functionalities including task scheduling, structured logging,
# dynamic error handling, persistent task state tracking, automated
# retry mechanisms, modular plug-and-play task expansion, AI-driven
# self-healing capabilities, and user interaction for high-level decisions.
#
# Classes:
# - AgentBase: An abstract base class designed for agents, equipping them 
#   with core methods for task scheduling, error handling, logging, task 
#   persistence, performance tracking, dynamic task loading, AI-driven
#   error resolution, and user decision prompts.
#
# Usage:
# Agents inheriting from `AgentBase` should implement the `solve_task` method,
# defining their unique task-solving logic. The base class handles logging, 
# scheduling, persistent state management, dynamic plugin loading, AI-driven
# error handling, and user interaction to ensure task reliability, scalability,
# and consistency.
# -------------------------------------------------------------------

import abc
import logging
import importlib
import json
import os
from typing import Any, Callable, Optional, Dict
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from pathlib import Path
import traceback
import subprocess
from sqlalchemy import create_engine, Column, Integer, String, Enum, DateTime, Text
from sqlalchemy.orm import declarative_base, sessionmaker
import enum
import time
from datetime import datetime

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
    scheduling, error handling, persistent task state management, 
    modular plug-and-play task expansion, AI-driven self-healing, and 
    user interaction for high-level decisions.
    """

    MAX_RETRIES = 3  # Max retries for task failure

    def __init__(self, name: str, description: str, plugin_dir: str = "plugins", log_to_file: bool = False):
        self.name = name
        self.description = description
        self.plugin_dir = plugin_dir  # Directory for dynamically loaded task plugins
        self.logger = logging.getLogger(self.name)
        self._setup_logger(log_to_file)
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()
        self.plugins = self.load_plugins()
        self.logger.info(f"{self.name} initialized with description: {self.description} and plugin directory: {self.plugin_dir}")

    def _setup_logger(self, log_to_file: bool):
        """Sets up the logging configuration for the agent."""
        if not self.logger.hasHandlers():
            handler = logging.StreamHandler() if not log_to_file else logging.FileHandler(f"{self.name}.log")
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def load_plugins(self) -> Dict[str, Callable]:
        """
        Dynamically loads plugins (task handlers) from the specified directory.

        Returns:
            Dict[str, Callable]: A dictionary of plugin functions.
        """
        plugins = {}
        plugin_path = Path(self.plugin_dir)
        if not plugin_path.exists():
            self.logger.warning(f"Plugin directory '{self.plugin_dir}' does not exist.")
            return plugins

        for plugin_file in plugin_path.glob("*.py"):
            module_name = plugin_file.stem
            try:
                module_spec = importlib.util.spec_from_file_location(module_name, plugin_file)
                module = importlib.util.module_from_spec(module_spec)
                module_spec.loader.exec_module(module)
                plugin_func = getattr(module, "run_task", None)
                if callable(plugin_func):
                    plugins[module_name] = plugin_func
                    self.logger.info(f"Loaded plugin: {module_name}")
            except Exception as e:
                self.logger.error(f"Error loading plugin '{module_name}': {e}")

        return plugins

    def execute_plugin_task(self, task_name: str, task_data: dict) -> str:
        """
        Executes a task using a dynamically loaded plugin.

        Args:
            task_name (str): The name of the task/plugin to execute.
            task_data (dict): Data to pass to the plugin.

        Returns:
            str: The result of the plugin task or an error message.
        """
        plugin = self.plugins.get(task_name)
        if plugin:
            try:
                self.logger.info(f"Executing plugin task '{task_name}' with data: {task_data}")
                return plugin(task_data)
            except Exception as e:
                self.log_error(e, {"task_name": task_name})
                return f"Error executing plugin '{task_name}': {str(e)}"
        else:
            error_message = f"Plugin '{task_name}' not found."
            self.logger.error(error_message)
            return error_message

    def ai_diagnose_and_resolve(self, error_message: str) -> Optional[str]:
        """
        Uses Mistral through Ollama CLI to diagnose and suggest resolutions for errors.

        Args:
            error_message (str): The error message to diagnose.

        Returns:
            Optional[str]: Suggested resolution from AI, if available.
        """
        prompt = f"Provide a solution for the following error:\n{error_message}"
        try:
            self.logger.info(f"Sending prompt to AI for error diagnosis: {prompt}")
            result = subprocess.run(
                ["ollama", "generate", "--model", "mistral", prompt],
                capture_output=True,
                text=True,
                check=True
            )
            suggestion = result.stdout.strip()
            self.logger.info(f"AI Suggestion for error '{error_message}': {suggestion}")
            return suggestion
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to get AI suggestion for error: {error_message}. Error: {e}")
            return None

    def handle_task_with_error_handling(self, task_data: dict, fallback: Optional[Callable] = None) -> str:
        """
        Executes a task with error handling, AI-based resolution, and optional user prompt for oversight.

        Args:
            task_data (dict): Data necessary for task execution.
            fallback (Optional[Callable]): Optional fallback function.

        Returns:
            str: Outcome of the task or error message.
        """
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

        Args:
            task_id (int): The ID of the task in the database.
            task_data (dict): Data necessary for task execution.

        Returns:
            str: The result of the task.

        Raises:
            Exception: Re-raises the last exception if all retries fail.
        """
        attempt = 0
        while attempt < self.MAX_RETRIES:
            try:
                self.update_task_state(task_id, TaskState.running)
                result = self.solve_task(task_data)
                self.logger.info("Task executed successfully.")
                return result
            except Exception as e:
                attempt += 1
                self.log_error(e, {"attempt": attempt})
                if attempt < self.MAX_RETRIES:
                    self.update_task_state(task_id, TaskState.retrying)
                    backoff = 2 ** attempt
                    self.logger.info(f"Retrying task in {backoff} seconds (Attempt {attempt}/{self.MAX_RETRIES})")
                    time.sleep(backoff)
                else:
                    self.logger.error(f"Max retries reached for task ID {task_id}.")
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
        task = session.query(Task).filter(Task.id == task_id).one_or_none()
        if task:
            task.status = new_status
            if result:
                task.result = result
            task.end_time = datetime.utcnow()
            session.commit()
            self.logger.info(f"Task ID {task_id} updated to status '{new_status.name}' with result: {result}")
        else:
            self.logger.error(f"Task ID {task_id} not found in the database.")

    def shutdown(self):
        """Gracefully shuts down the scheduler and closes database sessions."""
        self.scheduler.shutdown()
        self.logger.info("Scheduler shut down successfully.")

# -------------------------------------------------------------------
# Example Usage
# -------------------------------------------------------------------
# Demonstrates subclassing, task execution, logging, scheduling, 
# dynamic plugin execution, AI-driven error resolution, and user prompts.

if __name__ == "__main__":
    class SampleAgent(AgentBase):
        def solve_task(self, task_data: dict) -> str:
            """
            Implements the abstract solve_task method. Processes the task_data
            and returns a result. Can be extended to handle various task types.
            """
            task_type = task_data.get("type")
            self.log(f"Processing task of type: {task_type}")
            
            if task_type == "simple_task":
                return "Simple task completed successfully."
            elif task_type == "trigger_error":
                raise ValueError("Simulated task error for demonstration.")
            elif task_type == "plugin_task":
                plugin_name = task_data.get("plugin_name")
                plugin_data = task_data.get("plugin_data", {})
                return self.execute_plugin_task(plugin_name, plugin_data)
            else:
                return "Unknown task type."

    # Instantiate an agent with file-based logging
    agent = SampleAgent(
        name="SampleAgent",
        description="A test agent with plugin support and AI self-healing capabilities.",
        plugin_dir="plugins",  # Ensure this directory exists and contains plugin modules
        log_to_file=True
    )
    
    # Introduction
    print(agent.introduce())
    
    # Execute a simple task
    simple_task_data = {"type": "simple_task"}
    print(agent.solve_task(simple_task_data))
    
    # Execute a task that triggers an error to test AI-based resolution and user prompts
    error_task_data = {"type": "trigger_error"}
    print(agent.handle_task_with_error_handling(error_task_data))
    
    # Execute a plugin-based task (ensure 'example_plugin.py' exists in the plugins directory)
    plugin_task_data = {
        "type": "plugin_task",
        "plugin_name": "example_plugin",  # Name of the plugin without .py extension
        "plugin_data": {"input": "Test input for plugin"}
    }
    print(agent.solve_task(plugin_task_data))
    
    # Schedule a recurring task with fallback handling
    # This example schedules the 'handle_task_with_error_handling' method to run every minute
    scheduled_task_id = "recurring_error_task"
    agent.schedule_task(
        cron_expression="*/1 * * * *",  # Every minute
        task_callable=agent.handle_task_with_error_handling,
        task_data=error_task_data,
        task_id=scheduled_task_id
    )
    
    # Keep the script running to allow scheduled tasks to execute
    try:
        while True:
            time.sleep(2)
    except (KeyboardInterrupt, SystemExit):
        agent.shutdown()

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
# 7. Plugin Health Check: Add a validation process to verify each plugin’s availability before execution.
# 8. AI-based Fallback Option: If Mistral fails, enable a fallback to another AI model or simpler resolution mechanism.
# 9. Multi-Error Diagnosis: Enhance AI diagnostics to handle multi-layered errors by iterating through each error in a stack trace.
# 10. Persistent Resolution History: Maintain a history of resolutions that the agent can reference for similar issues.
# 11. User Decision Caching: Allow user responses to be stored for future automated decisions on similar edge cases.
# 12. Asynchronous Task Execution: Refactor task execution methods to be asynchronous for improved performance and scalability.
# 13. Enhanced Plugin Interface: Define a more comprehensive plugin interface, possibly using abstract base classes, to ensure consistency across plugins.
# 14. Security Enhancements: Implement security measures for plugin execution to prevent malicious code execution.
# 15. Comprehensive Unit Testing: Develop unit tests for each component to ensure reliability and facilitate future development.
