"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains revit sheet views report header tests . 
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
from duHast.Revit.Views.Reporting.views_report_header import get_sheets_report_headers
from duHast.Utilities import result as res


class GetSheetReportHeaders(revit_test.RevitTest):
    def __init__(self, doc):
        # store document in base class
        super(GetSheetReportHeaders, self).__init__(
            doc=doc, test_name="get_sheets_report_headers"
        )

    def test(self):
        """
        get sheets report header test

        :param doc: Current Revit model document.
        :type doc: Autodesk.Revit.DB.Document
        :param test_name: The test name.
        :type test_name: str

        :return:
            Result class instance.
                - .result = True if sheet reprt headers where retrieved successfully, otherwise False
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
            result = get_sheets_report_headers(self.document)
            expected_result = [
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
