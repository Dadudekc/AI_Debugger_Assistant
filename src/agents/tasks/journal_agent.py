# -------------------------------------------------------------------
# File Path: C:\Projects\AI_Debugger_Assistant\src\agents\tasks\journal_agent.py
#
# Project: AI_Debugger_Assistant
#
# Description:
# This file defines the `JournalAgent` class, an agent responsible for 
# creating, organizing, and managing journal entries. It assists in 
# capturing debugging logs, session summaries, and user reflections, 
# contributing to enhanced traceability and knowledge retention.
#
# Classes:
# - JournalAgent: Extends `AgentBase` to provide task-specific methods 
#   for journal creation, organization, and data export.
#
# Usage:
# This module is instantiated and managed by the core agent dispatcher
# in the AI_Debugger_Assistant project.
# -------------------------------------------------------------------

import os
import datetime
import json
from src.agents.core.agent_base import AgentBase  # Adjust path as necessary

class JournalAgent(AgentBase):
    """
    An agent specialized in creating and managing journal entries.
    Provides functions for saving logs, reflections, and summaries
    related to debugging and development tasks.
    
    Attributes:
        name (str): The name of the agent.
        description (str): Brief description of the agent's role.
    """

    def __init__(self, name="JournalAgent", description="Agent for managing journal entries and logs"):
        """
        Initializes the JournalAgent with default parameters.
        
        Args:
            name (str): The agent's name.
            description (str): A short description of the agent's purpose.
        """
        super().__init__(name, description)
        self.journal_directory = "journals"  # Default directory for journal entries
        if not os.path.exists(self.journal_directory):
            os.makedirs(self.journal_directory)
        self.logger.info(f"{self.name} initialized for journal management.")

    def create_journal_entry(self, title: str, content: str, tags=None) -> dict:
        """
        Creates a new journal entry with title, content, and optional tags.

        Args:
            title (str): The title of the journal entry.
            content (str): The main content of the journal entry.
            tags (list of str, optional): Tags associated with the entry.

        Returns:
            dict: Metadata of the created entry, including file path and timestamp.
        """
        if tags is None:
            tags = []
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")
        filename = f"{self.journal_directory}/{title}_{timestamp}.json"
        
        entry_data = {
            "title": title,
            "content": content,
            "tags": tags,
            "timestamp": timestamp
        }
        
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(entry_data, file, indent=4)
        
        self.logger.info(f"Journal entry '{title}' created at {filename}.")
        return {"file_path": filename, "timestamp": timestamp}

    def retrieve_journal_entry(self, title: str) -> dict:
        """
        Retrieves a journal entry by title from the journal directory.

        Args:
            title (str): Title of the journal entry to retrieve.

        Returns:
            dict: The content of the journal entry if found, otherwise an error message.
        """
        try:
            matching_files = [f for f in os.listdir(self.journal_directory) if title in f]
            if not matching_files:
                raise FileNotFoundError(f"No journal entry found with title '{title}'.")

            filepath = os.path.join(self.journal_directory, matching_files[0])
            with open(filepath, "r", encoding="utf-8") as file:
                entry_data = json.load(file)
            
            self.logger.info(f"Retrieved journal entry '{title}'.")
            return entry_data
        except Exception as e:
            error_message = f"Error retrieving journal entry '{title}': {str(e)}"
            self.logger.error(error_message)
            return {"error": error_message}

    def update_journal_entry(self, title: str, new_content: str) -> dict:
        """
        Updates an existing journal entry with new content.

        Args:
            title (str): Title of the journal entry to update.
            new_content (str): New content to update in the journal entry.

        Returns:
            dict: Success message with the updated timestamp or error message.
        """
        try:
            entry = self.retrieve_journal_entry(title)
            if "error" in entry:
                return entry

            entry["content"] = new_content
            entry["timestamp"] = datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")
            filepath = os.path.join(self.journal_directory, f"{title}_{entry['timestamp']}.json")
            
            with open(filepath, "w", encoding="utf-8") as file:
                json.dump(entry, file, indent=4)
            
            self.logger.info(f"Updated journal entry '{title}' with new content.")
            return {"message": f"Journal entry '{title}' updated successfully.", "file_path": filepath}
        except Exception as e:
            error_message = f"Error updating journal entry '{title}': {str(e)}"
            self.logger.error(error_message)
            return {"error": error_message}

    def delete_journal_entry(self, title: str) -> dict:
        """
        Deletes a journal entry by title.

        Args:
            title (str): Title of the journal entry to delete.

        Returns:
            dict: Success or error message.
        """
        try:
            matching_files = [f for f in os.listdir(self.journal_directory) if title in f]
            if not matching_files:
                raise FileNotFoundError(f"No journal entry found with title '{title}'.")

            filepath = os.path.join(self.journal_directory, matching_files[0])
            os.remove(filepath)
            self.logger.info(f"Deleted journal entry '{title}'.")
            return {"message": f"Journal entry '{title}' deleted successfully."}
        except Exception as e:
            error_message = f"Error deleting journal entry '{title}': {str(e)}"
            self.logger.error(error_message)
            return {"error": error_message}

    def list_journal_entries(self) -> list:
        """
        Lists all journal entries in the journal directory.

        Returns:
            list: A list of journal entry metadata including titles and timestamps.
        """
        entries = []
        for filename in os.listdir(self.journal_directory):
            if filename.endswith(".json"):
                with open(os.path.join(self.journal_directory, filename), "r", encoding="utf-8") as file:
                    entry_data = json.load(file)
                    entries.append({"title": entry_data["title"], "timestamp": entry_data["timestamp"]})
        
        self.logger.info(f"Listed {len(entries)} journal entries.")
        return entries

# Example usage (testing purposes)
if __name__ == "__main__":
    journal_agent = JournalAgent()
    journal_agent.create_journal_entry("Debugging Session", "Fixed bug in login system", tags=["debugging", "login"])
    print("Current Entries:", journal_agent.list_journal_entries())


# -------------------------------------------------------------------
# Value-Adding Improvements
# -------------------------------------------------------------------
# 1. **Auto-Tagging with NLP**: Integrate an NLP model to analyze journal 
#    content and suggest or automatically add relevant tags, making journal 
#    organization more intuitive and enhancing searchability.
#
# 2. **Search and Filter Capabilities**: Add advanced search and filtering 
#    options based on tags, timestamps, and keywords within the content 
#    to retrieve specific journal entries quickly.
#
# 3. **Journal Summarization and Insights**: Incorporate a summarization 
#    feature to automatically generate concise summaries for each entry 
#    and provide monthly or project-based insights, improving retrospective analysis.
# -------------------------------------------------------------------
