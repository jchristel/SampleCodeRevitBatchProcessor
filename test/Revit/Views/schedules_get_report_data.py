"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains revit schedule report data tests . 
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
from duHast.Revit.Views.Reporting.schedules_report import get_schedules_report_data
from duHast.Utilities.Objects import result as res

from test.Revit.Views.schedules_report import REVIT_TEST_FILE_NAME


class GetScheduleReportData(revit_test.RevitTest):
    def __init__(self, doc):
        # store document in base class
        super(GetScheduleReportData, self).__init__(
            doc=doc, test_name="get schedules report data"
        )

    def test(self):
        """
        get views report data test

        :param doc: Current Revit model document.
        :type doc: Autodesk.Revit.DB.Document
        :param test_name: The test name.
        :type test_name: str

        :return:
            Result class instance.
                - .result = True if schedule report data was retrieved successfully, otherwise False
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
            result = get_schedules_report_data(self.document, REVIT_TEST_FILE_NAME)
            expected_result = []
            if self.revit_version_number == 2022:
                expected_result = [
                    {
                        "View Template": "-1",
                        "HOSTFILE": REVIT_TEST_FILE_NAME,
                        "Phase Filter": "2029",
                        "None": "-1",
                        "Id": "970420",
                        "Dependency": "Independent",
                        "Filter": "Invalid storage type: (NONE)",
                        "Sorting/Grouping": "Invalid storage type: (NONE)",
                        "View Name": "Wall Schedule",
                        "Phase": "3",
                        "Formatting": "Invalid storage type: (NONE)",
                        "Visibility/Graphics Overrides": "Invalid storage type: (NONE)",
                        "Design Stage": "None",
                        "Fields": "Invalid storage type: (NONE)",
                        "Appearance": "Invalid storage type: (NONE)",
                    }
                ]
            elif self.revit_version_number > 2022:
                expected_result = [
                    {
                        "View Template": "-1",
                        "HOSTFILE": REVIT_TEST_FILE_NAME,
                        "Phase Filter": "2029",
                        "None": "-1",
                        "Id": "970420",
                        "Dependency": "Independent",
                        "Filter": "Invalid storage type: (NONE)",
                        "Sorting/Grouping": "Invalid storage type: (NONE)",
                        "View Name": "Wall Schedule",
                        "Phase": "3",
                        "Formatting": "Invalid storage type: (NONE)",
                        "Visibility/Graphics Overrides": "Invalid storage type: (NONE)",
                        "Design Stage": "None",
                        "Fields": "Invalid storage type: (NONE)",
                        "Appearance": "Invalid storage type: (NONE)",
                        "Export to IFC": "By Type", #2023 onwards
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
