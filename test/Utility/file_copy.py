"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains file copy tests . 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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

from test.utils import test
import os

from duHast.Utilities.files_io import (
    copy_file,
    file_exist,
)


class FileCopy(test.Test):
    def __init__(self):
        # store document in base class
        super(FileCopy, self).__init__(test_name="file_copy")

    def test(self):
        """
        file_copy test

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

            # test valid file copy
            def action_one(tmp_dir):
                flag_action = True
                message_action = ""
                new_file_name = os.path.join(tmp_dir,"new file_name.txt")
                try:
                    self.write_test_files(test_files, tmp_dir)
                    result = copy_file(os.path.join(tmp_dir, test_files[0]), new_file_name)
                    expected_result = True
                    expected_result_check = file_exist(new_file_name)
                    message_action = (
                        "File copy: {} vs  expected: {} vs file check {}".format(
                            result, expected_result, expected_result_check
                        )
                    )
                    assert expected_result == result
                    assert expected_result_check == result

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
            
            # test in-valid file copy
            def action_two(tmp_dir):
                flag_action = True
                message_action = ""
                new_file_name = os.path.join(tmp_dir,"new file_name.txt")
                try:
                    self.write_test_files(test_files, tmp_dir)
                    result = copy_file("invalid/file/name.txt", new_file_name)
                    expected_result = False
                    expected_result_check = file_exist(new_file_name)
                    message_action = (
                        "File copy: {} vs  expected: {} vs file check {}".format(
                            result, expected_result, expected_result_check
                        )
                    )
                    assert expected_result == result
                    assert expected_result_check == result

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

            flag_one, message_one = self.call_with_temp_directory(action_one)
            flag_two, message_two = self.call_with_temp_directory(action_two)

            flag = flag_one & flag_two
            message = "{}\n{}".format(message_one, message_two)

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
