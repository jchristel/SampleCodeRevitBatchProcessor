"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains revit independent report data header tests . 
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
from duHast.Revit.Annotation.Reporting.gen_annotations_instance_report_header import (
    get_report_header,
    REPORT_GENERIC_ANNOTATIONS_INSTANCE_HEADER,
    REPORT_GENERIC_ANNOTATIONS_INSTANCE_HEADER_2023,
)
from duHast.Revit.Common.revit_version import get_revit_version_number
from duHast.Utilities import result as res

from test.Revit.Annotation.annotations_report import (
    REVIT_INDEPENDENT_TAG_TEST_FILE_NAME,
)


class GetIndependentTagReportDataHeader(revit_test.RevitTest):
    def __init__(self, doc):
        # store document in base class
        super(GetIndependentTagReportDataHeader, self).__init__(
            doc=doc, test_name="get_tag_instances_get_report_header"
        )

    def test(self):
        """
        get_report_header test for independent tag instances

        :param doc: Current Revit model document.
        :type doc: Autodesk.Revit.DB.Document
        :param test_name: The test name.
        :type test_name: str

        :return:
            Result class instance.
                - .result = True if tag instance data headers was retrieved successfully, otherwise False
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
            result = get_report_header(self.document)
            expected_result_all = {
                2022: REPORT_GENERIC_ANNOTATIONS_INSTANCE_HEADER,
                2023: REPORT_GENERIC_ANNOTATIONS_INSTANCE_HEADER + REPORT_GENERIC_ANNOTATIONS_INSTANCE_HEADER_2023
            }
            # get the expected result based on Revit version
            expected_result = []
            if get_revit_version_number(self.document) <= 2022:
                expected_result = expected_result_all[2022]
            else:
                expected_result = expected_result_all[2023]

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
