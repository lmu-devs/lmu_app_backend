import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


def setup_logger(module_name: str, component_name: str, log_file: Optional[str] = None):
    """Configure logger with consistent formatting and multiple handlers
    
    Args:
        module_name: The module name (usually __name__ from calling module)
        component_name: The component name (e.g., 'canteen', 'menu')
        log_file: Optional file name for logging to file
    """
    
    logger = logging.getLogger(str(component_name))
    
    if logger.hasHandlers():
        return logger
    
    logger.setLevel(logging.INFO)
    
    # Format
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File Handler (if log_file specified)
    if log_file:
        log_path = Path("logs")
        log_path.mkdir(exist_ok=True)
        
        file_handler = logging.FileHandler(
            log_path / f"{log_file}_{datetime.now().strftime('%Y%m%d')}.log"
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

# API Loggers
def get_food_api_logger(module_name: str):
    return setup_logger(module_name, "food", "food_api")

def get_user_logger(module_name: str):
    return setup_logger(module_name, "user", "user_api")

def get_feedback_logger(module_name: str):
    return setup_logger(module_name, "feedback", "feedback_api")

# Data Fetcher Loggers
def get_main_fetcher_logger(module_name: str):
    return setup_logger(module_name, "main_fetcher", "main_fetcher")

def get_eat_fetcher_logger(module_name: str):
    return setup_logger(module_name, "eat_fetcher", "eat_fetcher")

def get_movie_fetcher_logger(module_name: str):
    return setup_logger(module_name, "movie_fetcher", "movie_fetcher")