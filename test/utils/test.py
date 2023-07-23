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
# BSD License
# Copyright 2023, Jan Christel
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

import os
import tempfile

from duHast.Utilities.Objects import base


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
    
