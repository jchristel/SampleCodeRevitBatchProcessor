"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains revit get view tests . 
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
from duHast.Revit.Views.views import get_views_in_model
from duHast.Utilities import result as res

# import Autodesk
import Autodesk.Revit.DB as rdb


class GetViews(revit_test.RevitTest):
    def __init__(self, doc):
        # store document in base class
        super(GetViews, self).__init__(doc=doc)

    def test(self):
        """
        get views in model test

        :param doc: Current Revit model document.
        :type doc: Autodesk.Revit.DB.Document
        :return: True if tested successfully, otherwise False
        :rtype: Boolean
        """

        return_value = res.Result()
        try:
            # set up a return all views filter
            def action(x):
                return True

            # get all views in model (only 1 in test model)
            result = get_views_in_model(self.document, action)

            return_value.append_message(
                " view name: {}, view type: {}, ".format(
                    result[0].Name, result[0].ViewType
                )
            )
            assert result[0].Name == "TEST"
            assert result[0].ViewType == rdb.ViewType.DraftingView

            return_value.append_message(
                " view name: {}, view type: {} ".format(
                    result[1].Name, result[1].ViewType
                )
            )
            assert result[1].ViewType == rdb.ViewType.Schedule
            assert result[1].Name == "Wall Schedule"

            return_value.append_message(
                " view name: {}, view type: {} ".format(
                    result[2].Name, result[2].ViewType
                )
            )

            assert result[2].ViewType == rdb.ViewType.FloorPlan
            assert result[2].Name == "Level 00"
            assert len(result) == 3

        except Exception as e:
            return_value.update_sep(
                False,
                "An exception occurred in function test_get_views_in_model {}".format(e),
            )

        return return_value
