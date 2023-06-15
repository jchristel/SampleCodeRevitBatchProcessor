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
from duHast.Revit.Views.Reporting.views_report import write_views_data
from duHast.Utilities import result as res

from test.Revit.Views.views_report import REVIT_TEST_FILE_NAME, OUTPUT_FILE_NAME


class WriteViewReportData(revit_test.RevitTest):
    def __init__(self, doc):
        # store document in base class
        super(WriteViewReportData, self).__init__(
            doc=doc, test_name="write_views_data", requires_temp_dir=True
        )

    def test(self):
        """
        Write all view data test.

        :param doc: Current Revit model document.
        :type doc: Autodesk.Revit.DB.Document
        :param test_name: The test name.
        :type test_name: str

        :return:
            Result class instance.
                - .result = True if view report data was written to file successfully, otherwise False
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
            result = write_views_data(
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
                    "View Template",
                    "View Name",
                    "Dependency",
                    "Title on Sheet",
                    "View Scale",
                    "Scale Value    1:",
                    "Display Model",
                    "Detail Level",
                    "Parts Visibility",
                    "Referencing Sheet",
                    "Referencing Detail",
                    "Crop View",
                    "Crop Region Visible",
                    "Annotation Crop",
                    "Visibility/Graphics Overrides",
                    "Graphic Display Options",
                    "Range: Base Level",
                    "Range: Top Level",
                    "Underlay Orientation",
                    "View Range",
                    "Associated Level",
                    "Orientation",
                    "Phase Filter",
                    "Phase",
                    "Wall Join Display",
                    "Scope Box",
                    "Discipline",
                    "Show Hidden Lines",
                    "Color Scheme Location",
                    "Color Scheme",
                    "Default Analysis Display Style",
                    "Depth Clipping",
                    "Visible In Option",
                    "Design Stage",
                    "Building",
                    "View Type",
                    "None",
                    "Sun Path",
                ],
                [
                    REVIT_TEST_FILE_NAME,
                    "21930",
                    "-1",
                    "TEST",
                    "Independent",
                    "None",
                    " 1 : 1",
                    "1",
                    "Property does not exist on element.",
                    "Medium",
                    "Property does not exist on element.",
                    "None",
                    "None",
                    "Property does not exist on element.",
                    "Property does not exist on element.",
                    "Property does not exist on element.",
                    "Invalid storage type: (NONE)",
                    "Property does not exist on element.",
                    "Property does not exist on element.",
                    "Property does not exist on element.",
                    "Property does not exist on element.",
                    "Property does not exist on element.",
                    "Property does not exist on element.",
                    "Property does not exist on element.",
                    "Property does not exist on element.",
                    "Property does not exist on element.",
                    "Property does not exist on element.",
                    "Property does not exist on element.",
                    "Architectural",
                    "Property does not exist on element.",
                    "Property does not exist on element.",
                    "Property does not exist on element.",
                    "Property does not exist on element.",
                    "Property does not exist on element.",
                    "Property does not exist on element.",
                    "TEST",
                    "None",
                    "TEST",
                    "21935",
                    "Property does not exist on element.",
                ],
                [
                    REVIT_TEST_FILE_NAME,
                    "970427",
                    "-1",
                    "Level 00",
                    "Independent",
                    "None",
                    " 1 : 100",
                    "100",
                    "Normal",
                    "Coarse",
                    "Show Original",
                    "None",
                    "None",
                    "No",
                    "No",
                    "No",
                    "Invalid storage type: (NONE)",
                    "Invalid storage type: (NONE)",
                    "-1",
                    "-1",
                    "Look down",
                    "Invalid storage type: (NONE)",
                    "Level 00",
                    "Project North",
                    "2029",
                    "3",
                    "Clean all wall joins",
                    "-1",
                    "Architectural",
                    "By Discipline",
                    "Background",
                    "Invalid storage type: (NONE)",
                    "-1",
                    "None",
                    "-1",
                    "None",
                    "None",
                    "None",
                    "970435",
                    "No",
                ],
                [
                    REVIT_TEST_FILE_NAME,
                    "970637",
                    "-1",
                    "Section - Level Test",
                    "Independent",
                    "None",
                    " 1 : 100",
                    "100",
                    "Normal",
                    "Coarse",
                    "Show Original",
                    "None",
                    "None",
                    "Yes",
                    "Yes",
                    "No",
                    "Invalid storage type: (NONE)",
                    "Invalid storage type: (NONE)",
                    "Property does not exist on element.",
                    "Property does not exist on element.",
                    "Property does not exist on element.",
                    "Property does not exist on element.",
                    "Property does not exist on element.",
                    "Property does not exist on element.",
                    "2029",
                    "3",
                    "Property does not exist on element.",
                    "-1",
                    "Architectural",
                    "By Discipline",
                    "Background",
                    "Invalid storage type: (NONE)",
                    "-1",
                    "Property does not exist on element.",
                    "-1",
                    "None",
                    "None",
                    "None",
                    "970644",
                    "No",
                ],
                [
                    REVIT_TEST_FILE_NAME,
                    "972024",
                    "-1",
                    "Export Model",
                    "Independent",
                    "None",
                    " 1 : 100",
                    "100",
                    "Property does not exist on element.",
                    "Medium",
                    "Show Original",
                    "Property does not exist on element.",
                    "Property does not exist on element.",
                    "No",
                    "No",
                    "No",
                    "Invalid storage type: (NONE)",
                    "Invalid storage type: (NONE)",
                    "Property does not exist on element.",
                    "Property does not exist on element.",
                    "Property does not exist on element.",
                    "Property does not exist on element.",
                    "Property does not exist on element.",
                    "Property does not exist on element.",
                    "2029",
                    "3",
                    "Property does not exist on element.",
                    "-1",
                    "Architectural",
                    "By Discipline",
                    "Property does not exist on element.",
                    "Property does not exist on element.",
                    "-1",
                    "Property does not exist on element.",
                    "-1",
                    "None",
                    "None",
                    "None",
                    "-1",
                    "No",
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
