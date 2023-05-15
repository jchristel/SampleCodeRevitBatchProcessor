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

from test.Revit.TestUtilis import revit_test
from duHast.Revit.Views.Reporting.views_report import get_views_report_data
from duHast.Utilities import result as res

from test.Revit.Views.views_report import REVIT_TEST_FILE_NAME


class GetViewReportData(revit_test.RevitTest):
    def __init__(self, doc):
        # store document in base class
        super(GetViewReportData, self).__init__(doc=doc)

    def test(self):
        """
        get views report data test

        :param doc: Current Revit model document.
        :type doc: Autodesk.Revit.DB.Document
        :return: True if tested successfully, otherwise False
        :rtype: Boolean
        """

        return_value = res.Result()
        try:
            # get sheet report headers
            result = get_views_report_data(self.document, REVIT_TEST_FILE_NAME)
            expected_result = [
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
                    "21930",
                    "-1",
                    "TEST",
                    "Independent",
                    "None",
                    " 1 : 1",
                    "1",
                    "Medium",
                    "None",
                    "None",
                    "Invalid storage type: (NONE)",
                    "Architectural",
                    "TEST",
                    "None",
                    "TEST",
                    "21935",
                    "Hidden Line",
                ],
            ]
            return_value.append_message = " result: {} \n expected: {} ".format(
                result, expected_result
            )
            assert sorted(result) == sorted(expected_result)

        except Exception as e:
            return_value.update_sep(
                False,
                "An exception occurred in function test_get_views_report_data {}".format(
                    e
                ),
            )

        return return_value