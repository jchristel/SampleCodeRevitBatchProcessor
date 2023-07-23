"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains file name without extension tests . 
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
    get_file_name_without_ext,
)


class FileNameWithoutExtension(test.Test):
    def __init__(self):
        # store document in base class
        super(FileNameWithoutExtension, self).__init__(
            test_name="file_name_without_ext"
        )

    def test(self):
        """
        get_file_name_without_ext test

        :param tmpdir: temp directory
        :type tmpdir: str
        :return: True if all tests past, otherwise False. A message containing results.
        :rtype: bool, str
        """

        flag = True
        message = "-"
        try:
            file_path = "/path/to/example_file.txt"
            expected_result = "example_file"
            result = get_file_name_without_ext(file_path)
            message = " {} vs {}".format(result, expected_result)
            assert result == expected_result

            file_path = "/path/to/another_example_file.csv"
            expected_result = "another_example_file"
            result = get_file_name_without_ext(file_path)
            message = message + "\n" + (" {} vs {}".format(result, expected_result))
            assert result == expected_result

            file_path = "\\path/to/another_example_file.csv"
            expected_result = "another_example_file"
            result = get_file_name_without_ext(file_path)
            message = message + "\n" + (" {} vs {}".format(result, expected_result))
            assert result == expected_result

            file_path = "C:\path/to some/another_example_file.csv"
            expected_result = "another_example_file"
            result = get_file_name_without_ext(file_path)
            message = message + "\n" + (" {} vs {}".format(result, expected_result))
            assert result == expected_result

            file_path = "\\path/to/another_example_file.0001.csv"
            expected_result = "another_example_file.0001"
            result = get_file_name_without_ext(file_path)
            message = message + "\n" + (" {} vs {}".format(result, expected_result))
            assert result == expected_result

            file_path = "example_file.docx"
            expected_result = "example_file"
            result = get_file_name_without_ext(file_path)
            message = message + "\n" + (" {} vs {}".format(result, expected_result))
            assert result == expected_result

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
