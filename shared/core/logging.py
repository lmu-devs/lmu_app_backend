import logging
import sys
from datetime import datetime
from pathlib import Path

def setup_logger(name: str, log_file: str = None):
    """Configure logger with consistent formatting and multiple handlers"""
    logger = logging.getLogger(name)
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

logger_fetcher = setup_logger("data_fetcher", "fetcher")