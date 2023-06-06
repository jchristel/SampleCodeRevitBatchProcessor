"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains revit views report data filtered tests . 
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
from duHast.Revit.Views.Reporting.views_report import get_views_report_data_filtered
from duHast.Utilities import result as res

from test.Revit.Views.views_report import REVIT_TEST_FILE_NAME, VIEW_DATA_FILTERS


class GetViewReportDataFiltered(revit_test.RevitTest):
    def __init__(self, doc):
        # store document in base class
        super(GetViewReportDataFiltered, self).__init__(
            doc=doc, test_name="get_views_report_data_filtered"
        )

    def test(self):
        """
        get views report data filtered test

        :param doc: Current Revit model document.
        :type doc: Autodesk.Revit.DB.Document
        :param test_name: The test name.
        :type test_name: str

        :return:
            Result class instance.
                - .result = True if view filtered view report data where retrieved was retrieved successfully, otherwise False
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
            result = get_views_report_data_filtered(
                self.document, REVIT_TEST_FILE_NAME, VIEW_DATA_FILTERS
            )
            expected_result = [
                [REVIT_TEST_FILE_NAME, "970427", "Level 00", "None", "-1"],
                [REVIT_TEST_FILE_NAME, "21930", "TEST", "None", "-1"],
                [REVIT_TEST_FILE_NAME, "970637", "Section - Level Test", "None", "-1"],
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
