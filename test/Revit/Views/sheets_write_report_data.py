"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains revit sheets report data tests . 
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
from duHast.Revit.Views.Reporting.sheets_report import write_sheet_data
from duHast.Utilities import result as res

from test.Revit.Views.sheets_report import REVIT_TEST_FILE_NAME, OUTPUT_FILE_NAME


class WriteSheetReportData(revit_test.RevitTest):
    def __init__(self, doc):
        # store document in base class
        super(WriteSheetReportData, self).__init__(
            doc=doc, test_name="Write all sheet data", requires_temp_dir=True
        )

    def test(self):
        """
        Write all sheet data test.

        :param doc: Current Revit model document.
        :type doc: Autodesk.Revit.DB.Document
        :param test_name: The test name.
        :type test_name: str

        :return:
            Result class instance.
                - .result = True if sheets report data was written to file successfully, otherwise False
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
            result = write_sheet_data(
                self.document,
                self.get_full_file_path(OUTPUT_FILE_NAME),
                REVIT_TEST_FILE_NAME,
            )
            return_value.append_message(
                " file written: {} to: {}".format(result.status, result.message)
            )
            # check file was written
            assert result.status == True
            # double check...
            expected_result_file_read = [
                [
                    "HOSTFILE",
                    "Id",
                    "Dependency",
                    "Referencing Sheet",
                    "Referencing Detail",
                    "Visibility/Graphics Overrides",
                    "Current Revision Issued",
                    "Current Revision Issued By",
                    "Current Revision Issued To",
                    "Current Revision Date",
                    "Current Revision Description",
                    "Current Revision",
                    "File Path",
                    "Approved By",
                    "Designed By",
                    "Checked By",
                    "Drawn By",
                    "Scale",
                    "Sheet Number",
                    "Sheet Name",
                    "Sheet Issue Date",
                    "Design Stage",
                    "View Type",
                    "None",
                    "Appears In Sheet List",
                    "Revisions on Sheet",
                    "Guide Grid",
                ],
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
                ],
            ]

            # check file content and perform temp directory clean up
            csv_check = self.test_csv_file(
                self.get_full_file_path(OUTPUT_FILE_NAME), expected_result_file_read
            )
            return_value.update(csv_check)

        except Exception as e:
            return_value.update_sep(
                False,
                "An exception occurred in function {}: {}".format(self.test_name, e),
            )
        finally:
            # clean up temp directory
            clean_up = self.clean_up()
            return_value.update_sep(
                clean_up,
                "Attempted to clean up temp directory with result: {}".format(clean_up),
            )

        return return_value
