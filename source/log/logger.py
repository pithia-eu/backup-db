import os
import logging
from logging.handlers import RotatingFileHandler

DEFAULT_LOG_NAME = "backup-db"
DEFAULT_LOG_PATH = "log/main.log"
DEFAULT_LOG_LEVEL = logging.DEBUG
DEFAULT_LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
DEFAULT_MAX_BYTES = 100000
DEFAULT_BACKUP_COUNT = 5


def setup_logger(log_name=DEFAULT_LOG_NAME,
                 file_path=DEFAULT_LOG_PATH,
                 log_level=DEFAULT_LOG_LEVEL,
                 log_format=DEFAULT_LOG_FORMAT,
                 max_bytes=DEFAULT_MAX_BYTES,
                 backup_count=DEFAULT_BACKUP_COUNT,
                 verbose=True):

    # Create a logger
    logger = logging.getLogger(log_name)  # Give logger a specific name
    logger.setLevel(log_level)  # Sets the threshold for this logger to level.

    # Check if the directory exists and script has write access to the log file directory
    directory = os.path.dirname(os.path.abspath(file_path))
    if not os.path.exists(directory):
        logger.error(f"Directory {directory} does not exist.")
        raise FileNotFoundError(f"Directory {directory} does not exist.")
    if not os.access(directory, os.W_OK):
        logger.error(f"Script does not have write access to the directory {directory}.")
        raise PermissionError(f"Script does not have write access to the directory {directory}.")

    # Create handlers
    # Console handler (only add if verbose is True)
    if verbose:
        c_handler = logging.StreamHandler()
        c_handler.setLevel(log_level)  # Console handler level
        # Create formatters and add to console handler
        c_formatter = logging.Formatter(log_format)
        c_handler.setFormatter(c_formatter)
        # Add console handler to the logger
        logger.addHandler(c_handler)

    # Rotating File Handler
    try:
        f_handler = RotatingFileHandler(file_path, maxBytes=max_bytes, backupCount=backup_count)
    except PermissionError:
        logger.exception("There is no write permission to create a log file at this path.", exc_info=True)
        raise
    except FileNotFoundError:
        logger.exception("The provided file path does not exist.", exc_info=True)
        raise

    f_handler.setLevel(log_level)  # File handler level
    # Create formatters and add them to file handler
    f_formatter = logging.Formatter(log_format)
    f_handler.setFormatter(f_formatter)
    # Add file handler to the logger
    logger.addHandler(f_handler)

    return logger
