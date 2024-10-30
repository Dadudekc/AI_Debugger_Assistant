# -------------------------------------------------------------------
# File Path: C:\Projects\AI_Debugger_Assistant\src\agents\tasks\debugger_agent.py
#
# Project: AI_Debugger_Assistant
#
# Description:
# This file defines the `DebuggerAgent` class, an agent specializing in 
# detecting and resolving syntax, runtime, and logical errors in code. 
# It leverages AI-driven insights to identify and fix common coding issues, 
# particularly useful in development and code review scenarios. 
#
# Classes:
# - DebuggerAgent: Extends `AgentBase` to provide task-specific methods 
#   for error detection and resolution, integrating with diagnostic tools.
#
# Usage:
# This module is instantiated and managed by the core agent dispatcher
# in the AI_Debugger_Assistant project.
# -------------------------------------------------------------------

import subprocess
import logging
from src.agents.core.agent_base import AgentBase  # Ensure the correct import path based on project structure

class DebuggerAgent(AgentBase):
    """
    An agent specialized in debugging code by detecting syntax, runtime, 
    and logical errors. Uses both internal methods and external tools to 
    identify issues in code snippets.
    
    Attributes:
        name (str): The name of the agent.
        description (str): A brief description of the agent's purpose.
    """

    def __init__(self, name="DebuggerAgent", description="Agent for code debugging and error resolution"):
        """
        Initializes the DebuggerAgent with default parameters.
        
        Args:
            name (str): The agent's name.
            description (str): A short description of the agent's role.
        """
        super().__init__(name, description)
        self.logger.info(f"{self.name} initialized with debugging capabilities.")

    def perform_task(self, task_data):
        """
        Perform debugging based on the provided code and detect errors.
        
        Args:
            task_data (dict): Contains code and other parameters for debugging.

        Returns:
            str: Summary of detected issues or success message.
        """
        code = task_data.get("code", "")
        syntax_errors = self.detect_syntax_errors(code)
        runtime_errors = self.detect_runtime_errors(code)
        logic_errors = self.detect_logic_errors(code)

        result_summary = {
            "syntax_errors": syntax_errors,
            "runtime_errors": runtime_errors,
            "logic_errors": logic_errors
        }

        return result_summary

    def detect_syntax_errors(self, code: str) -> str:
        """
        Checks the provided code for syntax errors.

        Args:
            code (str): The code snippet to check.

        Returns:
            str: Syntax error details or "No syntax errors detected."
        """
        try:
            compile(code, "<string>", "exec")
            self.logger.info("No syntax errors detected.")
            return "No syntax errors detected."
        except SyntaxError as e:
            error_message = f"Syntax Error: {e.text.strip()} (Line {e.lineno})"
            self.logger.error(error_message)
            return error_message

    def detect_runtime_errors(self, code: str) -> str:
        """
        Executes the code in a controlled environment to detect runtime errors.

        Args:
            code (str): The code snippet to execute.

        Returns:
            str: Runtime error details or "No runtime errors detected."
        """
        try:
            exec(code)
            self.logger.info("No runtime errors detected.")
            return "No runtime errors detected."
        except Exception as e:
            error_message = f"Runtime Error: {str(e)}"
            self.logger.error(error_message)
            return error_message

    def detect_logic_errors(self, code: str) -> str:
        """
        Uses an external static analysis tool (e.g., pylint) to detect 
        logical errors in the code.

        Args:
            code (str): The code snippet to analyze.

        Returns:
            str: Logic error details or "No logic errors detected."
        """
        # Write code to a temp file for analysis
        temp_file_path = "temp_code.py"
        with open(temp_file_path, "w") as temp_file:
            temp_file.write(code)

        try:
            result = subprocess.run(
                ["pylint", temp_file_path],
                capture_output=True,
                text=True
            )
            self.logger.info("Logic errors detected using pylint.")
            return result.stdout if result.returncode != 0 else "No logic errors detected."
        except Exception as e:
            error_message = f"Error during logic error detection: {str(e)}"
            self.logger.error(error_message)
            return error_message
        finally:
            # Clean up the temporary file
            import os
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)

    def suggest_fixes(self, error_summary: dict) -> dict:
        """
        Suggests potential fixes based on detected errors.

        Args:
            error_summary (dict): A dictionary containing detected errors.

        Returns:
            dict: Suggested fixes for each detected error type.
        """
        fixes = {}
        for error_type, error_message in error_summary.items():
            if "syntax" in error_type:
                fixes[error_type] = "Check the syntax, especially missing colons or parentheses."
            elif "runtime" in error_type:
                fixes[error_type] = "Verify variable definitions and ensure proper data handling."
            elif "logic" in error_type:
                fixes[error_type] = "Review code logic or try running pylint for detailed feedback."
            else:
                fixes[error_type] = "No suggestions available."
        self.logger.info("Generated fix suggestions for errors.")
        return fixes

# Example usage (testing purposes)
if __name__ == "__main__":
    debugger = DebuggerAgent()
    sample_code = "for i in range(10)\n    print(i)"  # Sample code with a syntax error
    error_report = debugger.perform_task({"code": sample_code})
    print("Error Report:", error_report)
    print("Suggested Fixes:", debugger.suggest_fixes(error_report))


# -------------------------------------------------------------------
# Value-Adding Improvements
# -------------------------------------------------------------------
# 1. **Automated Fixes**: Implement AI-driven or rule-based methods to 
#    automatically correct minor syntax or runtime issues, streamlining 
#    debugging by making preliminary adjustments before alerting the user.
#
# 2. **Enhanced Error Reporting**: Add functionality to generate and export 
#    error logs and reports in user-friendly formats (e.g., JSON or HTML) 
#    for in-depth analysis and tracking over time.
#
# 3. **Learning-Based Debugging**: Integrate a learning mechanism where 
#    the agent remembers frequent errors and past fixes, enhancing its 
#    suggestion quality for recurring issues.
# -------------------------------------------------------------------
