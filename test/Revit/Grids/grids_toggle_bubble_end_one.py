"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains revit grids toggle bubble visibility at one end tests . 
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
from duHast.Revit.Grids.grids import get_grids_in_model
from duHast.Revit.Grids.grids_appearance import toggle_bubble_one_end
from duHast.Revit.Views.views import get_views_in_model
from duHast.Utilities.Objects import result as res

# import Autodesk
import Autodesk.Revit.DB as rdb


class GridsToggleBubbleVisibilityAtOneEnd(revit_test.RevitTest):
    def __init__(self, doc):
        # store document in base class
        super(GridsToggleBubbleVisibilityAtOneEnd, self).__init__(
            doc=doc, test_name="toggle_bubble_one_end"
        )

    def _toggle_grid_bubbles(self, grids, view):
        """
        Tests toggling grid end one of each grid past in.

        :param grids: The grids
        :type grids: Autodesk.Revit.DB.Grid
        :param view: The view in which to toggle grid bubbles
        :type view: Autodesk.Revit.DB.View

        :return:
            Result class instance.
            - result.status. True if all grids bubble(s) at one end visibility was toggled successfully, otherwise False.
            - result.message will contain the name(s) of the grid(s) where a bubble visibility was set.
            - result.result empty list
            On exception:
            - result.status (bool) will be False.
            - result.message will contain generic exception message including the grid name.
            - result.result will be empty
        :rtype: :class:`.Result`
        """

        return_value = res.Result()
        # toggle grid bubbles off on both ends
        change_bubble_one = toggle_bubble_one_end(self.document, grids, view)
        # check for any exceptions
        return_value.append_message(
            "result one end: {} vs expected: {}".format(
                change_bubble_one.status,
                True,  # expecting the action to complete successfully
            )
        )
        assert (
            change_bubble_one.status == True
        )  # expecting the action to complete successfully
        return return_value

    def _check_grid_bubbles(self, grids, view, is_visible):
        """
        Checks actual grid bubble visibility.

        :param grids: The grids
        :type grids: Autodesk.Revit.DB.Grid
        :param view: The view in which to toggle grid bubbles
        :type view: Autodesk.Revit.DB.View
        :param is_visible: _description_
        :param is_visible: Assumed visibility status
        :type is_visible: bool
        :return:
            Result class instance.
            - result.status. True if all grids bubble(s) visibility was set successfully, otherwise False.
            - result.message will contain the name(s) of the grid(s) where a bubble visibility was set.
            - result.result empty list
            On exception:
            - result.status (bool) will be False.
            - result.message will contain generic exception message including the grid name.
            - result.result will be empty
        :rtype: :class:`.Result`
        """

        return_value = res.Result()
        # check grids
        for grid in grids:
            return_value.append_message(
                "id: {} result: {} vs expected: {}".format(
                    grid.Id,
                    grid.IsBubbleVisibleInView(rdb.DatumEnds.End1, view),
                    is_visible,
                )
            )
            assert grid.IsBubbleVisibleInView(rdb.DatumEnds.End1, view) == is_visible
        return return_value

    def test(self):
        """
        toggle_bubble_one_end test

        :param doc: Current Revit model document.
        :type doc: Autodesk.Revit.DB.Document
        :param test_name: The test name.
        :type test_name: str

        :return:
            Result class instance.
                - .result = True if grid visibility of bubble at one end was successfully toggled, otherwise False
                - .message will contain result(s) vs expected result(s)
                - . result (empty list)

                on exception:

                - .result Will be False
                - .message will contain exception message.
                - . result (empty list)
        :rtype: :class:`.Result`
        """

        return_value = res.Result()

        # set up a return specific plan return filter
        def action_name_check(x):
            if x.Name == "Level 00":
                return True

        try:
            # action to be executed in a transaction group so it can be rolled back at end of test
            def action(doc):
                action_return_value = res.Result()
                try:
                    # get all grids in the model
                    grids = get_grids_in_model(self.document)
                    # get sample view
                    views = get_views_in_model(self.document, action_name_check)

                    if len(views) >= 1:
                        # switch grid bubbles off
                        toggle_grids_first = self._toggle_grid_bubbles(grids, views[0])
                        action_return_value.update(toggle_grids_first)
                        # check actual grids
                        check_grids_off = self._check_grid_bubbles(
                            grids,
                            views[0],
                            False,  # False here refers the actual visibility of the bubble
                        )
                        action_return_value.update(check_grids_off)

                        # switch bubbles back on
                        toggle_grids_on = self._toggle_grid_bubbles(grids, views[0])
                        action_return_value.update(toggle_grids_on)
                        # check actual grids
                        check_grids_on = self._check_grid_bubbles(
                            grids,
                            views[0],
                            True,  # True here refers the actual visibility of the bubble
                        )
                        action_return_value.update(check_grids_on)

                    else:
                        raise ValueError(
                            "No view found in which to change grid appearance!"
                        )

                except Exception as e:
                    action_return_value.update_sep(
                        False,
                        "An exception occurred in function {}: {}".format(
                            self.test_name, e
                        ),
                    )
                return action_return_value

            return_value.update(self.in_transaction_group(action))

        except Exception as e:
            return_value.update_sep(
                False,
                "An exception occurred in function {}: {}".format(self.test_name, e),
            )
        return return_value
