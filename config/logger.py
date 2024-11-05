# File Path: C:\Projects\AI_Debugger_Assistant\ai_agent_project\src\utils\logger.py

import logging
import sys

def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Sets up a logger with the given name and level.

    Args:
        name (str): Name of the logger.
        level (int): Logging level.

    Returns:
        logging.Logger: Configured logger.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Create console handler with a higher log level
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(level)

    # Create formatter and add it to the handlers
    formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(name)s: %(message)s')
    ch.setFormatter(formatter)

    # Add the handlers to the logger if not already added
    if not logger.handlers:
        logger.addHandler(ch)

    return logger

# Initialize the root logger
setup_logger(__name__)
