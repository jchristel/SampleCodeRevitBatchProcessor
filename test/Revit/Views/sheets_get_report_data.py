"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains revit sheet report data tests . 
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

import os
from test.Revit.TestUtils import revit_test
from duHast.Revit.Views.Reporting.sheets_report import get_sheet_report_data
from duHast.Utilities.Objects import result as res

from test.Revit.Views.sheets_report import REVIT_TEST_FILE_NAME


class GetSheetReportData(revit_test.RevitTest):
    def __init__(self, doc):
        # store document in base class
        super(GetSheetReportData, self).__init__(
            doc=doc, test_name="get sheet report data "
        )

    def test(self):
        """
        get sheet report data  test

        :param doc: Current Revit model document.
        :type doc: Autodesk.Revit.DB.Document
        :param test_name: The test name.
        :type test_name: str

        :return:
            Result class instance.
                - .status True if sheet report data was retrieved successfully, otherwise False
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
            # get sheet report headers
            result = get_sheet_report_data(self.document, REVIT_TEST_FILE_NAME)

            expected_result = [
                {
                    "Current Revision Issued By": "None",
                    "File Path": os.path.join(
                        "C:\\Users\\jchristel\\dev\\SampleCodeRevitBatchProcessor\\test\\_rbp_flow\\_sampleFiles",
                        self.file_name,
                    ),
                    "Designed By": "Designer",
                    "HOSTFILE": REVIT_TEST_FILE_NAME,
                    "Current Revision Issued To": "None",
                    "View Type": "None",
                    "None": "21928",
                    "Appears In Sheet List": "Yes",
                    "Id": "21924",
                    "Sheet Issue Date": "None",
                    "Dependency": "Independent",
                    "Scale": " ",
                    "Sheet Number": "SPLASH",
                    "Approved By": "Approver",
                    "Current Revision Date": "None",
                    "Referencing Detail": "None",
                    "Referencing Sheet": "None",
                    "Current Revision Description": "None",
                    "Current Revision": "None",
                    "Current Revision Issued": "No",
                    "Checked By": "Checker",
                    "Sheet Name": "SPLASH",
                    "Guide Grid": "-1",
                    "Drawn By": "Author",
                    "Visibility/Graphics Overrides": "Invalid storage type: (NONE)",
                    "Revisions on Sheet": "Invalid storage type: (NONE)",
                    "Design Stage": "SPLASH",
                }
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
