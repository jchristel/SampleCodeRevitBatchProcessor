"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains file rename tests . 
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
    file_exist,
    rename_file,
)


class FileRename(test.Test):
    def __init__(self):
        # store document in base class
        super(FileRename, self).__init__(test_name="file_rename")

    def test(self):
        """
        Test file_exist.

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
                ["file.txt", "file_after.txt"],
                ["file_2.text", "file_after.txt"],
                ["file_2.text", ""],
            ]

            test_file_to_be_written = list(entry[0] for entry in test_files)

            # test short data
            def action_one(tmp_dir):
                flag_action = True
                message_action = ""
                try:
                    self.write_test_files(test_file_to_be_written,tmp_dir)
                    
                    # test valid scenario
                    result = rename_file(
                        os.path.join(tmp_dir, test_files[0][0]),
                        os.path.join(tmp_dir, test_files[0][1]),
                    )
                    result_file_exist = file_exist(os.path.join(tmp_dir, test_files[0][1]))
                    message_action = (
                        "rename result: {} vs expected result: {} vs file check result: {}".format(
                            result, True, result_file_exist
                        )
                    )
                    assert result == True
                    assert result == result_file_exist

                    result = rename_file(
                        os.path.join(tmp_dir, test_files[1][0]),
                        os.path.join(tmp_dir, test_files[1][1]),
                    )
                    message_action = message_action + "\n" + " {} vs {}".format(result, False)
                    assert result == False

                    result = rename_file(
                        os.path.join(tmp_dir, test_files[2][0]),
                        os.path.join(tmp_dir, test_files[2][1]),
                    )
                    message_action = message_action + "\n" + " {} vs {}".format(result, False)
                    assert result == False

                    # check non existing source file
                    result = rename_file(
                        os.path.join(tmp_dir, "not here.txt"),
                        os.path.join(tmp_dir, test_files[2][1]),
                    )
                    message_action = message_action + "\n" + " {} vs {}".format(result, False)
                    assert result == False

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
