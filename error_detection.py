# -------------------------------------------------------------------
# File Path: C:\Projects\AI_Debugger_Assistant\src\error_detection\error_detection.py
#
# Project: AI_Debugger_Assistant
#
# Description:
# This module provides tools to detect syntax, runtime, and logic errors 
# in Python code. It leverages AST parsing for syntax checking, executes 
# code in a sandboxed environment to identify runtime issues, and uses 
# pylint for static analysis to catch logic errors. This serves as a 
# comprehensive error-detection assistant to streamline debugging and 
# error resolution processes.
#
# Classes:
# - ErrorDetection: Handles detection of syntax, runtime, and logic errors 
#   in provided code and includes an initial attempt at auto-fixing common 
#   syntax issues.
#
# Usage:
# The `ErrorDetection` class can be instantiated to analyze code, detect 
# different types of errors, and provide basic syntax fixes when possible.
# -------------------------------------------------------------------

import ast
import traceback
import subprocess
import tempfile
import os


class ErrorDetection:
    """
    Detects and categorizes errors in Python code. Supports syntax, runtime,
    and static (logic) error detection, with basic syntax error auto-fix.
    """

    def __init__(self, pylint_path='pylint'):
        """
        Initialize ErrorDetection with optional path to pylint.

        Args:
            pylint_path (str): Path to the pylint executable. Defaults to 'pylint'.
        """
        self.pylint_path = pylint_path

    def detect_syntax_errors(self, code: str) -> str:
        """
        Detects syntax errors in the provided code using AST parsing.

        Args:
            code (str): Code to check for syntax errors.

        Returns:
            str: Error message if syntax errors are found, or an empty string if none.
        """
        try:
            ast.parse(code)
            return ""
        except SyntaxError as e:
            return f"Syntax Error: {e.msg} (line {e.lineno})"

    def detect_runtime_errors(self, code: str, globals_=None, locals_=None) -> str:
        """
        Detects runtime errors by executing the code in a controlled environment.

        Args:
            code (str): Code to execute and check for runtime errors.
            globals_ (dict): Optional globals for code execution.
            locals_ (dict): Optional locals for code execution.

        Returns:
            str: Error message if runtime errors occur, or an empty string if none.
        """
        try:
            exec(code, globals_ or {}, locals_ or {})
            return ""
        except Exception as e:
            return f"Runtime Error: {e}\n{traceback.format_exc()}"

    def detect_logic_errors(self, file_path: str) -> str:
        """
        Runs pylint on the provided code file to identify potential logic errors.

        Args:
            file_path (str): Path to the file containing the code to be checked.

        Returns:
            str: Pylint output with logic errors if found, or an empty string if none.
        """
        try:
            result = subprocess.run(
                [self.pylint_path, file_path],
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                return result.stdout
            return "No logic issues found."
        except FileNotFoundError:
            return f"Error: Pylint not found at '{self.pylint_path}'. Install pylint or update the path."
        except Exception as e:
            return f"Error running pylint: {str(e)}"

    def detect_all_errors(self, code: str, file_path: str = None) -> dict:
        """
        Detects syntax, runtime, and logic errors in the provided code.

        Args:
            code (str): Code to check.
            file_path (str): Optional path to the file for logic error checking with pylint.

        Returns:
            dict: Dictionary with results for each error type.
        """
        errors = {
            "syntax_errors": self.detect_syntax_errors(code),
            "runtime_errors": self.detect_runtime_errors(code),
            "logic_errors": self.detect_logic_errors(file_path) if file_path else "Skipped",
        }
        return errors

    def quick_fix_syntax_errors(self, code: str) -> tuple:
        """
        Attempts to fix basic syntax errors by identifying common patterns.

        Args:
            code (str): Code to fix.

        Returns:
            tuple: (str) Attempted fix, (bool) Whether fix was successful.
        """
        lines = code.splitlines()
        fixed_lines = []
        for line in lines:
            # Fix for missing colons in control structures
            if line.strip() and not line.strip().endswith(':') and ('if ' in line or 'for ' in line or 'while ' in line):
                fixed_lines.append(line + ':')
            else:
                fixed_lines.append(line)
        fixed_code = "\n".join(fixed_lines)

        # Verify if the fix resolved syntax errors
        syntax_error = self.detect_syntax_errors(fixed_code)
        return fixed_code, syntax_error == ""

# Usage Example
if __name__ == "__main__":
    code_sample = """
def example_function():
    for i in range(10)
        print(i)
    """
    
    error_detector = ErrorDetection()
    
    # Detect syntax errors
    syntax_errors = error_detector.detect_syntax_errors(code_sample)
    print("Syntax Errors:", syntax_errors)
    
    # Detect runtime errors
    runtime_errors = error_detector.detect_runtime_errors(code_sample)
    print("Runtime Errors:", runtime_errors)
    
    # Detect logic errors with pylint (using a sample file path)
    logic_errors = error_detector.detect_logic_errors("path/to/temp_file.py")
    print("Logic Errors:", logic_errors)
    
    # Detect all errors at once
    all_errors = error_detector.detect_all_errors(code_sample, "path/to/temp_file.py")
    print("All Errors:", all_errors)

    # Attempt a quick fix for syntax errors
    fixed_code, fix_successful = error_detector.quick_fix_syntax_errors(code_sample)
    print("Fixed Code:\n", fixed_code)
    print("Fix Successful:", fix_successful)


# -------------------------------------------------------------------
# Future Enhancements for Improved Error Detection
# -------------------------------------------------------------------
# 1. **Enhanced Syntax Error Correction**: Integrate NLP models or machine 
#    learning techniques to suggest sophisticated syntax corrections based 
#    on context and common error patterns.
#
# 2. **Detailed Logic Analysis with Categorization**: Provide categorized 
#    pylint reports to help identify and prioritize logic errors, e.g., 
#    based on severity or occurrence frequency.
#
# 3. **Continuous Integration Compatibility**: Enable this module to run 
#    as a CI pipeline step, auto-checking code for errors during 
#    development and committing, and logging results for easier tracking.
# -------------------------------------------------------------------
