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
import os
import sys

from duHast.Utilities.directory_io import create_target_directory
from duHast.Utilities.Objects.base import Base
from duHast.Utilities.logging_handlers import std_console_handler, std_file_handler


class LoggerObject(Base):
    def __init__(
        self,
        log_name="duHast",
        output_path=os.getenv("APPDATA"),
        log_level=(10, 30),
        file_format=".txt",
        cons_str_handler=None,
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
        logging.basicConfig(level=logging.INFO)
        # Get log naming and output path
        self.log_name = log_name
        self.output_path = output_path
        self.log_file_dir = os.path.join(self.output_path, self.log_name)
        # Create the directory and the full log file path
        create_target_directory(self.output_path, self.log_name)
        self.log_file_path = os.path.join(self.log_file_dir, log_name + file_format)
        # Get log levels
        self.log_level = log_level
        self.file_log_level, self.console_log_level = self.log_level
        # Set handlers
        self.file_handler = std_file_handler(self)
        self.console_handler = std_console_handler(self, cons_str_handler)

        # Create logger object
        self.new_logger = logging.getLogger(self.log_name)
        self.init_handlers()
        self.logger_object = self.new_logger

    def clear_handlers(self):
        self.new_logger.propagate = 0
        while self.new_logger.handlers:
            self.new_logger.handlers.pop()

    def init_handlers(self):
        self.clear_handlers()
        self.new_logger.setLevel(logging.DEBUG)
        self.new_logger.addHandler(self.file_handler)
        self.new_logger.addHandler(self.console_handler)

    def set_stream_handler(self, st_handlr):
        self.clear_handlers()
        self.new_logger.setLevel(logging.DEBUG)
        self.new_logger.addHandler(self.file_handler)
        self.new_logger.addHandler(st_handlr)

    def get_logger_obj(self):
        return self.logger_object

    def update_log_level(self, log_level):
        """
        Set the log levels for the file and console handlers
        """
        log_level_file, log_level_console = log_level
        self.file_handler.setLevel(log_level_file)
        self.console_handler.setLevel(log_level_console)
        return self.get_logger_obj()
