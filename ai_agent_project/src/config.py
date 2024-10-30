# config.py

"""
Configuration Module

Contains configuration settings for the AI Agent Integration system,
including database paths, logging settings, and AI model parameters.
"""

import os

# Database Configuration
DB_PATH = os.getenv('DB_PATH', 'ai_agent_memory.db')
TABLE_NAME = os.getenv('TABLE_NAME', 'memory_entries')

# Logging Configuration
LOG_FILE = os.getenv('LOG_FILE', 'logs/ai_agent.log')
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')  # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL

# AI Model Configuration
AI_MODEL = os.getenv('AI_MODEL', 'mistral')
OLLAMA_COMMAND = os.getenv('OLLAMA_COMMAND', 'ollama')

# Memory Management
MEMORY_RETRIEVE_LIMIT = int(os.getenv('MEMORY_RETRIEVE_LIMIT', '5'))
MEMORY_CLEANUP_DAYS = int(os.getenv('MEMORY_CLEANUP_DAYS', '30'))

# Other Configurations can be added here
