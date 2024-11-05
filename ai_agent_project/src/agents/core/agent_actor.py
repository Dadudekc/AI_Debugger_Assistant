import subprocess
import logging
from typing import List, Dict, Any, Optional
from utilities.ai_agent_utils import PerformanceMonitor, MemoryManager

logger = logging.getLogger(__name__)

class AgentActor:
    """
    Executes tasks using the tools provided in the ToolServer.
    """
    def __init__(self, tool_server, memory_manager, performance_monitor):
        self.tool_server = tool_server
        self.memory_manager = memory_manager
        self.performance_monitor = performance_monitor
        logger.info("AgentActor initialized without Docker dependency.")

    def solve_task(self, task: str) -> str:
        """
        Solves the task, distinguishing between shell commands and Python code.
        """
        logger.info(f"AgentActor received task: {task}")

        if task.startswith("python:"):
            # Remove 'python:' prefix and execute using PythonNotebook
            python_code = task[len("python:"):].strip()
            result = self.tool_server.python_notebook.execute_code(python_code)
            logger.debug(f"Executed Python task with result: {result}")
            return result
        else:
            # Execute as a shell command
            result = self.tool_server.shell.execute_command(task)
            logger.debug(f"Executed shell task with result: {result}")
            return result


    def utilize_tool(self, tool_name: str, operation: str, parameters: Dict[str, Any]) -> Any:
        """
        Executes a specified operation on a tool managed by ToolServer.

        Args:
            tool_name (str): The name of the tool.
            operation (str): The operation to perform.
            parameters (Dict[str, Any]): Parameters for the operation.

        Returns:
            Any: The result of the tool operation.
        """
        tool = getattr(self.tool_server, tool_name, None)
        if tool:
            tool_method = getattr(tool, operation, None)
            if tool_method:
                return tool_method(**parameters)
            else:
                logger.error(f"Operation '{operation}' not found in tool '{tool_name}'.")
                return f"Error: Operation '{operation}' not found in tool '{tool_name}'."
        else:
            logger.error(f"Tool '{tool_name}' not found in ToolServer.")
            return f"Error: Tool '{tool_name}' not found in ToolServer."
