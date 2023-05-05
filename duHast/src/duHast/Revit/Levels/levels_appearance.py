'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Revit levels appearance modifier functions.
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

from duHast.Utilities import result as res
from duHast.Revit.Common import transaction as rTran


def change_levels_2D (doc, levels, view):
    '''
    Changes all levels in view to 2D
    :param doc: The current model document.
    :type doc: Autodesk.Revit.DB.Document
    :param levels: List of levels to be changed to 2D.
    :type levels: [Autodesk.Revit.DB.Level]
    :param view: The view in which to change the levels
    :type view: Autodesk.Revit.DB.View
    :return: 
        Result class instance.
        - result.status. True if all levels where set to 2D, otherwise False.
        - result.message will contain the name(s) of the level(s) changed to 2D
        - result.result empty list
        On exception:
        - result.status (bool) will be False.
        - result.message will contain generic exception message including the level name.
        - result.result will be empty
    :rtype: :class:`.Result`
    '''

    return_value = res.Result()
    # needs to run in a transaction
    def action():
        action_return_value = res.Result()
        level_counter = 0
        for g in levels:
            level_counter = level_counter + 1
            try:
                g.SetDatumExtentType(rdb.DatumEnds.End1, view, rdb.DatumExtentType.ViewSpecific)
                g.SetDatumExtentType(rdb.DatumEnds.End0, view, rdb.DatumExtentType.ViewSpecific)
                action_return_value.update_sep(True, 'Changed level {} to 2D.'.format(g.Name))
            except Exception as e:
                action_return_value.update_sep(False, 'Failed to change level {} to 2D with exception: {}'.format(g.Name, e))
        if(level_counter == 0):
            action_return_value.update_sep(True, 'No levels visible in view {}'.format(view.Name))
        return action_return_value
    transaction = rdb.Transaction(doc, "levels to 2D")
    return_value = rTran.in_transaction(transaction, action)
    return return_value


def show_head_end (doc, level, view, end_identifier, show_head):
    '''
    Toggles level head visibility on specified end for given level.
    
    :param doc: The current model document.
    :type doc: Autodesk.Revit.DB.Document
    :param level: The level of which a heads visibility is to be toggled.
    :type level: Autodesk.Revit.DB.Level
    :param view: The view in which a level heads visibility is to be toggled.
    :type view: Autodesk.Revit.DB.View
    :param end_identifier: which end.
    :type end_identifier: 
    :param show_head: True head will switched on, False it will be switched off
    :type show_head: bool
    :return: 
        Result class instance.
        - result.status. True if all levels head(s) visibility was set successfully, otherwise False.
        - result.message will contain the name(s) of the level(s) where a head visibility was set.
        - result.result empty list
        On exception:
        - result.status (bool) will be False.
        - result.message will contain generic exception message including the level name.
        - result.result will be empty
    :rtype: :class:`.Result`
    '''

    return_value = res.Result()
    # needs to run in a transaction
    def action():
        action_return_value = res.Result()
        try:
            if (show_head):
                level.ShowBubbleInView(end_identifier, view)
                action_return_value.update_sep(True, 'Set level {} head to visible at end: {}'.format(level.Name, end_identifier))
            else:
                level.HideBubbleInView(end_identifier, view)
                action_return_value.update_sep(True, 'Set level {} head to invisible at end: {}'.format(level.Name, end_identifier))
        except Exception as e:
            action_return_value.update_sep(False, 'Failed to change level {} head visibility at end {} with exception: {}'.format(level.Name, end_identifier, e))
        return action_return_value

    transaction = rdb.Transaction(doc, "Toggle head. {}".format(show_head))
    return_value = rTran.in_transaction(transaction, action)
    return return_value


def hide_both_heads (doc, levels, view):
    '''
    Hides both heads of levels in given view.
    :param doc: The current model document.
    :type doc: Autodesk.Revit.DB.Document
    :param level: The level of which a heads visibility is to be toggled.
    :type level: Autodesk.Revit.DB.Level
    :param view: The view in which a level heads visibility is to be toggled.
    :type view: Autodesk.Revit.DB.View
    :return: 
        Result class instance.
        - result.status. True if all levels head(s) visibility was switched off successfully, otherwise False.
        - result.message will contain the name(s) of the level(s) where a head visibility was set.
        - result.result empty list
        On exception:
        - result.status (bool) will be False.
        - result.message will contain generic exception message including the level name.
        - result.result will be empty
    :rtype: :class:`.Result`
    '''

    return_value = res.Result()
    for l in levels:
        return_value.update(show_head_end(doc, l, view, rdb.DatumEnds.End1, False))
        return_value.update( show_head_end(doc, l, view, rdb.DatumEnds.End0, False))

    return return_value

def show_head_zero_end (doc, levels, view):
    '''
    Turns on level heads at zero end in specified view.
    :param doc: The current model document.
    :type doc: Autodesk.Revit.DB.Document
    :param level: The levels of which a heads visibility is to be toggled.
    :type level: [Autodesk.Revit.DB.Level]
    :param view: The view in which a level heads visibility is to be toggled.
    :type view: Autodesk.Revit.DB.View
    :return: 
        Result class instance.
        - result.status. True if all levels head(s) visibility at zero end was set to visible successfully, otherwise False.
        - result.message will contain the name(s) of the level(s) where a head visibility was set.
        - result.result empty list
        On exception:
        - result.status (bool) will be False.
        - result.message will contain generic exception message including the level name.
        - result.result will be empty
    :rtype: :class:`.Result`
    '''

    return_value = res.Result()
    for l in levels:
        return_value.update(show_head_end(doc, l, view, rdb.DatumEnds.End0, True))

    return return_value

