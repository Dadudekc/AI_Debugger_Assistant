# memory_manager.py

"""
MemoryManager Class

Handles all interactions with the SQLite database for storing and retrieving
memory entries related to AI agent interactions. Implements concurrency handling,
input sanitization, and logging for robust memory management.
"""

import sqlite3
import threading
import logging
from datetime import datetime

class MemoryManager:
    def __init__(self, db_path="ai_agent_memory.db", table_name="memory_entries"):
        """
        Initialize the MemoryManager with the path to the SQLite database and table name.

        Args:
            db_path (str): Path to the SQLite database file.
            table_name (str): Name of the table to store memory entries.
        """
        self.db_path = db_path
        self.table_name = table_name
        self.lock = threading.Lock()
        self._initialize_database()

    def _initialize_database(self):
        """
        Create the memory table if it doesn't exist.
        """
        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {self.table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_name TEXT NOT NULL,
            user_prompt TEXT NOT NULL,
            ai_response TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(create_table_query)
            conn.commit()
        logging.info(f"Initialized database and ensured table '{self.table_name}' exists.")

    def _get_connection(self):
        """
        Get a new database connection.

        Returns:
            sqlite3.Connection: A new connection object.
        """
        return sqlite3.connect(self.db_path)

    def save_memory(self, project_name, user_prompt, ai_response):
        """
        Save a memory entry to the database.

        Args:
            project_name (str): The name of the project/domain.
            user_prompt (str): The user's prompt.
            ai_response (str): The AI's response.
        """
        insert_query = f"""
        INSERT INTO {self.table_name} (project_name, user_prompt, ai_response)
        VALUES (?, ?, ?);
        """
        with self.lock, self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(insert_query, (project_name, user_prompt, ai_response))
            conn.commit()
        logging.info(f"Saved memory entry for project '{project_name}'.")

    def retrieve_memory(self, project_name, limit=5):
        """
        Retrieve the latest memory entries for a given project.

        Args:
            project_name (str): The name of the project/domain.
            limit (int): Number of recent entries to retrieve.

        Returns:
            str: Formatted string of past interactions to include in the prompt.
        """
        select_query = f"""
        SELECT user_prompt, ai_response FROM {self.table_name}
        WHERE project_name = ?
        ORDER BY timestamp DESC
        LIMIT ?;
        """
        with self.lock, self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(select_query, (project_name, limit))
            rows = cursor.fetchall()
        # Reverse to maintain chronological order
        rows = rows[::-1]
        memory_context = ""
        for user_prompt, ai_response in rows:
            memory_context += f"User: {user_prompt}\nAI: {ai_response}\n"
        logging.info(f"Retrieved {len(rows)} memory entries for project '{project_name}'.")
        return memory_context

    def delete_memory_older_than(self, project_name, days):
        """
        Delete memory entries older than a certain number of days for a project.

        Args:
            project_name (str): The name of the project/domain.
            days (int): Number of days to retain memories.
        """
        delete_query = f"""
        DELETE FROM {self.table_name}
        WHERE project_name = ?
        AND timestamp < datetime('now', ?);
        """
        time_threshold = f"-{days} days"
        with self.lock, self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(delete_query, (project_name, time_threshold))
            conn.commit()
        logging.info(f"Deleted memory entries older than {days} days for project '{project_name}'.")

    def summarize_memories(self, project_name, limit=100):
        """
        Summarize a large number of memory entries to manage database size.

        Args:
            project_name (str): The name of the project/domain.
            limit (int): Number of recent entries to keep before summarizing.
        """
        # Placeholder for summarization logic
        # This could involve using the AI to generate a summary of past interactions
        logging.info(f"Summarization feature is not yet implemented for project '{project_name}'.")

    def close(self):
        """
        Close any open connections if necessary.
        (For SQLite, connections are managed via context managers, so this might be redundant.)
        """
        pass
