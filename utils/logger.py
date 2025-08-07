import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logger(name: str, log_file: str = "app.log", max_bytes: int = 10*1024*1024, backup_count: int = 5) -> logging.Logger:
    """
    Configures and returns a logger with console and rotating file handlers.
    
    Args:
        name: Name of the logger (usually __name__ of the calling module).
        log_file: Path to the log file.
        max_bytes: Maximum size of the log file before rotation (default: 10MB).
        backup_count: Number of backup log files to keep (default: 5).
    
    Returns:
        Configured logger instance.
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)  # Set default level to INFO
    
    # Avoid duplicate handlers if logger is already configured
    if not logger.handlers:
        # Formatter
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # File handler with rotation
        try:
            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=max_bytes,
                backupCount=backup_count
            )
            file_handler.setLevel(logging.INFO)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            logger.error(f"Failed to set up file handler for logging: {str(e)}")
    
    return logger