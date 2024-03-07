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
from duHast.Revit.Views.Reporting.views_report import get_views_report_data
from duHast.Utilities.Objects import result as res

from test.Revit.Views.views_report import REVIT_TEST_FILE_NAME


class GetViewReportData(revit_test.RevitTest):
    def __init__(self, doc):
        # store document in base class
        super(GetViewReportData, self).__init__(
            doc=doc, test_name="get_views_report_data"
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
                - .status True if view report data was retrieved successfully, otherwise False
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
            result = get_views_report_data(self.document, REVIT_TEST_FILE_NAME)
            expected_result = [
                {
                    "Default Analysis Display Style": "-1",
                    "Graphic Display Options": "Invalid storage type: (NONE)",
                    "Show Hidden Lines": "By Discipline",
                    "Associated Level": "Level 00",
                    "Phase": "3",
                    "Range: Top Level": "-1",
                    "Scope Box": "-1",
                    "View Type": "None",
                    "Sun Path": "No",
                    "Building": "None",
                    "Color Scheme": "Invalid storage type: (NONE)",
                    "HOSTFILE":REVIT_TEST_FILE_NAME,
                    "Crop Region Visible": "No",
                    "Visibility/Graphics Overrides": "Invalid storage type: (NONE)",
                    "Design Stage": "None",
                    "Range: Base Level": "-1",
                    "Id": "970427",
                    "Scale Value    1:": "100",
                    "Dependency": "Independent",
                    "Discipline": "Architectural",
                    "View Name": "Level 00",
                    "Title on Sheet": "None",
                    "Visible In Option": "-1",
                    "Underlay Orientation": "Look down",
                    "Depth Clipping": "None",
                    "Referencing Sheet": "None",
                    "None": "970435",
                    "View Range": "Invalid storage type: (NONE)",
                    "Phase Filter": "2029",
                    "Orientation": "Project North",
                    "Wall Join Display": "Clean all wall joins",
                    "Referencing Detail": "None",
                    "View Scale": " 1 : 100",
                    "Parts Visibility": "Show Original",
                    "View Template": "-1",
                    "Color Scheme Location": "Background",
                    "Annotation Crop": "No",
                    "Display Model": "Normal",
                    "Detail Level": "Coarse",
                    "Crop View": "No",
                },
                {
                    "Default Analysis Display Style": "-1",
                    "Graphic Display Options": "Invalid storage type: (NONE)",
                    "Show Hidden Lines": "By Discipline",
                    "Far Clip Offset": "304800",
                    "Phase": "3",
                    "Projection Mode": "Orthographic",
                    "Scope Box": "-1",
                    "View Type": "None",
                    "Sun Path": "No",
                    "Section Box": "No",
                    "Building": "None",
                    "Rendering Settings": "Invalid storage type: (NONE)",
                    "HOSTFILE": REVIT_TEST_FILE_NAME,
                    "Locked Orientation": "No",
                    "Camera Position": "Adjusting",
                    "Far Clip Active": "No",
                    "Crop Region Visible": "No",
                    "Visibility/Graphics Overrides": "Invalid storage type: (NONE)",
                    "Design Stage": "None",
                    "Id": "972024",
                    "Scale Value    1:": "100",
                    "Dependency": "Independent",
                    "Discipline": "Architectural",
                    "Show Grids": "Invalid storage type: (NONE)",
                    "View Name": "Export Model",
                    "Title on Sheet": "None",
                    "Visible In Option": "-1",
                    "None": "-1",
                    "Phase Filter": "2029",
                    "View Scale": " 1 : 100",
                    "Parts Visibility": "Show Original",
                    "View Template": "-1",
                    "Annotation Crop": "No",
                    "Detail Level": "Medium",
                    "Crop View": "No",
                    "Target Elevation": "1195",
                    "Eye Elevation": "13275",
                },
                {
                    "Detail Level": "Medium",
                    "View Template": "-1",
                    "HOSTFILE": REVIT_TEST_FILE_NAME,
                    "View Type": "TEST",
                    "None": "21935",
                    "Id": "21930",
                    "View Scale": " 1 : 1",
                    "Dependency": "Independent",
                    "Discipline": "Architectural",
                    "View Name": "TEST",
                    "Visual Style": "Hidden Line",
                    "Referencing Sheet": "None",
                    "Title on Sheet": "None",
                    "Referencing Detail": "None",
                    "Scale Value    1:": "1",
                    "Visibility/Graphics Overrides": "Invalid storage type: (NONE)",
                    "Design Stage": "TEST",
                    "Building": "None",
                },
                {
                    "Color Scheme": "Invalid storage type: (NONE)",
                    "Detail Level": "Coarse",
                    "Annotation Crop": "No",
                    "View Template": "-1",
                    "HOSTFILE": REVIT_TEST_FILE_NAME,
                    "View Type": "None",
                    "Far Clip Offset": "3048",
                    "Phase Filter": "2029",
                    "None": "970644",
                    "Id": "970637",
                    "Color Scheme Location": "Background",
                    "View Scale": " 1 : 100",
                    "Dependency": "Independent",
                    "Parts Visibility": "Show Original",
                    "Graphic Display Options": "Invalid storage type: (NONE)",
                    "Far Clipping": "None",
                    "Discipline": "Architectural",
                    "Show Hidden Lines": "By Discipline",
                    "Display Model": "Normal",
                    "View Name": "Section - Level Test",
                    "Default Analysis Display Style": "-1",
                    "Phase": "3",
                    "Sun Path": "No",
                    "Referencing Sheet": "None",
                    "Title on Sheet": "None",
                    "Referencing Detail": "None",
                    "Hide at scales coarser than": " 1 : 100",
                    "Visible In Option": "-1",
                    "Scope Box": "-1",
                    "Scale Value    1:": "100",
                    "Crop View": "Yes",
                    "Crop Region Visible": "Yes",
                    "Visibility/Graphics Overrides": "Invalid storage type: (NONE)",
                    "Design Stage": "None",
                    "Building": "None",
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
