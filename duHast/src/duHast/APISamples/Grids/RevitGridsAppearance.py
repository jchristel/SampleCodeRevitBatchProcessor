'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Revit grids appearance modifier functions.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''
#
#License:
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

import Autodesk.Revit.DB as rdb

from duHast.Utilities import Result as res
from duHast.APISamples.Common import RevitTransaction as rTran



def change_grids_2D (doc, grids, view):
    '''
    Changes all grids in view to 2D
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
    '''

    return_value = res.Result()
    # needs to run in a transaction
    def action():
        action_return_value = res.Result()
        grid_counter = 0
        for g in grids:
            grid_counter = grid_counter + 1
            try:
                g.SetDatumExtentType(rdb.DatumEnds.End1, view, rdb.DatumExtentType.ViewSpecific)
                g.SetDatumExtentType(rdb.DatumEnds.End0, view, rdb.DatumExtentType.ViewSpecific)
                action_return_value.UpdateSep(True, 'Changed grid {} to 2D.'.format(g.Name))
            except Exception as e:
                action_return_value.UpdateSep(False, 'Failed to change grid {} to 2D with exception: {}'.format(g.Name, e))
        if(grid_counter == 0):
            action_return_value.UpdateSep(True, 'No grids visible in view {}'.format(view.Name))
        return action_return_value
    transaction = rdb.Transaction(doc, "Grids to 2D")
    return_value = rTran.in_transaction(transaction, action)
    return return_value


def show_bubble_end (doc, grid, view, end_identifier, show_bubble):
    '''
    Toggles grid bubble visibility on specified end for given grid.
    :param doc: The current model document.
    :type doc: Autodesk.Revit.DB.Document
    :param grid: The grid of which a bubbles visibility is to be toggled.
    :type grid: Autodesk.Revit.DB.Grid
    :param view: The view in which a grid bubbles visibility is to be toggled.
    :type view: Autodesk.Revit.DB.View
    :param show_bubble: True bubble will switched on, False it will be switched off
    :type show_bubble: bool
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
    '''

    return_value = res.Result()
    # needs to run in a transaction
    def action():
        action_return_value = res.Result()
        try:
            if(show_bubble):
                grid.ShowBubbleInView(end_identifier, view)
                action_return_value.UpdateSep(True, 'Set grid {} bubble to visible at end: {}'.format(grid.Name, end_identifier))
            else:
                grid.HideBubbleInView(end_identifier, view)
                action_return_value.UpdateSep(True, 'Set grid {} bubble to invisible at end: {}'.format(grid.Name, end_identifier))
        except Exception as e:
            action_return_value.UpdateSep(False, 'Failed to change grid {} bubble visibility at end {} with exception: {}'.format(grid.Name, end_identifier, e))
        return action_return_value

    transaction = rdb.Transaction(doc, "Toggle Bubble. {}".format((show_bubble)))
    return_value = rTran.in_transaction(transaction, action)
    return return_value


def hide_both_bubbles (doc, grids, view):
    '''
    Hides both bubbles of grids in given view.
    :param doc: The current model document.
    :type doc: Autodesk.Revit.DB.Document
    :param grid: The grid of which a bubbles visibility is to be toggled.
    :type grid: Autodesk.Revit.DB.Grid
    :param view: The view in which a grid bubbles visibility is to be toggled.
    :type view: Autodesk.Revit.DB.View
    :return: 
        Result class instance.
        - result.status. True if all grids bubble(s) visibility was switched off successfully, otherwise False.
        - result.message will contain the name(s) of the grid(s) where a bubble visibility was set.
        - result.result empty list
        On exception:
        - result.status (bool) will be False.
        - result.message will contain generic exception message including the grid name.
        - result.result will be empty
    :rtype: :class:`.Result`
    '''

    return_value = res.Result()
    for g in grids:
        return_value.Update(show_bubble_end(doc, g, view, rdb.DatumEnds.End1, False))
        return_value.Update( show_bubble_end(doc, g, view, rdb.DatumEnds.End0, False))

    return return_value

def show_bubble_zero_end (doc, grids, view):
    '''
    Turns on grid bubbles at zero end in specified view.
    :param doc: The current model document.
    :type doc: Autodesk.Revit.DB.Document
    :param grid: The grids of which a bubbles visibility is to be toggled.
    :type grid: [Autodesk.Revit.DB.Grid]
    :param view: The view in which a grid bubbles visibility is to be toggled.
    :type view: Autodesk.Revit.DB.View
    :return: 
        Result class instance.
        - result.status. True if all grids bubble(s) visibility at zero end was set to visible successfully, otherwise False.
        - result.message will contain the name(s) of the grid(s) where a bubble visibility was set.
        - result.result empty list
        On exception:
        - result.status (bool) will be False.
        - result.message will contain generic exception message including the grid name.
        - result.result will be empty
    :rtype: :class:`.Result`
    '''

    return_value = res.Result()
    for g in grids:
        return_value.Update(show_bubble_end(doc, g, view, rdb.DatumEnds.End0, True))

    return return_value

