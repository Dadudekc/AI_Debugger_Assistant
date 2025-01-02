import sys
import json
import os
import subprocess
import tempfile
import shutil
import logging
from pathlib import Path

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QVBoxLayout, QPushButton, QWidget, QComboBox, QLabel,
    QHBoxLayout, QMessageBox, QFileDialog
)
from PyQt5.QtCore import Qt

# --------------------------------------------------------------------------
# LOGGING SETUP
# --------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("AdvancedAICodeBuilder")

class AdvancedAICodeBuilder(QMainWindow):
    """
    An advanced code builder/debugger app with:
      1. Logging for transparency.
      2. User-selected save location for generated projects.
      3. ASCII directory structure display for clarity.
      4. AI-driven multi-file generation and iterative debugging.
    """

    def __init__(self, projects_dir):
        super().__init__()
        self.projects_dir = projects_dir
        self.projects = self.load_projects(projects_dir)
        self.selected_project = None
        self.save_directory = None  # User-chosen directory for saving projects

        self.initUI()
        logger.info("Application initialized.")

    # --------------------------------------------------------------------------
    # 1. LOADING PROJECTS
    # --------------------------------------------------------------------------
    def load_projects(self, projects_dir):
        logger.info(f"Loading JSON projects from: {projects_dir}")
        projects = {}
        for filename in os.listdir(projects_dir):
            if filename.endswith(".json"):
                filepath = os.path.join(projects_dir, filename)
                with open(filepath, "r", encoding="utf-8") as f:
                    project_name = filename[:-5]  # Remove '.json'
                    projects[project_name] = json.load(f)
                    logger.info(f"Loaded project: {project_name} from {filepath}")
        return projects

    # --------------------------------------------------------------------------
    # 2. GUI SETUP
    # --------------------------------------------------------------------------
    def initUI(self):
        self.setWindowTitle("Advanced AI Code Builder/Debugger (Enhanced)")
        self.setGeometry(100, 100, 1200, 700)

        main_layout = QVBoxLayout()

        # Project selection
        self.project_dropdown = QComboBox(self)
        self.project_dropdown.addItem("Select Project")
        self.project_dropdown.addItems(self.projects.keys())
        self.project_dropdown.currentIndexChanged.connect(self.update_project_context)
        main_layout.addWidget(QLabel("Select Project:"))
        main_layout.addWidget(self.project_dropdown)

        # Prompt input
        self.prompt_input = QTextEdit(self)
        self.prompt_input.setPlaceholderText("Describe your build request, bug, or feature request...")
        main_layout.addWidget(QLabel("Prompt:"))
        main_layout.addWidget(self.prompt_input)

        # AI Response display
        self.response_display = QTextEdit(self)
        self.response_display.setReadOnly(True)
        main_layout.addWidget(QLabel("AI Response:"))
        main_layout.addWidget(self.response_display)

        # Code Editor
        self.code_editor = QTextEdit(self)
        self.code_editor.setPlaceholderText("Generated or debugged code (multi-file) appears here.")
        main_layout.addWidget(QLabel("Code/Output Editor:"))
        main_layout.addWidget(self.code_editor)

        # Execution/Build Output
        self.execution_output = QTextEdit(self)
        self.execution_output.setReadOnly(True)
        main_layout.addWidget(QLabel("Build/Execution Output:"))
        main_layout.addWidget(self.execution_output)

        # Buttons
        button_layout = QHBoxLayout()
        self.generate_button = QPushButton("Generate Project Code")
        self.generate_button.clicked.connect(self.generate_project_code)

        self.build_button = QPushButton("Build Project")
        self.build_button.clicked.connect(self.build_project)

        self.execute_button = QPushButton("Debug/Execute Code")
        self.execute_button.clicked.connect(self.debug_or_execute_code)

        self.select_save_button = QPushButton("Select Save Location")
        self.select_save_button.clicked.connect(self.select_save_location)

        button_layout.addWidget(self.generate_button)
        button_layout.addWidget(self.build_button)
        button_layout.addWidget(self.execute_button)
        button_layout.addWidget(self.select_save_button)
        main_layout.addLayout(button_layout)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    # --------------------------------------------------------------------------
    # 3. PROJECT SELECTION
    # --------------------------------------------------------------------------
    def update_project_context(self, index):
        if index > 0:
            project_name = self.project_dropdown.currentText()
            self.selected_project = self.projects[project_name]
            self.response_display.append(f"Selected Project: {project_name}")
            logger.info(f"Project selected: {project_name}")
        else:
            self.selected_project = None
            self.response_display.append("No project selected.")
            logger.info("No project selected.")

    def select_save_location(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory:
            self.save_directory = directory
            self.response_display.append(f"Save directory set to: {directory}")
            logger.info(f"User selected save directory: {directory}")
        else:
            self.response_display.append("Save directory not selected.")
            logger.info("User canceled save directory selection.")

    # --------------------------------------------------------------------------
    # 4. CODE GENERATION FOR ENTIRE PROJECT
    # --------------------------------------------------------------------------
    def generate_project_code(self):
        """
        Uses AI to generate an entire multi-file code structure for the selected project.
        """
        if not self.selected_project:
            self.response_display.append("No project selected. Please choose a project first.")
            logger.warning("Generate code called without selected project.")
            return

        prompt = self.prompt_input.toPlainText().strip()
        if not prompt:
            prompt = "Generate the entire multi-file code structure for this project."

        project_json_str = json.dumps(self.selected_project, indent=2)
        ai_prompt = (
            f"You are an advanced AI specialized in building multi-file coding projects.\n\n"
            f"Below is the JSON describing the project:\n{project_json_str}\n\n"
            f"Additional User Prompt:\n{prompt}\n\n"
            f"Task: Create a cohesive, multi-file code structure. Also provide an ASCII directory structure."
        )

        self.response_display.append("Generating project code via AI. Please wait...")
        logger.info("Requesting AI to generate project code.")
        code_output = self.run_ai_generation(ai_prompt)
        self.code_editor.setText(code_output)
        self.response_display.append("Project code generation complete.")
        logger.info("Project code generation complete.")

    def run_ai_generation(self, prompt):
        """
        Connect with your actual LLM or advanced code generation service.
        Return code + ASCII directory structure in a serialized format.
        """
        # Placeholder demonstration
        logger.info("run_ai_generation() invoked with prompt.")
        return (
            "# AI-Generated multi-file structure (with ASCII tree below):\n"
            "# FILE: main.py\n"
            "print('Hello from main!')\n\n"
            "# FILE: utils.py\n"
            "def helper():\n"
            "    pass\n\n"
            "## ASCII TREE:\n"
            "project_root\n"
            "├── main.py\n"
            "└── utils.py\n"
        )

    # --------------------------------------------------------------------------
    # 5. BUILDING THE PROJECT
    # --------------------------------------------------------------------------
    def build_project(self):
        """
        Writes code to user-chosen directory, installs dependencies,
        and displays ASCII directory structure for clarity.
        """
        if not self.selected_project:
            self.response_display.append("No project selected. Please choose a project first.")
            logger.warning("Build project called without selected project.")
            return

        if not self.save_directory:
            self.execution_output.append("No save directory selected. Please choose a save location.")
            logger.warning("No save directory selected for building.")
            return

        code_content = self.code_editor.toPlainText().strip()
        if not code_content:
            self.execution_output.append("No generated code to build.")
            logger.warning("Build called but code editor is empty.")
            return

        self.execution_output.append(f"Saving project to: {self.save_directory}")
        logger.info(f"Saving project to {self.save_directory}")

        # Parse AI output (multi-file + ASCII tree)
        project_dir = os.path.join(self.save_directory, "AIProject")
        os.makedirs(project_dir, exist_ok=True)

        self.execution_output.append(f"Creating project directory: {project_dir}")
        logger.info(f"Project directory created (or already exists): {project_dir}")

        # Convert code_content from a 'serialized multi-file structure' to actual files
        self.write_multifile_project(project_dir, code_content)

        # Show ASCII tree if present
        ascii_tree = self.extract_ascii_tree(code_content)
        if ascii_tree:
            self.execution_output.append("ASCII Directory Structure:\n")
            self.execution_output.append(ascii_tree)
            logger.info("Displayed ASCII directory structure.")

        # Install dependencies
        self.install_dependencies()
        self.execution_output.append("Build step complete. (For Python, no formal build command.)")
        logger.info("Build step complete.")

    def write_multifile_project(self, project_dir, code_content):
        lines = code_content.splitlines()
        current_file = None
        current_buffer = []
        for line in lines:
            if line.startswith("# FILE: "):
                # If there's a previous file, write it out
                if current_file and current_buffer:
                    self.write_file(project_dir, current_file, "\n".join(current_buffer))
                # Start a new file
                current_file = line.replace("# FILE: ", "").strip()
                current_buffer = []
            elif line.startswith("## ASCII TREE:"):
                # Stop processing files if we encounter ASCII tree
                # because everything after this might not be file contents
                break
            else:
                current_buffer.append(line)

        # Last file
        if current_file and current_buffer:
            self.write_file(project_dir, current_file, "\n".join(current_buffer))

    def write_file(self, project_dir, filename, content):
        file_path = os.path.join(project_dir, filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        logger.info(f"Created file: {file_path}")

    def extract_ascii_tree(self, code_content):
        """
        Looks for "## ASCII TREE:" in code_content and returns everything below it.
        """
        marker = "## ASCII TREE:"
        idx = code_content.find(marker)
        if idx == -1:
            return ""
        return code_content[idx + len(marker):].strip()

    def install_dependencies(self):
        """
        Installs dependencies from the 'technologies' field in the selected project JSON.
        """
        if not self.selected_project:
            return
        tech = self.selected_project.get("technologies", {})
        frameworks = tech.get("frameworks", [])
        libs = tech.get("libraries", [])
        packages = frameworks + libs

        if packages:
            self.execution_output.append("Installing dependencies...")
            logger.info("Installing dependencies from project JSON.")
        for pkg in packages:
            install_cmd = ["pip", "install", pkg]
            self.execution_output.append(f"Installing: {pkg}")
            logger.info(f"Installing package: {pkg}")
            try:
                subprocess.run(install_cmd, check=True, capture_output=True)
            except subprocess.CalledProcessError as e:
                error_msg = e.stderr.decode("utf-8").strip()
                self.execution_output.append(f"Error installing {pkg}: {error_msg}")
                logger.error(f"Error installing {pkg}: {error_msg}")

    # --------------------------------------------------------------------------
    # 6. DEBUG / EXECUTE CODE
    # --------------------------------------------------------------------------
    def debug_or_execute_code(self):
        """
        Iteratively debugs code until it runs or iteration limit is reached, then executes.
        """
        code_content = self.code_editor.toPlainText().strip()
        if not code_content:
            self.execution_output.append("No code to debug/execute.")
            logger.warning("Debug/execute called but code editor is empty.")
            return

        self.execution_output.append("Initiating iterative debug approach...\n")
        logger.info("Starting iterative debug loop.")
        final_code = self.iterative_debug(code_content)

        snippet = final_code[:300] + "..." if len(final_code) > 300 else final_code
        self.execution_output.append(f"Final code snippet after debug:\n{snippet}\n")

        self.execution_output.append("Executing final code...\n")
        execution_result = self.run_code_inline(final_code)
        self.execution_output.append(execution_result)
        logger.info("Execution finished.")

    def iterative_debug(self, code):
        max_iter = 5
        for i in range(max_iter):
            self.execution_output.append(f"Iteration {i+1} / {max_iter}\n")
            logger.info(f"Debug iteration {i+1} of {max_iter}")
            test_result = self.run_code_inline(code)

            if "Execution Error:" not in test_result:
                self.execution_output.append("No errors detected. Code is stable.\n")
                logger.info("Code stable, no errors found.")
                break

            # Extract error message
            error_msg = test_result.replace("Execution Error:", "").strip()
            self.execution_output.append(f"Error Detected:\n{error_msg}\n")

            # Request fix from AI
            code = self.run_ai_debug_suggestions(code, error_msg)
            snippet = code[:300] + "..." if len(code) > 300 else code
            self.execution_output.append(f"Updated code snippet:\n{snippet}\n")
            logger.info("AI provided an updated snippet.")
        else:
            self.execution_output.append("Reached iteration limit. Code may still be broken.\n")
            logger.warning("Hit iteration limit with unresolved errors.")

        return code

    # --------------------------------------------------------------------------
    # 7. AI DEBUG SUGGESTIONS
    # --------------------------------------------------------------------------
    def run_ai_debug_suggestions(self, current_code, error_msg):
        """
        Passes code and error to an AI, requesting a corrected version of the entire code.
        """
        debug_prompt = f"""
We have the following code that fails with the error:
{error_msg}

Current Code:
{current_code}

Please provide a corrected version of the entire code.
"""
        logger.info("Requesting AI debug suggestions.")
        return self.run_ollama(debug_prompt)

    # --------------------------------------------------------------------------
    # 8. CODE RUNNERS
    # --------------------------------------------------------------------------
    def run_code_inline(self, code):
        """
        Writes code to a temporary Python file, executes it, and captures output or errors.
        """
        logger.info("Running code inline in a temp file.")
        with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as temp_file:
            temp_file.write(code.encode("utf-8"))
            temp_file_path = temp_file.name

        try:
            result = subprocess.run(
                ["python", temp_file_path],
                capture_output=True,
                text=True,
                check=True
            )
            if result.stdout:
                return result.stdout
            return "Code executed successfully with no output."
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.strip()
            return f"Execution Error: {error_msg}"
        finally:
            os.remove(temp_file_path)

    # --------------------------------------------------------------------------
    # 9. AI PLACEHOLDER METHODS
    # --------------------------------------------------------------------------
    def run_ollama(self, prompt):
        """
        Replace with actual call to your LLM or advanced AI model.
        """
        logger.info("Placeholder run_ollama call made.")
        if "Please provide a corrected version" in prompt:
            return "# [AI-FIXED CODE]\nprint('AI fix attempt made!')\n"
        return (
            "# [AI-GENERATED MULTI-FILE STUB + ASCII TREE]\n"
            "print('Hello from advanced AI builder!')\n"
        )


# ------------------------------------------------------------------------------
# MAIN
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    projects_dir = r"D:\TradingRobotPlug\Chatbots\configs\projects"  # Update as needed
    app = QApplication(sys.argv)
    builder = AdvancedAICodeBuilder(projects_dir)
    builder.show()
    sys.exit(app.exec_())
