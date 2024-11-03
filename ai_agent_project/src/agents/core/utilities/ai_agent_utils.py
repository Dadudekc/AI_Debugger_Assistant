# ai_agent_utils.py

import math
import random
import re
import numpy as np
import pandas as pd
from statistics import mean, median, stdev
import json
import os
import logging
from datetime import datetime
import docker
from typing import Dict, Any, Optional, List

import subprocess
import shlex
import platform
import logging

# Initialize the logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Set to DEBUG for detailed logs

# Create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# Create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Add formatter to ch
ch.setFormatter(formatter)

# Add ch to logger
if not logger.handlers:
    logger.addHandler(ch)

# ------------------------
# PerformanceMonitor Class
# ------------------------

import math
import datetime
import random
import json
import re
import numpy as np
import pandas as pd
from statistics import mean, median, stdev
from typing import Any, Dict
import logging

# Setup logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

class PerformanceMonitor:
    """
    Tracks and analyzes the performance of agents.
    Logs successes and failures to identify areas for improvement.
    """
    def __init__(self, performance_file='performance.json'):
        self.performance_file = performance_file
        if not os.path.exists(self.performance_file):
            with open(self.performance_file, 'w') as f:
                json.dump({}, f)
        logger.info(f"PerformanceMonitor initialized with performance file: {self.performance_file}")

    def log_performance(self, agent_name: str, task: str, success: bool, details: str = ""):
        """
        Logs the performance of an agent on a specific task.
        """
        try:
            with open(self.performance_file, 'r') as f:
                data = json.load(f)
            if agent_name not in data:
                data[agent_name] = []
            data[agent_name].append({
                'timestamp': datetime.datetime.now().isoformat(),  # Corrected datetime usage
                'task': task,
                'success': success,
                'details': details
            })
            with open(self.performance_file, 'w') as f:
                json.dump(data, f, indent=4)
            logger.debug(f"Performance logged for agent '{agent_name}': {'Success' if success else 'Failure'} - {task}")
        except Exception as e:
            logger.error(f"Error logging performance: {str(e)}")

# ------------------------
# MemoryManager Class
# ------------------------

class MemoryManager:
    """
    Manages memory storage and retrieval for AI interactions.
    Stores conversations in a JSON file.
    """
    def __init__(self, memory_file='memory.json'):
        self.memory_file = memory_file
        self._initialize_memory_file()

    def _initialize_memory_file(self):
        """
        Initializes the memory file if it does not exist.
        """
        if not os.path.exists(self.memory_file):
            with open(self.memory_file, 'w') as f:
                json.dump({}, f)
        logger.info(f"MemoryManager initialized with memory file: {self.memory_file}")

    def save_memory(self, project_name: str, user_input: str, ai_response: str):
        """
        Saves the user input and AI response to memory.
        """
        try:
            data = self._load_memory_data()
            if project_name not in data:
                data[project_name] = []
            data[project_name].append({
                'timestamp': datetime.now().isoformat(),
                'user_input': user_input,
                'ai_response': ai_response
            })
            self._save_memory_data(data)
            logger.debug(f"Memory saved for project '{project_name}'.")
        except Exception as e:
            logger.error(f"Error saving memory: {str(e)}")

    def retrieve_memory(self, project_name: str, limit: int = 5) -> str:
        """
        Retrieves the latest interactions from memory.
        """
        try:
            data = self._load_memory_data()
            interactions = data.get(project_name, [])[-limit:]
            memory_context = "\n".join(
                f"User: {interaction['user_input']}\nAI: {interaction['ai_response']}"
                for interaction in interactions
            )
            logger.debug(f"Memory retrieved for project '{project_name}': {memory_context}")
            return memory_context
        except Exception as e:
            logger.error(f"Error retrieving memory: {str(e)}")
            return ""

    def _load_memory_data(self) -> Dict:
        """
        Loads memory data from the JSON file.
        """
        with open(self.memory_file, 'r') as f:
            return json.load(f)

    def _save_memory_data(self, data: Dict):
        """
        Saves memory data to the JSON file.
        """
        with open(self.memory_file, 'w') as f:
            json.dump(data, f, indent=4)

# ------------------------
# PythonNotebook Class
# ------------------------


