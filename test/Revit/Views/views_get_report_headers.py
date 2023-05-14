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

from test.Revit.TestUtilis import revit_test
from duHast.Revit.Views.Reporting.views_report_header import get_views_report_headers
from duHast.Utilities import result as res


class GetViewReportHeaders(revit_test.RevitTest):
    def __init__(self, doc):
        # store document in base class
        super(GetViewReportHeaders, self).__init__(doc=doc)

    def test(self):
        """
        get views report header test

        :param doc: Current Revit model document.
        :type doc: Autodesk.Revit.DB.Document
        :return: True if tested successfully, otherwise False
        :rtype: Boolean
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
            return_value.append_message = " result: {} \n expected: {} ".format(
                result, expected_result
            )
            assert sorted(result) == sorted(expected_result)

        except Exception as e:
            return_value.update_sep(
                False,
                "An exception occurred in function test_get_views_report_headers {}".format(
                    e
                ),
            )

        return return_value
