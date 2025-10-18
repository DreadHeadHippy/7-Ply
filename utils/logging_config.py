"""
Logging configuration for 7-Ply Discord Bot
Sets up persistent file logging with rotation
"""

import logging
import logging.handlers
import os
from datetime import datetime

def setup_logging():
    """Configure logging for security and file operations"""
    
    # Ensure logs directory exists
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    # Configure security logger
    security_logger = logging.getLogger('7ply_security')
    security_logger.setLevel(logging.INFO)
    
    # Security log file with rotation (10MB, keep 5 files)
    security_handler = logging.handlers.RotatingFileHandler(
        os.path.join(log_dir, 'security.log'),
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    
    security_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    security_handler.setFormatter(security_formatter)
    security_logger.addHandler(security_handler)
    
    # Configure file operations logger
    file_logger = logging.getLogger('7ply_file_security')
    file_logger.setLevel(logging.INFO)
    
    # File operations log with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        os.path.join(log_dir, 'file_operations.log'),
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    
    file_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    file_logger.addHandler(file_handler)
    
    # Configure general bot logger
    bot_logger = logging.getLogger('7ply_bot')
    bot_logger.setLevel(logging.INFO)
    
    # General bot log
    bot_handler = logging.handlers.RotatingFileHandler(
        os.path.join(log_dir, 'bot.log'),
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    
    bot_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - [%(name)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    bot_handler.setFormatter(bot_formatter)
    bot_logger.addHandler(bot_handler)
    
    # Also log to console for immediate feedback
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)  # Only warnings and errors to console
    console_formatter = logging.Formatter('%(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)
    
    security_logger.addHandler(console_handler)
    file_logger.addHandler(console_handler)
    bot_logger.addHandler(console_handler)
    
    return security_logger, file_logger, bot_logger

# Initialize logging when module is imported
security_logger, file_logger, bot_logger = setup_logging()

# Export for use in other modules
__all__ = ['security_logger', 'file_logger', 'bot_logger']