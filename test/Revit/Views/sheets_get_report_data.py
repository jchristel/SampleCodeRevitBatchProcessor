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
                - .result = True if sheet report data was retrieved successfully, otherwise False
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
