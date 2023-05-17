"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains revit test base class . 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Requires python 3
"""
#
# License:
#
#
# Revit Batch Processor Sample Code
#
# Copyright (c) 2023  Jan Christel
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#

import os
import tempfile

from duHast.Utilities import base


class Test(base.Base):
    def __init__(self, test_name):
        """"""

        # initialise base class
        super(Test, self).__init__()
        self.test_name = test_name

    def test(self):
        return True, ""

    def call_with_temp_directory(self,func):
        """
        Utility function setting up a temp directory and calling pass in function with that directory as an argument.

        :param func: test function to be executed
        :type func: func
        :return: True if all tests past, otherwise False
        :rtype: bool
        """

        flag = True
        message = "-"
        with tempfile.TemporaryDirectory() as tmp_dir:
            flag, message = func(tmp_dir)
        return flag, message

    def write_test_files(self, file_names, tmp_dir):
        """
        Utility function writing out test files into given directory

        :param file_names: A list of file names.
        :type file_names: [str]
        :param temp_dir: Fully qualified directory path.
        :type temp_dir: str
        """

        for file_name in file_names:
            file_path = os.path.join(tmp_dir, file_name)
            with open(file_path, "w") as f1:
                f1.write("test content")

    def write_file_with_data(self,file_name, tmp_dir, data):
        """
        Function writing out a text file with given data.

        :param file_name: The file name.
        :type file_name: str
        :param tmp_dir: The directory path.
        :type tmp_dir: str
        :param data: data to be written to file
        :type data: [str]
        """

        with open(os.path.join(tmp_dir, file_name), "w") as f:
            for d in data:
                f.write(d + "\n")
            f.close()
    
