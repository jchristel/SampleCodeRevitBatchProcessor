"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains file size tests . 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright © 2023, Jan Christel
# All rights reserved.

# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

# - Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# - Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# - Neither the name of Jan Christel nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
#
# This software is provided by Jan Christel "as is" and any express or implied warranties, including, but not limited to, the implied warranties of merchantability and fitness for a particular purpose are disclaimed. 
# In no event shall Jan Christel be liable for any direct, indirect, incidental, special, exemplary, or consequential damages (including, but not limited to, procurement of substitute goods or services; loss of use, data, or profits; 
# or business interruption) however caused and on any theory of liability, whether in contract, strict liability, or tort (including negligence or otherwise) arising in any way out of the use of this software, even if advised of the possibility of such damage.
#
#
#

from test.utils import test
import os

from duHast.Utilities.files_io import (
    get_file_size,
    FILE_SIZE_IN_KB,
    FILE_SIZE_IN_MB,
    FILE_SIZE_IN_GB,
)


class FileSize(test.Test):
    def __init__(self):
        # store document in base class
        super(FileSize, self).__init__(test_name="file_size")

    def test(self):
        """
        file_size test

        :param tmpdir: temp directory
        :type tmpdir: str
        :return: True if all tests past, otherwise False
        :rtype: bool
        """

        flag = True
        message = "-"
        try:
            # test data
            test_files = [
                "test_file_size.txt",
            ]

            # test short data
            def action_one(tmp_dir):
                flag_action = True
                message_action = ""
                try:
                    self.write_test_files(test_files, tmp_dir)
                    # get full test file path
                    file_path = os.path.join(tmp_dir, test_files[0])

                    # get file size
                    file_size = os.path.getsize(file_path)
                    message_action = "File size in byte on disk: {}".format(file_size)

                    # Test file size in KB
                    result = get_file_size(file_path, unit=FILE_SIZE_IN_KB)
                    expected_result = file_size / 1024
                    message_action = (
                        message_action
                        + "\n"
                        + (" {} vs {}".format(result, expected_result))
                    )
                    assert expected_result == result

                    # Test file size in MB
                    result = get_file_size(file_path, unit=FILE_SIZE_IN_MB)
                    expected_result = file_size / (1024 * 1024)
                    message_action = (
                        message_action
                        + "\n"
                        + (" {} vs {}".format(result, expected_result))
                    )
                    assert expected_result == result

                    # Test file size in GB
                    result = get_file_size(file_path, unit=FILE_SIZE_IN_GB)
                    expected_result = file_size / (1024 * 1024 * 1024)
                    message_action = (
                        message_action
                        + "\n"
                        + (" {} vs {}".format(result, expected_result))
                    )
                    assert expected_result == result
                except Exception as e:
                    flag_action = False
                    message_action = (
                        message_action
                        + "\n"
                        + (
                            "An exception occurred in function  {} : {}".format(
                                self.test_name, e
                            )
                        )
                    )
                return flag_action, message_action

            flag, message = self.call_with_temp_directory(action_one)

        except Exception as e:
            flag = False
            message = (
                message
                + "\n"
                + (
                    "An exception occurred in function {} : {}".format(
                        self.test_name, e
                    )
                )
            )
        return flag, message
