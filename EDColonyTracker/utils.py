"""
Utility functions for Elite Dangerous Cargo Tracker.
"""

import os
import sys
import csv
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('edcolonytracker.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('EDColonyTracker')

def ensure_directory_exists(path):
    """Ensure that a directory exists, creating it if necessary."""
    if not os.path.exists(path):
        os.makedirs(path)
        logger.info(f"Created directory: {path}")