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
# BSD License
# Copyright © 2023, Jan Christel
# All rights reserved.

# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

# - Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# - Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# - Neither the name of Jan Christel nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
#
# This software is provided by Jan Christel "as is" and any express or implied warranties, including, but not limited to, the implied warranties of merchantability and fitness for a particular purpose are disclaimed. 
# In no event shall Jan Christel be liable for any direct, indirect, incidental, special, exemplary, or consequential damages (including, but not limited to, procurement of substitute goods or services; loss of use, data, or profits; 
# or business interruption) however caused and on any theory of liability, whether in contract, strict liability, or tort (including negligence or otherwise) arising in any way out of the use of this software, even if advised of the possibility of such damage.
#
#
#

from test.Revit.TestUtils import revit_test
from duHast.Revit.Views.Reporting.views_report import get_views_report_data_filtered
from duHast.Utilities.Objects import result as res

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
                {
                    "HOSTFILE": REVIT_TEST_FILE_NAME,
                    "Id": "970427",
                    "View Name": "Level 00",
                    "View Template": "-1",
                    "Title on Sheet": "None",
                },
                {
                    "HOSTFILE": REVIT_TEST_FILE_NAME,
                    "Id": "972024",
                    "View Name": "Export Model",
                    "View Template": "-1",
                    "Title on Sheet": "None",
                },
                {
                    "HOSTFILE": REVIT_TEST_FILE_NAME,
                    "Id": "21930",
                    "View Name": "TEST",
                    "View Template": "-1",
                    "Title on Sheet": "None",
                },
                {
                    "HOSTFILE": REVIT_TEST_FILE_NAME,
                    "Id": "970637",
                    "View Name": "Section - Level Test",
                    "View Template": "-1",
                    "Title on Sheet": "None",
                },
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
