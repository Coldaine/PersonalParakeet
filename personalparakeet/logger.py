import logging
import sys
from pathlib import Path

def setup_logger(name: str = "personalparakeet", level: str = "INFO") -> logging.Logger:
    """Setup logger with console and file handlers"""
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Console handler with emojis
    console = logging.StreamHandler(sys.stdout)
    console_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console.setFormatter(console_format)
    
    # File handler without emojis
    log_dir = Path.home() / ".personalparakeet" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    file_handler = logging.FileHandler(log_dir / "personalparakeet.log")
    file_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_format)
    
    logger.addHandler(console)
    logger.addHandler(file_handler)
    return logger