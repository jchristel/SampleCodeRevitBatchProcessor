"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains revit grids toggle bubble visibility at end tests . 
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
from duHast.Revit.Grids.grids import get_grids_in_model
from duHast.Revit.Grids.grids_appearance import show_bubble_end
from duHast.Revit.Views.views import get_views_in_model
from duHast.Utilities.Objects import result as res

# import Autodesk
import Autodesk.Revit.DB as rdb


class GridsToggleBubbleVisibilityAtEnd(revit_test.RevitTest):
    def __init__(self, doc):
        # store document in base class
        super(GridsToggleBubbleVisibilityAtEnd, self).__init__(
            doc=doc, test_name="show_bubble_end"
        )

    def _toggle_grid_bubbles(self, grids, view, is_visible):
        """
        Tests toggling both grid ends of each grid past in.

        :param grids: The grids
        :type grids: Autodesk.Revit.DB.Grid
        :param view: The view in which to toggle grid bubbles
        :type view: Autodesk.Revit.DB.View
        :param is_visible: True: bubbles on, False bubbles off
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
        # toggle grid bubbles off on both ends
        for grid in grids:
            # set hide bubble at zero end
            change_bubble_zero = show_bubble_end(
                self.document, grid, view, rdb.DatumEnds.End0, is_visible
            )
            change_bubble_one = show_bubble_end(
                self.document, grid, view, rdb.DatumEnds.End1, is_visible
            )
            # check for any exceptions
            return_value.append_message(
                "grid id: {} result zero end: {} vs expected: {}".format(
                    grid.Id, change_bubble_zero.status, True
                )
            )
            # check for any exceptions
            return_value.append_message(
                "grid id: {} result one end: {} vs expected: {}".format(
                    grid.Id, change_bubble_one.status, True
                )
            )
            assert change_bubble_zero.status == True
            assert change_bubble_one.status == True
        return return_value

    def _check_grid_bubbles(self, grids, view, is_visible):
        """
        Checks actual grid bubble visibility.

        :param grids: The grids
        :type grids: Autodesk.Revit.DB.Grid
        :param view: The view in which to toggle grid bubbles
        :type view: Autodesk.Revit.DB.View
        :param is_visible: _description_
        :param is_visible: True: bubbles on, False bubbles off
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
                    grid.IsBubbleVisibleInView(rdb.DatumEnds.End0, view),
                    is_visible,
                )
            )
            return_value.append_message(
                "id: {} result: {} vs expected: {}".format(
                    grid.Id,
                    grid.IsBubbleVisibleInView(rdb.DatumEnds.End1, view),
                    is_visible,
                )
            )

            assert grid.IsBubbleVisibleInView(rdb.DatumEnds.End0, view) == is_visible
            assert grid.IsBubbleVisibleInView(rdb.DatumEnds.End1, view) == is_visible
        return return_value

    def test(self):
        """
        show_bubble_end test

        :param doc: Current Revit model document.
        :type doc: Autodesk.Revit.DB.Document
        :param test_name: The test name.
        :type test_name: str

        :return:
            Result class instance.
                - .result = True if all grids bubble(s) visibility was set successfully, otherwise False.
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
                        toggle_grids_off = self._toggle_grid_bubbles(
                            grids,
                            views[0],
                            False,  # False here refers to the actual bubble visibility
                        )
                        action_return_value.update(toggle_grids_off)
                        # check actual grids
                        check_grids_off = self._check_grid_bubbles(
                            grids,
                            views[0],
                            False,  # False here refers the actual visibility of the bubble
                        )
                        action_return_value.update(check_grids_off)

                        # switch bubbles back on
                        toggle_grids_on = self._toggle_grid_bubbles(
                            grids,
                            views[0],
                            True,  # true here refers to the actual bubble visibility
                        )
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
