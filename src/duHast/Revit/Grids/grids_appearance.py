"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Revit grids appearance modifier functions.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Note: Any grid appearance modification in a view will throw an exception if the grid is not actually visible in the view.

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

from Autodesk.Revit.DB import DatumEnds, DatumExtentType, Transaction


from duHast.Utilities.Objects import result as res
from duHast.Revit.Common import transaction as rTran


def change_grids_2D(doc, grids, view):
    """
    Changes all grids in view to 2D

    Note: Any grid past in, which is not visible in the view, will throw an exception when attempting to set to 2D.

    :param doc: The current model document.
    :type doc: Autodesk.Revit.DB.Document
    :param grids: List of grids to be changed to 2D.
    :type grids: [Autodesk.Revit.DB.Grid]
    :param view: The view in which to change the grids
    :type view: Autodesk.Revit.DB.View
    :return:
        Result class instance.
        - result.status. True if all grids where set to 2D, otherwise False.
        - result.message will contain the name(s) of the grid(s) changed to 2D
        - result.result empty list
        On exception:
        - result.status (bool) will be False.
        - result.message will contain generic exception message including the grid name.
        - result.result will be empty
    :rtype: :class:`.Result`
    """

    return_value = res.Result()

    # needs to run in a transaction
    def action():
        action_return_value = res.Result()
        grid_counter = 0
        for g in grids:
            grid_counter = grid_counter + 1
            try:
                g.SetDatumExtentType(DatumEnds.End1, view, DatumExtentType.ViewSpecific)
                g.SetDatumExtentType(DatumEnds.End0, view, DatumExtentType.ViewSpecific)
                action_return_value.update_sep(
                    True, "Changed grid {} to 2D.".format(g.Name)
                )
            except Exception as e:
                action_return_value.update_sep(
                    False,
                    "Failed to change grid {} to 2D with exception: {}".format(
                        g.Name, e
                    ),
                )
        if grid_counter == 0:
            action_return_value.update_sep(
                True, "No grids visible in view {}".format(view.Name)
            )
        return action_return_value

    transaction = Transaction(doc, "Grids to 2D")
    return_value = rTran.in_transaction(transaction, action)
    return return_value


def show_bubble_end(doc, grid, view, end_identifier, show_bubble):
    """
    Toggles grid bubble visibility on the specified end for a given grid.

    :param doc: The current model document.
    :type doc: Autodesk.Revit.DB.Document

    :param grid: The grid of which a bubble's visibility is to be toggled.
    :type grid: Autodesk.Revit.DB.Grid

    :param view: The view in which a grid bubble's visibility is to be toggled.
    :type view: Autodesk.Revit.DB.View

    :param end_identifier: An enumerated type representing ends of a datum plane.
    :type end_identifier: Autodesk.Revit.DB.DatumEnds

    :param show_bubble: True if the bubble will be switched on, False if it will be switched off.
    :type show_bubble: bool

    :return: Result class instance.

        - `result.status` (bool): True if the grid bubble(s) visibility was set successfully, otherwise False.
        - `result.message` (str): Contains the name(s) of the grid(s) where bubble visibility was set.
        - `result.result` (list): Empty list.

    On exception:

        - `result.status` (bool) will be False.
        - `result.message` (str) will contain a generic exception message including the grid name.
        - `result.result` (list) will be empty.

    :rtype: :class:`.Result`
    """

    return_value = res.Result()

    # needs to run in a transaction
    def action():
        action_return_value = res.Result()
        try:
            if show_bubble:
                grid.ShowBubbleInView(end_identifier, view)
                action_return_value.update_sep(
                    True,
                    "Set grid {} bubble to visible at end: {}".format(
                        grid.Name, end_identifier
                    ),
                )
            else:
                grid.HideBubbleInView(end_identifier, view)
                action_return_value.update_sep(
                    True,
                    "Set grid {} bubble to invisible at end: {}".format(
                        grid.Name, end_identifier
                    ),
                )
        except Exception as e:
            action_return_value.update_sep(
                False,
                "Failed to change grid {} bubble visibility at end {} with exception: {}".format(
                    grid.Name, end_identifier, e
                ),
            )
        return action_return_value

    transaction = Transaction(doc, "Toggle Bubble. {}".format((show_bubble)))
    return_value = rTran.in_transaction(transaction, action)
    return return_value


