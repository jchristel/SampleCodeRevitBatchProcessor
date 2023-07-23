"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains directory date stamp tests . 
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
from datetime import datetime

from duHast.Utilities.date_stamps import get_file_date_stamp, get_date_stamped_file_name


class GetDateStampFile(test.Test):
    def __init__(self):
        # store document in base class
        super(GetDateStampFile, self).__init__(test_name = "get_file_date_stamp")

    def test(self):
        """
        get_date_stamped_file_name() test

        :return: True if all tests pass, otherwise False
        :rtype: _bool
        """

        flag = True
        message = "-"
        try:
            revit_file_path = "C:/Users/User/Documents/RevitFile.rvt"
            file_extension = ".txt"
            file_suffix = "_backup"

            date_stamp = get_file_date_stamp()
            result = date_stamp + "_RevitFile_backup.txt"

            # Call the function to get the actual output
            expected_result = get_date_stamped_file_name(
                revit_file_path, file_extension, file_suffix
            )
            message = " {} vs {}".format(result, expected_result)

            # Assert the actual output matches the expected output
            assert expected_result == result
        except Exception as e:
            print(
                "An exception occurred in function test_get_date_stamped_file_name {}".format(
                    e
                )
            )
            flag = False
        return flag, message