def show_head_one_end (doc, levels, view):
    '''
    Turns on level heads at One end in specified view.
    :param doc: The current model document.
    :type doc: Autodesk.Revit.DB.Document
    :param level: The levels of which a heads visibility is to be toggled.
    :type level: [Autodesk.Revit.DB.Level]
    :param view: The view in which a level heads visibility is to be toggled.
    :type view: Autodesk.Revit.DB.View
    :return: 
        Result class instance.
        - result.status. True if all levels head(s) visibility at one end was set to visible successfully, otherwise False.
        - result.message will contain the name(s) of the level(s) where a head visibility was set.
        - result.result empty list
        On exception:
        - result.status (bool) will be False.
        - result.message will contain generic exception message including the level name.
        - result.result will be empty
    :rtype: :class:`.Result`
    '''

    return_value = res.Result()
    for l in levels:
        return_value.update( show_head_end(doc, l, view, rdb.DatumEnds.End1, True))

    return return_value

def toggle_head_end (doc, level, view, end_identifier):
    '''
    Toggles level head visibility on specified end for given level in given views.
    :param doc: The current model document.
    :type doc: Autodesk.Revit.DB.Document
    :param level: The level of which a heads visibility is to be toggled.
    :type level: Autodesk.Revit.DB.Level
    :param view: The view in which a level heads visibility is to be toggled.
    :type view: Autodesk.Revit.DB.View
    :param end_identifier: The end of the level to be modified.
    :type view: Autodesk.Revit.DB.DatumEnds
    :return: 
        Result class instance.
        - result.status. True if all levels head(s) visibility was changed successfully, otherwise False.
        - result.message will contain the name(s) of the level(s) where a head visibility was changed.
        - result.result empty list
        On exception:
        - result.status (bool) will be False.
        - result.message will contain generic exception message including the level name.
        - result.result will be empty
    :rtype: :class:`.Result`
    '''

    return_value = res.Result()
    def action():
        try:
            action_return_value = res.Result()
            end_head_one = level.IsBubbleVisibleInView(end_identifier,view)
            if(end_head_one == False):
                level.ShowBubbleInView(end_identifier, view)
                action_return_value.update_sep(True, 'Set level {} head to visible at end: {}.'.format(level.Name, end_identifier))
            else:
                level.HideBubbleInView(end_identifier, view)
                action_return_value.update_sep(True, 'Set level {} head to not visible at end: {}.'.format(level.Name, end_identifier))
        except Exception as e:
            action_return_value.update_sep(False, 'Failed to change level {} head visibility at end: {} with exception: {}'.format(level.Name, end_identifier, e))
        return action_return_value
    transaction = rdb.Transaction(doc, "Toggle head.")
    return_value = rTran.in_transaction(transaction, action)
    return return_value


def toggle_head_one_end (doc, levels, view ):
    '''
    Toggles level head visibility on one end for given levels
    :param doc: The current model document.
    :type doc: Autodesk.Revit.DB.Document
    :param levels: The levels of which a heads visibility at one end is to be toggled.
    :type levels: [Autodesk.Revit.DB.Level]
    :param view: The view in which a level heads visibility is to be toggled.
    :type view: Autodesk.Revit.DB.View
    :return: 
        Result class instance.
        - result.status. True if all levels head(s) visibility at one end was changed successfully, otherwise False.
        - result.message will contain the name(s) of the level(s) where a head visibility was changed.
        - result.result empty list
        On exception:
        - result.status (bool) will be False.
        - result.message will contain generic exception message including the level name.
        - result.result will be empty
    :rtype: :class:`.Result`
    '''

    return_value = res.Result()
    for l in levels:
        return_value.update( toggle_head_end(doc, l, view, rdb.DatumEnds.End1))
    return return_value


def toggle_head_zero_end (doc, levels, view ):
    '''
    Toggles level head visibility on zero end for given levels
    :param doc: The current model document.
    :type doc: Autodesk.Revit.DB.Document
    :param levels: The levels of which a head visibility at zero end is to be toggled.
    :type levels: [Autodesk.Revit.DB.Level]
    :param view: The view in which a level heads visibility is to be toggled.
    :type view: Autodesk.Revit.DB.View
    :return: 
        Result class instance.
        - result.status. True if all level head(s) visibility at one end was changed successfully, otherwise False.
        - result.message will contain the name(s) of the level(s) where a head visibility was changed.
        - result.result empty list
        On exception:
        - result.status (bool) will be False.
        - result.message will contain generic exception message including the level name.
        - result.result will be empty
    :rtype: :class:`.Result`
    '''

    return_value = res.Result()
    for l in levels:
        return_value.update(toggle_head_end(doc, l, view, rdb.DatumEnds.End0))
    return return_value