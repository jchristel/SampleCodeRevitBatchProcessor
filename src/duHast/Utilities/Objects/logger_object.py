"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A logger class
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2024, Peter Smith
# All rights reserved.

# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

# - Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# - Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# - Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
#
# This software is provided by the copyright holder "as is" and any express or implied warranties, including, but not limited to, the implied warranties of merchantability and fitness for a particular purpose are disclaimed.
# In no event shall the copyright holder be liable for any direct, indirect, incidental, special, exemplary, or consequential damages (including, but not limited to, procurement of substitute goods or services; loss of use, data, or profits;
# or business interruption) however caused and on any theory of liability, whether in contract, strict liability, or tort (including negligence or otherwise) arising in any way out of the use of this software, even if advised of the possibility of such damage.
#
#
#

import logging
import os
import sys

from duHast.Utilities.directory_io import create_target_directory
from duHast.Utilities.Objects.base import Base


class FilterFile(logging.Filter):
    """
    Filter to stop logs to file handler.

    To use change your log call to something like:
    my_logger.info("This is a console only output", extra={"block": "file"})
    """

    def filter(self, record):
        if "block" in record.__dict__.keys():
            if record.block == "file":
                return False
        return True


class FilterConsole(logging.Filter):
    """
    Filter to stop logs to console handler.

    To use change your log call to something like:
    my_logger.info("This is a file only output", extra={"block": "console"})
    """

    def filter(self, record):
        if "block" in record.__dict__.keys():
            if record.block == "console":
                return False
        return True


class LoggerObject(Base):
    def __init__(
        self,
        log_name="duHast",
        output_path=os.getenv("APPDATA"),
        log_level=(10, 30),
        **kwargs
    ):

        """
        Constructor for the LoggerObject class.

        :param log_name: The name of the log.
        :type log_name: str
        :param output_path: The path to the output directory.
        :type output_path: str
        :param log_level: The log levels for the file and console handlers.
        :type log_level: tuple
        """

        super(LoggerObject, self).__init__(**kwargs)

        # Get log naming and output path
        self.log_name = log_name
        self.output_path = output_path
        self.log_file_dir = os.path.join(self.output_path, self.log_name)
        create_target_directory(self.output_path, self.log_name)
        self.log_file_path = os.path.join(self.log_file_dir, self.log_name + ".log")
        # Get log levels
        self.log_level = log_level
        self.file_log_level, self.console_log_level = self.log_level
        # Establish handlers
        self.file_log_format = self.get_standard_formatter()
        self.file_handler = self.create_file_handler()
        self.console_log_format = self.get_presentation_formatter()
        self.console_handler = self.create_console_handler()
        # Create logger object
        new_logger = logging.getLogger(self.log_name)
        new_logger.propagate = 0
        while new_logger.handlers:
            new_logger.handlers.pop()
        new_logger.setLevel(logging.DEBUG)
        new_logger.addHandler(self.file_handler)
        new_logger.addHandler(self.console_handler)

        self.logger_object = new_logger
        logging.basicConfig(level=logging.DEBUG)

    def get_logger_obj(self):
        return self.logger_object

    def get_standard_formatter(self):
        """Standard output formatting for console and file handlers"""
        return logging.Formatter(
            "%(levelname)s | %(asctime)s.%(msecs)03d | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    def get_presentation_formatter(self):
        """Output formatting for presentation"""
        return logging.Formatter("%(message)s")

    def create_file_handler(self):
        """
        Create file handler to self.log_file_path location
        """
        # Set file output
        file_handler = logging.FileHandler(self.log_file_path)
        # Default file level is INFO
        file_handler.setLevel(self.file_log_level)
        # Add the filter to the file handler
        file_handler.addFilter(FilterFile())
        file_handler.setFormatter(self.file_log_format)
        file_handler.name = "file"
        return file_handler

    def create_console_handler(self):
        """
        Creates a console handler to output to stdout (console)
        displaying only the message as default
        """
        # Create a console handler
        console_handler = logging.StreamHandler(sys.stdout)
        # Default console level is WARNING
        console_handler.setLevel(self.console_log_level)
        # Add the filter to the console handler
        console_handler.addFilter(FilterConsole())
        console_handler.setFormatter(self.console_log_format)
        return console_handler

    def update_log_level(self, log_level):
        """
        Set the log levels for the file and console handlers
        """
        log_level_file, log_level_console = log_level
        self.file_handler.setLevel(log_level_file)
        self.console_handler.setLevel(log_level_console)
        return self.get_logger_obj()
