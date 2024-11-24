"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A logger class
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The LoggerObject class is a custom logger class that extends both logging.Logger and Base.
It is designed to handle logging with both file and console handlers, providing a structured
and formatted logging mechanism.

Key Features:
1. Initialization:
   - The constructor initializes the logger with a specified name, output path, log levels,
     file format, and handlers for both file and console logging.
   - It creates the necessary directories and sets up the log file path.
   - Handlers are set up with specified formatters and added to the logger.

2. Methods:
   - clear_handlers(): Clears all existing handlers from the logger.
   - init_handlers(): Initializes and adds the file and console handlers to the logger.
   - get_logger_obj(): Returns the logger object.
   - update_log_level(log_level): Updates the log levels for both file and console handlers.

Usage:
- The class can be used to create a logger that writes logs to a file and outputs them to the console
  with specified formats.
- It allows dynamic updating of log levels and ensures that handlers are properly managed.

Example Usage:

# Create a logger object
logger = LoggerObject(log_name="myLogger", output_path="/path/to/logs")

# Get the logger object
logger_obj = logger.get_logger_obj()

# Update log levels
logger.update_log_level((logging.INFO, logging.ERROR))

# Log messages
logger_obj.info("This is an info message")
logger_obj.error("This is an error message")


"""

# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2024, Jan Christel
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
from logging.handlers import RotatingFileHandler
import os

from duHast.Utilities.directory_io import create_target_directory
from duHast.Utilities.Objects.base import Base
from duHast.Utilities.logging_handlers import std_console_handler, std_file_handler
from duHast.Utilities.logger_formatting import level_time_local_msg_formatter, msg_only


class LoggerObject(logging.Logger, Base):
    def __init__(
        self,
        log_name="duHast",
        output_path=os.getenv("APPDATA"),
        log_level=(10, 30),
        file_format=".txt",
        fil_stream_hndlr=RotatingFileHandler,
        fil_stream_frmt=level_time_local_msg_formatter,
        cons_stream_hndlr=logging.StreamHandler,
        cons_stream_frmt=msg_only,
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
        :param file_format: The file format for the log file.
        :type file_format: str
        :param fil_stream_hndlr: The file stream handler class.
        :type fil_stream_hndlr: class
        :param fil_stream_frmt: The file stream formatter.
        :type fil_stream_frmt: logging.Formatter
        :param cons_stream_hndlr: The console stream handler class.
        :type cons_stream_hndlr: class
        :param cons_stream_frmt: The console stream formatter.
        :type cons_stream_frmt: logging.Formatter
        """
        
        # Get log naming and output path
        self.log_name = log_name
        self.output_path = output_path
        self.log_file_dir = os.path.join(self.output_path, self.log_name)
        # Create the directory and the full log file path
        create_target_directory(self.output_path, self.log_name)
        self.log_file_path = os.path.join(self.log_file_dir, log_name + file_format)
        logging.Logger.__init__(self, log_name)
        logging.basicConfig(filename=self.log_file_path, level=logging.INFO)
        # Get log levels
        self.level = log_level
        self.file_log_level, self.console_log_level = self.level
        # Set handlers
        self.file_handler = std_file_handler(
            self, file_hndlr=fil_stream_hndlr, file_formatter=fil_stream_frmt
        )
        self.console_handler = std_console_handler(
            self, cons_hndlr=cons_stream_hndlr, cons_formatter=cons_stream_frmt
        )

        # Create logger object
        self.new_logger = logging.getLogger(self.log_name)
        self.init_handlers()
        self.logger_object = self.new_logger

    def clear_handlers(self):
        """
        Clears all handlers from the logger.
        """
        
        self.new_logger.propagate = 0
        for handler in self.new_logger.handlers:
            handler.flush()
            handler.close()
            self.new_logger.removeHandler(handler)

    def init_handlers(self):
        """
        Initializes the file and console handlers for the logger.
        """
        
        self.clear_handlers()
        ex_handlers = [h.__class__.__name__ for h in self.new_logger.handlers]
        self.new_logger.setLevel(logging.INFO)

        if not "FileHandler" in ex_handlers:
            self.new_logger.addHandler(self.file_handler)
        if not "StreamHandler" in ex_handlers:
            self.new_logger.addHandler(self.console_handler)

    def get_logger_obj(self):
        """
        Returns the logger object.

        :return: The logger object.
        :rtype: logging.Logger
        """
        
        return self.logger_object

    def update_log_level(self, log_level):
        """
        Set the log levels for the file and console handlers.

        :param log_level: A tuple containing the log levels for the file and console handlers.
        :type log_level: tuple
        :return: The updated logger object.
        :rtype: logging.Logger
        """
        
        log_level_file, log_level_console = log_level
        self.file_handler.setLevel(log_level_file)
        self.console_handler.setLevel(log_level_console)
        return self.get_logger_obj()
