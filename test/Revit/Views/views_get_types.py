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
from duHast.Revit.Views.views import get_view_types
from duHast.Utilities import result as res

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
                - .result = True if revision sequence was changed successfully, otherwise False
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