def show_bubble_one_end (doc, grids, view):
    '''
    Turns on grid bubbles at One end in specified view.
    :param doc: The current model document.
    :type doc: Autodesk.Revit.DB.Document
    :param grid: The grids of which a bubbles visibility is to be toggled.
    :type grid: [Autodesk.Revit.DB.Grid]
    :param view: The view in which a grid bubbles visibility is to be toggled.
    :type view: Autodesk.Revit.DB.View
    :return: 
        Result class instance.
        - result.status. True if all grids bubble(s) visibility at one end was set to visible successfully, otherwise False.
        - result.message will contain the name(s) of the grid(s) where a bubble visibility was set.
        - result.result empty list
        On exception:
        - result.status (bool) will be False.
        - result.message will contain generic exception message including the grid name.
        - result.result will be empty
    :rtype: :class:`.Result`
    '''

    return_value = res.Result()
    for g in grids:
        return_value.Update( show_bubble_end(doc, g, view, rdb.DatumEnds.End1, True))

    return return_value

def toggle_bubble_end (doc, grid, view, end_identifier):
    '''
    Toggles grid bubble visibility on specified end for given grid in given views.
    :param doc: The current model document.
    :type doc: Autodesk.Revit.DB.Document
    :param grid: The grid of which a bubbles visibility is to be toggled.
    :type grid: Autodesk.Revit.DB.Grid
    :param view: The view in which a grid bubbles visibility is to be toggled.
    :type view: Autodesk.Revit.DB.View
    :param end_identifier: The end of the grid to be modified.
    :type view: Autodesk.Revit.DB.DatumEnds
    :return: 
        Result class instance.
        - result.status. True if all grids bubble(s) visibility was changed successfully, otherwise False.
        - result.message will contain the name(s) of the grid(s) where a bubble visibility was changed.
        - result.result empty list
        On exception:
        - result.status (bool) will be False.
        - result.message will contain generic exception message including the grid name.
        - result.result will be empty
    :rtype: :class:`.Result`
    '''

    return_value = res.Result()
    def action():
        try:
            action_return_value = res.Result()
            endBubbleOne = grid.IsBubbleVisibleInView(end_identifier,view)
            if(endBubbleOne == False):
                grid.ShowBubbleInView(end_identifier, view)
                action_return_value.UpdateSep(True, 'Set grid {} bubble to visible at end: {}.'.format(grid.Name, end_identifier))
            else:
                grid.HideBubbleInView(end_identifier, view)
                action_return_value.UpdateSep(True, 'Set grid {} bubble to not visible at end: {}.'.format(grid.Name, end_identifier))
        except Exception as e:
            action_return_value.UpdateSep(False, 'Failed to change grid {} bubble visibility at end: {} with exception: {}'.format(grid.Name, end_identifier, e))
        return action_return_value
    transaction = rdb.Transaction(doc, "Toggle Bubble.")
    return_value = rTran.in_transaction(transaction, action)
    return return_value


def toggle_bubble_one_end (doc, grids, view ):
    '''
    Toggles grid bubble visibility on one end for given grids
    :param doc: The current model document.
    :type doc: Autodesk.Revit.DB.Document
    :param grids: The grids of which a bubbles visibility at one end is to be toggled.
    :type grids: [Autodesk.Revit.DB.Grid]
    :param view: The view in which a grid bubbles visibility is to be toggled.
    :type view: Autodesk.Revit.DB.View
    :return: 
        Result class instance.
        - result.status. True if all grids bubble(s) visibility at one end was changed successfully, otherwise False.
        - result.message will contain the name(s) of the grid(s) where a bubble visibility was changed.
        - result.result empty list
        On exception:
        - result.status (bool) will be False.
        - result.message will contain generic exception message including the grid name.
        - result.result will be empty
    :rtype: :class:`.Result`
    '''

    return_value = res.Result()
    for g in grids:
        return_value.Update( toggle_bubble_end(doc, g, view, rdb.DatumEnds.End1))
    return return_value


def toggle_bubble_zero_end (doc, grids, view ):
    '''
    Toggles grid bubble visibility on zero end for given grids
    :param doc: The current model document.
    :type doc: Autodesk.Revit.DB.Document
    :param grids: The grids of which a bubbles visibility at zero end is to be toggled.
    :type grids: [Autodesk.Revit.DB.Grid]
    :param view: The view in which a grid bubbles visibility is to be toggled.
    :type view: Autodesk.Revit.DB.View
    :return: 
        Result class instance.
        - result.status. True if all grids bubble(s) visibility at one end was changed successfully, otherwise False.
        - result.message will contain the name(s) of the grid(s) where a bubble visibility was changed.
        - result.result empty list
        On exception:
        - result.status (bool) will be False.
        - result.message will contain generic exception message including the grid name.
        - result.result will be empty
    :rtype: :class:`.Result`
    '''

    return_value = res.Result()
    for g in grids:
        return_value.Update(toggle_bubble_end(doc, g, view, rdb.DatumEnds.End0))
    return return_value