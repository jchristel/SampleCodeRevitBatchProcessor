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
        super(GetViews, self).__init__(doc=doc, test_name="get_views_in_model")

    def test(self):
        """
        get views in model test

        :param doc: Current Revit model document.
        :type doc: Autodesk.Revit.DB.Document
        :param test_name: The test name.
        :type test_name: str

        :return:
            Result class instance.
                - .result = True if views where retrieved successfully, otherwise False
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
            # set up a return all views filter
            def action(x):
                return True

            views_in_model = [
                ["TEST", rdb.ViewType.DraftingView],
                ["Wall Schedule", rdb.ViewType.Schedule],
                ["Level 00", rdb.ViewType.FloorPlan],
                ["Section - Level Test", rdb.ViewType.Section],
            ]
            # get all views in model (only 1 in test model)
            result = get_views_in_model(self.document, action)

            # check against expected views
            counter = 0
            for view_retrieved in result:
                return_value.append_message(
                    " view name: {}, view type: {}, ".format(
                        view_retrieved.Name, view_retrieved.ViewType
                    )
                )
                assert view_retrieved.Name == views_in_model[counter][0]
                assert view_retrieved.ViewType == views_in_model[counter][1]

                counter = counter + 1

            # check overall number of views retrieved matches expected
            return_value.append_message(
                " number of retrieved views: {}, number of expected views: {}, ".format(
                    len(result), len(views_in_model)
                )
            )
            assert len(result) == len(views_in_model)

        except Exception as e:
            return_value.update_sep(
                False,
                "An exception occurred in function {}: {}".format(self.test_name, e),
            )

        return return_value
