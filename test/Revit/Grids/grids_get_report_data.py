"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains revit grids report data tests . 
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
from duHast.Revit.Grids.Reporting.grid_report_utils import get_grid_report_data
from duHast.Utilities.Objects import result as res

from test.Revit.Grids.grids_report import REVIT_TEST_FILE_NAME


class GetGridReportData(revit_test.RevitTest):
    def __init__(self, doc):
        # store document in base class
        super(GetGridReportData, self).__init__(
            doc=doc, test_name="get_grid_report_data"
        )

    def test(self):
        """
        get grid report data test

        :param doc: Current Revit model document.
        :type doc: Autodesk.Revit.DB.Document
        :param test_name: The test name.
        :type test_name: str

        :return:
            Result class instance.
                - .result = True if grid data was retrieved successfully, otherwise False
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
            # get grid report headers
            result = get_grid_report_data(self.document, REVIT_TEST_FILE_NAME)
            expected_result = [
                [
                    REVIT_TEST_FILE_NAME,
                    "224340",
                    "A",
                    "unknown",
                    "[9.28594923983e-14,57.4787559983,8.0]",
                    "[-1.39259773061e-14,-8.61998952334,-1.0]",
                ],
                [
                    REVIT_TEST_FILE_NAME,
                    "224438",
                    "01",
                    "unknown",
                    "[61.0698871087,3.46777487067e-14,8.0]",
                    "[-10.7328110722,-1.9732224956e-13,-1.0]",
                ],
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
