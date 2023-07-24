"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains revit views report header tests . 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2023, Jan Christel
# All rights reserved.

# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

# - Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# - Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# - Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
#
# This software is provided by the copyright holder "as is" and any express or implied warranties, including, but not limited to, the implied warranties of merchantability and fitness for a particular purpose are disclaimed. 
# In no event shall the copyright holder be liable for any direct, indirect, incidental, special, exemplary, or consequential damages (including, but not limited to, procurement of substitute goods or services; loss of use, data, or profits; 
# or business interruption) however caused and on any theory of liability, whether in contract, strict liability, or tort (including negligence or otherwise) arising in any way out of the use of this software, even if advised of the possibility of such damage.
#
#
#

from test.Revit.TestUtils import revit_test
from duHast.Revit.Views.Reporting.views_report_header import get_views_report_headers
from duHast.Utilities.Objects import result as res


class GetViewReportHeaders(revit_test.RevitTest):
    def __init__(self, doc):
        # store document in base class
        super(GetViewReportHeaders, self).__init__(
            doc=doc, test_name="get_views_report_headers"
        )

    def test(self):
        """
        get views report header test

        :param doc: Current Revit model document.
        :type doc: Autodesk.Revit.DB.Document
        :param test_name: The test name.
        :type test_name: str

        :return:
            Result class instance.
                - .result = True if views report headers where retrieved successfully, otherwise False
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
            result = get_views_report_headers(self.document)
            expected_result = [
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
