# C:\Projects\AI_Debugger_Assistant\src\main.py
# 
#
# Description:
# This file is part of the AI_Debugger_Assistant project.
# It provides .
#
\"\"\"
Main Entry Point for AI Debugger Assistant

This script initializes the core components and starts the application.
\"\"\"

from agents.agent_dispatcher import AgentDispatcher
from memory.memory_manager import MemoryManager
from error_detection.error_detection import ErrorDetector
from gui.ai_agent_gui import AIAgentGUI

def main():
    # Initialize core components
    memory_manager = MemoryManager()
    error_detector = ErrorDetector()
    agent_dispatcher = AgentDispatcher()

    # Start the GUI
    gui = AIAgentGUI(agent_dispatcher, memory_manager, error_detector)
    gui.run()

if __name__ == "__main__":
    main()
