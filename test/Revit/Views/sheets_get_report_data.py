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

from test.Revit.TestUtils import revit_test
from duHast.Revit.Views.Reporting.sheets_report import get_sheet_report_data
from duHast.Utilities import result as res

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
                [
                    REVIT_TEST_FILE_NAME,
                    "21924",
                    "Independent",
                    "None",
                    "None",
                    "Invalid storage type: (NONE)",
                    "No",
                    "None",
                    "None",
                    "None",
                    "None",
                    "None",
                    "C:\\Users\\jchristel\\Documents\\GitHub\\SampleCodeRevitBatchProcessor\\test\\_rbp_flow\\_sampleFiles\\Revit_2022.rvt",
                    "Approver",
                    "Designer",
                    "Checker",
                    "Author",
                    " ",
                    "SPLASH",
                    "SPLASH",
                    "None",
                    "SPLASH",
                    "None",
                    "21928",
                    "Yes",
                    "Invalid storage type: (NONE)",
                    "-1",
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
