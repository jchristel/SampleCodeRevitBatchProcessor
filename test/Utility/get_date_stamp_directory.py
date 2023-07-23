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
# - Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
#
# This software is provided by the copyright holder "as is" and any express or implied warranties, including, but not limited to, the implied warranties of merchantability and fitness for a particular purpose are disclaimed. 
# In no event shall the copyright holder be liable for any direct, indirect, incidental, special, exemplary, or consequential damages (including, but not limited to, procurement of substitute goods or services; loss of use, data, or profits; 
# or business interruption) however caused and on any theory of liability, whether in contract, strict liability, or tort (including negligence or otherwise) arising in any way out of the use of this software, even if advised of the possibility of such damage.
#
#
#

from test.utils import test
from datetime import datetime

from duHast.Utilities.date_stamps import get_folder_date_stamp


class GetDateStampDirectory(test.Test):
    def __init__(self):
        # store document in base class
        super(GetDateStampDirectory, self).__init__(test_name = "get_folder_date_stamp")

    def test(self):
        """
        _summary_

        :return: True if all tests pass, otherwise False
        :rtype: _bool
        """

        flag = True
        message = "-"
        try:
            # Test with default format
            expected_result = datetime.now().strftime("%Y%m%d")
            result = get_folder_date_stamp()
            message = " {} vs {}".format(result, expected_result)
            assert result == expected_result

            # Test with a different format
            expected_result = datetime.now().strftime("%Y-%m-%d")
            result = get_folder_date_stamp("%Y-%m-%d")
            message = message + "\n" + (" {} vs {}".format(result, expected_result))
            assert result == expected_result

            # Test with a invalid format
            expected_result = "invalid-format"
            result = get_folder_date_stamp("invalid-format")
            message = message + "\n" + (" {} vs {}".format(result, expected_result))
            assert result == expected_result

        except Exception as e:
            message = (
                message
                + "\n"
                + (
                    "An exception occurred in function get_folder_date_stamp {}".format(
                        e
                    )
                )
            )
            flag = False
        return flag, message
