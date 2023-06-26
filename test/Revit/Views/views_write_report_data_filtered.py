"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains revit views report data tests . 
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
from duHast.Revit.Views.Reporting.views_report import write_view_data_by_property_names
from duHast.Utilities.Objects import result as res

from test.Revit.Views.views_report import (
    REVIT_TEST_FILE_NAME,
    OUTPUT_FILE_NAME,
    VIEW_DATA_FILTERS,
)


class WriteViewReportDataFiltered(revit_test.RevitTest):
    def __init__(self, doc):
        # store document in base class
        super(WriteViewReportDataFiltered, self).__init__(
            doc=doc,
            test_name="write_view_data_by_property_names",
            requires_temp_dir=True,
        )

    def test(self):
        """
        Write view data with property filter test.

        :param doc: Current Revit model document.
        :type doc: Autodesk.Revit.DB.Document
        :param test_name: The test name.
        :type test_name: str

        :return:
            Result class instance.
                - .result = True if views report data was written successfully, otherwise False
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
            result = write_view_data_by_property_names(
                self.document,
                self.get_full_file_path(OUTPUT_FILE_NAME),
                REVIT_TEST_FILE_NAME,
                VIEW_DATA_FILTERS,
            )
            return_value.append_message(
                " file written: {} to: {}".format(result.status, result.message)
            )
            # check file was written
            assert result.status == True
            # double check...
            expected_result_file_read = [
                ["HOSTFILE", "Id", "View Name", "Title on Sheet", "View Template"],
                [REVIT_TEST_FILE_NAME, "21930", "TEST", "None", "-1"],
                [REVIT_TEST_FILE_NAME, "970427", "Level 00", "None", "-1"],
                [REVIT_TEST_FILE_NAME, "970637", "Section - Level Test", "None", "-1"],
                [REVIT_TEST_FILE_NAME, "972024", "Export Model", "None", "-1"],
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
