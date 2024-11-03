import sqlite3
import threading
import logging
from datetime import datetime

class MemoryManager:
    def __init__(self, db_path="ai_agent_memory.db", table_name="memory_entries"):
        self.db_path = db_path
        self.table_name = table_name
        self.lock = threading.Lock()
        self._initialize_database()

    def _initialize_database(self):
        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {self.table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_name TEXT NOT NULL,
            user_prompt TEXT NOT NULL,
            ai_response TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(create_table_query)
                conn.commit()
            logging.info(f"Initialized database and ensured table '{self.table_name}' exists.")
        except sqlite3.Error as e:
            logging.error(f"Failed to initialize database: {e}")

    def _get_connection(self):
        try:
            conn = sqlite3.connect(self.db_path)
            logging.debug("Database connection established.")
            return conn
        except sqlite3.Error as e:
            logging.error(f"Failed to connect to database: {e}")
            raise

    def save_memory(self, project_name, user_prompt, ai_response):
        insert_query = f"""
        INSERT INTO {self.table_name} (project_name, user_prompt, ai_response)
        VALUES (?, ?, ?);
        """
        try:
            with self.lock, self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(insert_query, (project_name, user_prompt, ai_response))
                conn.commit()
            logging.info(f"Saved memory entry for project '{project_name}'.")
        except sqlite3.Error as e:
            logging.error(f"Failed to save memory: {e}")

    def retrieve_memory(self, project_name, limit=5):
        select_query = f"""
        SELECT user_prompt, ai_response FROM {self.table_name}
        WHERE project_name = ?
        ORDER BY timestamp DESC
        LIMIT ?;
        """
        try:
            with self.lock, self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(select_query, (project_name, limit))
                rows = cursor.fetchall()
            rows = rows[::-1]  # Reverse to chronological order
            memory_context = ""
            for user_prompt, ai_response in rows:
                memory_context += f"User: {user_prompt}\nAI: {ai_response}\n"
            logging.info(f"Retrieved {len(rows)} memory entries for project '{project_name}'.")
            return memory_context
        except sqlite3.Error as e:
            logging.error(f"Failed to retrieve memory: {e}")
            return ""

    def delete_memory_older_than(self, project_name, days):
        delete_query = f"""
        DELETE FROM {self.table_name}
        WHERE project_name = ?
        AND timestamp < datetime('now', ?);
        """
        time_threshold = f"-{days} days"
        try:
            with self.lock, self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(delete_query, (project_name, time_threshold))
                conn.commit()
            logging.info(f"Deleted memory entries older than {days} days for project '{project_name}'.")
        except sqlite3.Error as e:
            logging.error(f"Failed to delete old memories: {e}")

    def summarize_memories(self, project_name, limit=100):
        logging.info(f"Summarization feature is not yet implemented for project '{project_name}'.")

    def close(self):
        logging.debug("MemoryManager close method called.")
        pass