def hide_both_bubbles(doc, grids, view):
    """
    Hides both bubbles of grids in the given view.

    :param doc: The current model document.
    :type doc: Autodesk.Revit.DB.Document

    :param grid: The grid for which bubble visibility is to be toggled.
    :type grid: Autodesk.Revit.DB.Grid

    :param view: The view in which grid bubble visibility is to be toggled.
    :type view: Autodesk.Revit.DB.View

    :return: Result class instance.

        - `result.status` (bool): True if all grid bubble(s) visibility was switched off successfully, otherwise False.
        - `result.message` (str): Contains the name(s) of the grid(s) where bubble visibility was set.
        - `result.result` (list): Empty list.

    On exception:

        - `result.status` (bool) will be False.
        - `result.message` (str) will contain a generic exception message including the grid name.
        - `result.result` (list) will be empty.

    :rtype: :class:`.Result`
    """

    return_value = res.Result()
    for g in grids:
        return_value.update(show_bubble_end(doc, g, view, DatumEnds.End1, False))
        return_value.update(show_bubble_end(doc, g, view, DatumEnds.End0, False))

    return return_value


def show_bubble_zero_end(doc, grids, view):
    """
    Turns on grid bubbles at the zero end in the specified view.

    :param doc: The current model document.
    :type doc: Autodesk.Revit.DB.Document

    :param grid: The grids for which bubble visibility is to be toggled.
    :type grid: List[Autodesk.Revit.DB.Grid]

    :param view: The view in which grid bubble visibility is to be toggled.
    :type view: Autodesk.Revit.DB.View

    :return: Result class instance.

        - `result.status` (bool): True if all grid bubble(s) visibility at the zero end was set to visible successfully, otherwise False.
        - `result.message` (str): Contains the name(s) of the grid(s) where bubble visibility was set.
        - `result.result` (list): Empty list.

    On exception:

        - `result.status` (bool) will be False.
        - `result.message` (str) will contain a generic exception message including the grid name.
        - `result.result` (list) will be empty.

    :rtype: :class:`.Result`
    """

    return_value = res.Result()
    for g in grids:
        return_value.update(show_bubble_end(doc, g, view, DatumEnds.End0, True))

    return return_value


def show_bubble_one_end(doc, grids, view):
    """
    Turns on grid bubbles at one end in the specified view.

    :param doc: The current model document.
    :type doc: Autodesk.Revit.DB.Document

    :param grid: The grids for which bubble visibility is to be toggled.
    :type grid: List[Autodesk.Revit.DB.Grid]

    :param view: The view in which grid bubble visibility is to be toggled.
    :type view: Autodesk.Revit.DB.View

    :return: Result class instance.

        - `result.status` (bool): True if all grid bubble(s) visibility at one end was set to visible successfully, otherwise False.
        - `result.message` (str): Contains the name(s) of the grid(s) where bubble visibility was set.
        - `result.result` (list): Empty list.

    On exception:

        - `result.status` (bool) will be False.
        - `result.message` (str) will contain a generic exception message including the grid name.
        - `result.result` (list) will be empty.

    :rtype: :class:`.Result`
    """

    return_value = res.Result()
    for g in grids:
        return_value.update(show_bubble_end(doc, g, view, DatumEnds.End1, True))

    return return_value


