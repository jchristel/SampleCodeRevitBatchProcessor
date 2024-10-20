import logging
import sys
from logger_filtering import FilterConsole, FilterFile
from logger_formatting import get_standard_formatter, get_presentation_formatter


class CustomStreamHandler(logging.StreamHandler):
    def __init__(self, custom_function, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.custom_function = custom_function

    def write(self, msg):
        self.custom_function(msg)


def std_file_handler(obj):
    """
    Create file handler to obj.log_file_path location
    """
    # Set file output
    file_handler = logging.FileHandler(obj.log_file_path)
    # Default file level is INFO
    file_handler.setLevel(obj.file_log_level)
    # Add the filter to the file handler
    file_handler.addFilter(FilterFile())
    file_handler.setFormatter(get_standard_formatter())
    file_handler.name = "file"
    return file_handler


def std_console_handler(obj, console_out):
    """
    Creates a console handler to output to stdout (console)
    displaying only the message as default
    """
    # Create a console handler
    if console_out != None:
        console_handler = logging.StreamHandler(console_out)
    else:
        console_handler = logging.StreamHandler(sys.stdout)
    # Default console level is WARNING
    console_handler.setLevel(obj.console_log_level)
    # Add the filter to the console handler
    console_handler.addFilter(FilterConsole())
    console_handler.setFormatter(get_presentation_formatter())
    return console_handler
