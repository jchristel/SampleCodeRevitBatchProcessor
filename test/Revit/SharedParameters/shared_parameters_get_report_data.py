"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains revit shared report data tests . 
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

from test.Revit.TestUtils import revit_test
from duHast.Revit.SharedParameters.Reporting.shared_parameter_report import (
    get_shared_parameter_report_data,
)
from duHast.Utilities.Objects import result as res

from test.Revit.SharedParameters.shared_parameters_report import REVIT_TEST_FILE_NAME


class GetSharedParameterReportData(revit_test.RevitTest):
    def __init__(self, doc):
        # store document in base class
        super(GetSharedParameterReportData, self).__init__(
            doc=doc, test_name="get_shared_parameter_report_data"
        )

    def test(self):
        """
        get shared parameter report data test

        :param doc: Current Revit model document.
        :type doc: Autodesk.Revit.DB.Document
        :param test_name: The test name.
        :type test_name: str

        :return:
            Result class instance.
                - .status True if wall data was retrieved successfully, otherwise False
                - .message will contain result(s) vs expected result(s)
                - . result (empty list)

                on exception:

                - .result Will be False
                - .message will contain exception message.
                - . result (empty list)
        :rtype: :class:`.Result`
        """

        return_value = res.Result()
        try:
            # get wall report headers
            result = get_shared_parameter_report_data(
                self.document, REVIT_TEST_FILE_NAME
            )
            expected_result = [
                [
                    REVIT_TEST_FILE_NAME,
                    "2fb72b30-386f-4b5d-a2b1-e99e0f55921f",
                    "970451",
                    "test_length",
                    "['Walls']",
                ]
            ]
            return_value.append_message(
                " result: {} \n expected: {} ".format(result, expected_result)
            )
            assert sorted(result) == sorted(expected_result)

        except Exception as e:
            return_value.update_sep(
                False,
                "An exception occurred in function {}: {}".format(self.test_name, e),
            )

        return return_value
