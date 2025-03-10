"""
Utility functions for the EDColonyTracker application.
"""

import os
import logging

# Base directory of the application
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Log file path
LOG_FILE = os.path.join(BASE_DIR, "edcolonytracker.log")

# Configure logging once for the entire application
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def get_logger(name):
    """
    Get a configured logger with the given name.
    
    Args:
        name (str): The name for the logger, typically the module name.
        
    Returns:
        logging.Logger: A configured logger instance.
    """
    return logging.getLogger(name)

def ensure_directory_exists(path):
    """Ensure that a directory exists, creating it if necessary."""
    if not os.path.exists(path):
        os.makedirs(path)
        logger = get_logger('EDColonyTracker')
        logger.info(f"Created directory: {path}")