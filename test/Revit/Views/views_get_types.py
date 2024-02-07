"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains revit view types tests . 
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
from duHast.Revit.Views.views import get_view_types
from duHast.Utilities.Objects import result as res

# import Autodesk
import Autodesk.Revit.DB as rdb


class GetViewTypes(revit_test.RevitTest):
    def __init__(self, doc):
        # store document in base class
        super(GetViewTypes, self).__init__(doc=doc, test_name="get_view_types")

    def test(self):
        """
        test get view types

        :param doc: Current Revit model document.
        :type doc: Autodesk.Revit.DB.Document
        :param test_name: The test name.
        :type test_name: str

        :return:
            Result class instance.
                - .status True if view types where retrieved successfully, otherwise False
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
            result_col = get_view_types(self.document)
            expected_result = [
                ["Structural Plan", rdb.ViewFamily.StructuralPlan],
                ["3D View", rdb.ViewFamily.ThreeDimensional],
                ["Schedule", rdb.ViewFamily.Schedule],
                ["Sheet", rdb.ViewFamily.Sheet],
                ["Walkthrough", rdb.ViewFamily.Walkthrough],
                ["Rendering", rdb.ViewFamily.ImageView],
                ["Cost Report", rdb.ViewFamily.CostReport],
                ["Legend", rdb.ViewFamily.Legend],
                ["Loads Report", rdb.ViewFamily.LoadsReport],
                ["Pressure Loss Report", rdb.ViewFamily.PressureLossReport],
                ["Panel Schedule", rdb.ViewFamily.PanelSchedule],
                ["Graphical Column Schedule", rdb.ViewFamily.GraphicalColumnSchedule],
                ["STC & NOTES", rdb.ViewFamily.Drafting],
                ["RCP (B53 Series)", rdb.ViewFamily.CeilingPlan],
                ["Section (D Series)", rdb.ViewFamily.Section],
                ["Plan Site (A Series)", rdb.ViewFamily.FloorPlan],
                ["NLA", rdb.ViewFamily.AreaPlan],
                ["DETAIL INTERIOR (J SERIES)", rdb.ViewFamily.Detail],
                ["Elevation (C Series)", rdb.ViewFamily.Elevation],
                ["Analysis Report", rdb.ViewFamily.SystemsAnalysisReport],
            ]
            result = []
            for vt in result_col:
                result.append([rdb.Element.Name.GetValue(vt), vt.ViewFamily])
            return_value.append_message(
                " result: {} \n expected: {} ".format(
                    sorted(result), sorted(expected_result)
                )
            )
            assert sorted(result) == sorted(expected_result)

        except Exception as e:
            return_value.update_sep(
                False,
                "An exception occurred in function {}: {}".format(self.test_name, e),
            )

        return return_value
