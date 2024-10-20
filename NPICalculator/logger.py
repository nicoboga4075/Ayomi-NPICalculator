""" Logging configuration for the app using Python logging built-in.

This module sets up a custom logger for the FastAPI application
and overrides uvicorn loggers.

"""
from logging import Formatter, getLogger
from logging.config import dictConfig
import sys

class CustomFormatter(Formatter):
    """ Custom logging formatter dynamically including extra attributes if they 
    are present in the log record, and uses a default log message and date format.
    """
    default_format = "%(asctime)s - %(levelname)s - Custom : %(message)s"
    default_datefmt = "%Y-%m-%d %H:%M:%S"

    def __init__(self, fmt=None, datefmt=None):
        """ Initializes custom formatter with default formats if none are provided. """
        fmt = fmt or self.default_format
        datefmt = datefmt or self.default_datefmt
        super().__init__(fmt=fmt, datefmt=datefmt)

    def format(self, record):
        """ Overrides the base format method to dynamically build the log message,
        including extra attributes if they are available in the record.
        """
        # Formats the time using the provided datefmt or default
        formatted_time = self.formatTime(record, self.datefmt)

        # Base log message
        base_message = f"{formatted_time} - {record.levelname} - Custom : {record.getMessage()}"

        # Optionally adds method, url, and process_time if they exist in the record
        if hasattr(record, "method"):
            base_message += f" - {record.method}"
        if hasattr(record, "url"):
            base_message += f" - {record.url}"
        if hasattr(record, "status_code"):
            base_message += f" - {record.status_code}"
        if hasattr(record, "process_time"):
            base_message += f" - {record.process_time:.2f}s"
        return base_message

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "uvicorn_formatter": {
            "format": "%(asctime)s - %(levelname)s - Uvicorn : %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S"
        },
        "custom_formatter": {
            "()": CustomFormatter,
        },
    },
    "handlers": {
        "uvicorn_console": {
            "class": "logging.StreamHandler",
            "formatter": "uvicorn_formatter",
            "level": "INFO",
            "stream": sys.stdout,
        },
        "custom_console": {
            "class": "logging.StreamHandler",
            "formatter": "custom_formatter",
            "level": "INFO",
            "stream": sys.stdout,
        },
        "file_handler": {
            "class": "logging.FileHandler",
            "formatter": "custom_formatter",
            "level": "INFO",
            "filename": "app.log",
            "mode": "a",
        },
    },
    "loggers": {
        "uvicorn": {
            "handlers": ["uvicorn_console"],
            "level": "INFO",
            "propagate": False,
        },
        "uvicorn.error": {
            "handlers": ["uvicorn_console", "file_handler"],
            "level": "INFO",
            "propagate": False,
        },
        "uvicorn.access": {
            "handlers": ["uvicorn_console"],
            "level": "WARNING", # Sets to WARNING to be overriden by custom for HTTP requests
            "propagate": False,
        },
        "custom": {
            "handlers": ["custom_console", "file_handler"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

dictConfig(LOGGING_CONFIG)

logger = getLogger("custom")