class PythonNotebook:
    """
    Executes Python code snippets within a restricted environment.
    Offers sandboxed code execution to enhance security.
    """
    def __init__(self):
        # Safe built-ins
        self.safe_builtins = {
            'abs': abs,
            'min': min,
            'max': max,
            'sum': sum,
            'len': len,
            'map': map,
            'filter': filter,
            'print': print,
            'mean': mean,
            'median': median,
            'stdev': stdev,
            'sorted': sorted,
            'list': list,
            'dict': dict,
            'set': set,
            'tuple': tuple,
            'range': range,
            '__import__': __import__,
        }
        # Whitelisted modules
        self.allowed_modules = {
            'math': math,
            'datetime': datetime,
            'random': random,
            'json': json,
            're': re,
            'np': np,
            'pd': pd,
        }
        # Contextual storage for maintaining state across executions
        self.state = {}

    def execute_code(self, code: str) -> Any:
        """
        Executes Python code safely within a restricted environment.
        """
        exec_globals = {'__builtins__': self.safe_builtins, **self.allowed_modules}
        exec_locals = self.state

        # Inject loop limit code for safety
        code_with_loop_limit = self._apply_loop_limit(code)

        try:
            exec(code_with_loop_limit, exec_globals, exec_locals)
            return exec_locals  # Return updated state
        except SyntaxError as e:
            error_message = f"Syntax Error: {str(e)}"
            logger.error(error_message)
            return error_message
        except RuntimeError as e:
            error_message = f"Runtime Error: {str(e)}"
            logger.error(error_message)
            return error_message
        except Exception as e:
            error_message = f"Error executing code: {str(e)}"
            logger.error(error_message)
            return error_message

    def _apply_loop_limit(self, code: str) -> str:
        """
        Wraps loops in the code with an iteration limit to prevent infinite loops.
        """
        loop_limit_code = """
_loop_counter = 0
_max_iterations = 1000  # Set a reasonable maximum iteration limit
def _check_loop():
    global _loop_counter
    _loop_counter += 1
    if _loop_counter > _max_iterations:
        raise RuntimeError("Infinite loop detected or too many iterations.")
"""
        # Replace while and for loops with loop limit check
        modified_code = code.replace("while ", "while _check_loop() and ")
        modified_code = modified_code.replace("for ", "for _check_loop() and ")
        return loop_limit_code + "\n" + modified_code

    def set_state(self, key: str, value: Any):
        """Sets a value in the notebook's state."""
        self.state[key] = value

    def get_state(self, key: str) -> Any:
        """Gets a value from the notebook's state."""
        return self.state.get(key, None)

    def reset_state(self):
        """Resets the notebook's state."""
        self.state.clear()


# ------------------------
# Shell Class
# ------------------------

class Shell:
    """
    Executes shell commands directly on the host system.
    """
    def execute_command(self, command: str) -> str:
        """
        Executes a shell command.
        """
        try:
            logger.info(f"Executing command: {command}")

            # Adjust for Windows OS by prefixing with 'cmd /c' for shell commands
            if platform.system() == "Windows":
                command = f"cmd /c {command}"

            result = subprocess.run(
                shlex.split(command),
                capture_output=True,
                text=True,
                shell=True if platform.system() == "Windows" else False
            )
            output = result.stdout if result.returncode == 0 else result.stderr
            logger.debug(f"Command output: {output}")
            return output

        except FileNotFoundError:
            error_msg = f"Command not found: {command}"
            logger.error(error_msg)
            return error_msg
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(error_msg)
            return error_msg

# ------------------------
# ToolServer Class
# ------------------------

class ToolServer:
    """
    A centralized server to manage various tools like shell commands and code execution.
    """
    def __init__(self, shell: Shell = None, python_notebook: PythonNotebook = None, 
                 image_name: str = "your_sandboxed_image_name", dockerfile_path: str = "./path_to_dockerfile_directory/"):
        # Initialize shell and python_notebook with defaults if none provided
        self.shell = shell if shell else Shell(image_name, dockerfile_path)
        self.python_notebook = python_notebook if python_notebook else PythonNotebook()
        logger.info("ToolServer initialized with all tools.")

    def execute_command(self, command: str) -> str:
        """
        Executes a shell command using the shell tool.
        """
        return self.shell.execute(command)

    def execute_code(self, code: str) -> str:
        """
        Executes Python code using the Python notebook tool.
        """
        return self.python_notebook.execute_code(code)


# Example usage
notebook = PythonNotebook()
notebook.set_state('data', [1, 2, 3, 4, 5])
print("Initial state:", notebook.state)
print("Executing sum:", notebook.execute_code("result = sum(data)"))
print("State after execution:", notebook.state)
notebook.reset_state()
print("State after reset:", notebook.state)