import logging
from logging.handlers import RotatingFileHandler
import sys
from duHast.Utilities.logger_filtering import FilterConsole, FilterFile


class CustomStreamHandler(logging.StreamHandler):
    def __init__(self, custom_function, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.custom_function = custom_function

    def write(self, msg):
        self.custom_function(msg)


def std_file_handler(obj, file_hndlr, file_formatter):
    """
    Create file handler to obj.log_file_path location
    """
    # Set file output
    if file_hndlr == RotatingFileHandler:
        file_handler = file_handler = RotatingFileHandler(
            filename=obj.log_file_path, maxBytes=5 * 1024 * 1024, backupCount=1
        )
    else:
        file_handler = file_hndlr(obj.log_file_path)
    # Default file level is INFO
    file_handler.setLevel(obj.file_log_level)
    # Add the filter to the file handler
    file_handler.addFilter(FilterFile())
    file_handler.setFormatter(file_formatter())
    file_handler.name = "file"
    return file_handler


def std_console_handler(obj, cons_hndlr, cons_formatter):
    """
    Creates a console handler to output to stdout (console)
    displaying only the message as default
    """
    # Create a console handler
    if cons_hndlr == logging.StreamHandler:
        console_handler = logging.StreamHandler(sys.stdout)
    else:
        console_handler = cons_hndlr(sys.stdout)
    # Default console level is WARNING
    console_handler.setLevel(obj.console_log_level)
    # Add the filter to the console handler
    console_handler.addFilter(FilterConsole())
    console_handler.setFormatter(cons_formatter())
    console_handler.name = "console"
    return console_handler
