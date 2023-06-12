"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains revit independent report data tests . 
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
from duHast.Revit.Annotation.Reporting.tags_independent_report import get_tag_instances_report_data
from duHast.Utilities import result as res

from test.Revit.Annotation.annotations_report import REVIT_INDEPENDENT_TAG_TEST_FILE_NAME


class GetIndependentTagReportData(revit_test.RevitTest):
    def __init__(self, doc):
        # store document in base class
        super(GetIndependentTagReportData, self).__init__(
            doc=doc, test_name="get_tag_instances_report_data"
        )

    def test(self):
        """
        get_tag_instances_report_data test

        :param doc: Current Revit model document.
        :type doc: Autodesk.Revit.DB.Document
        :param test_name: The test name.
        :type test_name: str

        :return:
            Result class instance.
                - .result = True if tag instance data was retrieved successfully, otherwise False
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
            # get instance report data
            result = get_tag_instances_report_data(self.document, REVIT_INDEPENDENT_TAG_TEST_FILE_NAME)
            expected_result = [
                [
                    REVIT_INDEPENDENT_TAG_TEST_FILE_NAME,
                    "1641",
                    "Wall 1",
                    "Structure",
                    "200.0",
                    "N/A",
                    "N/A",
                ],
                [
                    REVIT_INDEPENDENT_TAG_TEST_FILE_NAME,
                    "1642",
                    "Curtain Wall 1",
                    "no layers - in place family or curtain wall",
                    "0.0",
                    "NA",
                    "NA",
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
