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
def get_api_logger(module_name: str):
    return setup_logger(module_name, "api", "api_api")

def get_canteen_logger(module_name: str):
    return setup_logger(module_name, "canteen", "canteen_api")

def get_menu_logger(module_name: str):
    return setup_logger(module_name, "menu", "menu_api")

def get_dish_logger(module_name: str):
    return setup_logger(module_name, "dish", "dish_api")

def get_user_logger(module_name: str):
    return setup_logger(module_name, "user", "user_api")

def get_feedback_logger(module_name: str):
    return setup_logger(module_name, "feedback", "feedback_api")

# Data Fetcher Loggers
def get_data_fetcher_logger(module_name: str):
    return setup_logger(module_name, "data_fetcher", "data_fetcher")