def toggle_bubble_end(doc, grid, view, end_identifier):
    """
    Toggles grid bubble visibility on a specified end for a given grid in given views.

    :param doc: The current model document.
    :type doc: Autodesk.Revit.DB.Document

    :param grid: The grid of which bubble visibility is to be toggled.
    :type grid: Autodesk.Revit.DB.Grid

    :param view: The view in which grid bubble visibility is to be toggled.
    :type view: Autodesk.Revit.DB.View

    :param end_identifier: The end of the grid to be modified.
    :type end_identifier: Autodesk.Revit.DB.DatumEnds

    :return: Result class instance.

        - `result.status` (bool): True if the grid bubble(s) visibility was changed successfully, otherwise False.
        - `result.message` (str): Contains the name of the grid where bubble visibility was changed.
        - `result.result` (list): Empty list.

    On exception:

        - `result.status` (bool) will be False.
        - `result.message` (str) will contain a generic exception message including the grid name.
        - `result.result` (list) will be empty.

    :rtype: :class:`.Result`
    """

    return_value = res.Result()

    def action():
        try:
            action_return_value = res.Result()
            endBubbleOne = grid.IsBubbleVisibleInView(end_identifier, view)
            if endBubbleOne == False:
                grid.ShowBubbleInView(end_identifier, view)
                action_return_value.update_sep(
                    True,
                    "Set grid {} bubble to visible at end: {}.".format(
                        grid.Name, end_identifier
                    ),
                )
            else:
                grid.HideBubbleInView(end_identifier, view)
                action_return_value.update_sep(
                    True,
                    "Set grid {} bubble to not visible at end: {}.".format(
                        grid.Name, end_identifier
                    ),
                )
        except Exception as e:
            action_return_value.update_sep(
                False,
                "Failed to change grid {} bubble visibility at end: {} with exception: {}".format(
                    grid.Name, end_identifier, e
                ),
            )
        return action_return_value

    transaction = Transaction(doc, "Toggle Bubble.")
    return_value = rTran.in_transaction(transaction, action)
    return return_value


def toggle_bubble_one_end(doc, grids, view):
    """
    Toggles grid bubble visibility on one end for given grids.

    :param doc: The current model document.
    :type doc: Autodesk.Revit.DB.Document

    :param grids: The grids of which bubble visibility at one end is to be toggled.
    :type grids: List[Autodesk.Revit.DB.Grid]

    :param view: The view in which grid bubble visibility is to be toggled.
    :type view: Autodesk.Revit.DB.View

    :return: Result class instance.

        - `result.status` (bool): True if the bubble visibility at one end was changed successfully for all grids, otherwise False.
        - `result.message` (str): Contains the name(s) of the grid(s) where bubble visibility was changed.
        - `result.result` (list): Empty list.

    On exception:

        - `result.status` (bool) will be False.
        - `result.message` (str) will contain a generic exception message including the grid name.
        - `result.result` (list) will be empty.

    :rtype: :class:`.Result`
    """

    return_value = res.Result()
    for g in grids:
        return_value.update(toggle_bubble_end(doc, g, view, DatumEnds.End1))
    return return_value


def toggle_bubble_zero_end(doc, grids, view):
    """
    Toggles grid bubble visibility on zero end for given grids.

    :param doc: The current model document.
    :type doc: Autodesk.Revit.DB.Document

    :param grids: The grids of which bubble visibility at zero end is to be toggled.
    :type grids: List[Autodesk.Revit.DB.Grid]

    :param view: The view in which grid bubble visibility is to be toggled.
    :type view: Autodesk.Revit.DB.View

    :return: Result class instance.

        - `result.status` (bool): True if the bubble visibility at zero end was changed successfully for all grids, otherwise False.
        - `result.message` (str): Contains the name(s) of the grid(s) where bubble visibility was changed.
        - `result.result` (list): Empty list.

    On exception:

        - `result.status` (bool) will be False.
        - `result.message` (str) will contain a generic exception message including the grid name.
        - `result.result` (list) will be empty.

    :rtype: :class:`.Result`
    """

    return_value = res.Result()
    for g in grids:
        return_value.update(toggle_bubble_end(doc, g, view, DatumEnds.End0))
    return return_value
