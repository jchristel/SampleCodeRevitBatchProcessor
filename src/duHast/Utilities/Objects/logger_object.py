import logging
import os
import sys

from duHast.Utilities.directory_io import create_target_directory


def check_log_file_dir_exists(log_file_dir):
    if not os.path.exists(log_file_dir):
        os.mkdir(log_file_dir)


class LoggerObject:
    def __init__(
        self, log_name="duHast", output_path=os.getenv("APPDATA"), log_level=(10, 30)
    ):
        self.log_name = log_name
        self.output_path = output_path  # os.getenv("APPDATA")
        self.log_file_dir = os.path.join(self.output_path, self.log_name)
        # check_log_file_dir_exists(self.log_file_dir)
        create_target_directory(self.output_path, self.log_name)
        self.log_file_path = os.path.join(self.log_file_dir, self.log_name + ".log")
        log_level_file, log_level_console = log_level
        self.file_log_level = log_level_file
        self.file_log_format = self.get_standard_formatter()
        self.file_handler = self.create_file_handler()
        self.console_log_level = log_level_console
        self.console_log_format = self.get_standard_formatter()
        self.console_handler = self.create_console_handler()
        self.logger_object = self.get_logger()
        logging.basicConfig(level=logging.DEBUG)

    def get_standard_formatter(self):
        return logging.Formatter(
            "%(levelname)s | %(asctime)s.%(msecs)03d | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    def create_file_handler(self):
        # Set file output
        file_handler = logging.FileHandler(self.log_file_path)
        # Default file level is INFO
        file_handler.setLevel(self.file_log_level)
        file_handler.setFormatter(self.file_log_format)
        return file_handler

    def create_console_handler(self):
        # Create a console handler
        console_handler = logging.StreamHandler(sys.stdout)
        # Default console level is WARNING
        console_handler.setLevel(self.console_log_level)
        console_handler.setFormatter(self.console_log_format)
        return console_handler

    def get_logger(self, name=None, func_name=""):
        if name == None:
            new_logger = logging.getLogger(self.log_name)
        else:
            new_logger = logging.getLogger(name)

        new_logger.propagate = 0
        while new_logger.handlers:
            new_logger.handlers.pop()
        new_logger.setLevel(logging.DEBUG)
        new_logger.addHandler(self.file_handler)
        new_logger.addHandler(self.console_handler)
        self.logger_object = new_logger
        return new_logger

    def get_logger_obj(self):
        return self.logger_object

    def update_log_level(self, log_level):
        log_level_file, log_level_console = log_level
        self.file_handler.setLevel(log_level_file)
        self.console_handler.setLevel(log_level_console)
        return self.get_logger_obj()
