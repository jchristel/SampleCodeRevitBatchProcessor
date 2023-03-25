'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Revit levels helper functions.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''
#
#License:
#
#
# Revit Batch Processor Sample Code
#
# Copyright (c) 2021  Jan Christel
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

import clr
import System
clr.AddReference("System.Core")
from System import Linq
clr.ImportExtensions(Linq)

# import common library modules
from duHast.APISamples import RevitCommonAPI as com
from duHast.APISamples import RevitElementParameterGetUtils as rParaGet
from duHast.APISamples import RevitWorksets as rWork
from duHast.APISamples import RevitFamilyUtils as rFamU
from duHast.Utilities import Result as res
from duHast.APISamples import RevitTransaction as rTran
from duHast.Utilities import Utility as util

# import Autodesk
import Autodesk.Revit.DB as rdb

# -------------------------------------------- common variables --------------------
#: header used in reports
REPORT_LEVELS_HEADER = ['HOSTFILE', 'ID', 'NAME', 'WORKSETNAME', 'ELEVATION']

def get_levels_in_model(doc):
  '''
  Get all levels in model

  :param doc: The current model document.
  :type doc: Autodesk.Revit.DB.Document
  :return: A collector with all levels in model.
  :rtype: Autodesk.Revit.DB.FilteredElementCollector
  '''

  collector = rdb.FilteredElementCollector(doc).OfClass(rdb.Level)
  return collector

# --------------------------------------------- visibility functions ------------------

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
                action_return_value.UpdateSep(True, 'Changed level {} to 2D.'.format(g.Name))
            except Exception as e:
                action_return_value.UpdateSep(False, 'Failed to change level {} to 2D with exception: {}'.format(g.Name, e))
        if(level_counter == 0):
            action_return_value.UpdateSep(True, 'No levels visible in view {}'.format(view.Name))
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
                action_return_value.UpdateSep(True, 'Set level {} head to visible at end: {}'.format(level.Name, end_identifier))
            else:
                level.HideBubbleInView(end_identifier, view)
                action_return_value.UpdateSep(True, 'Set level {} head to invisible at end: {}'.format(level.Name, end_identifier))
        except Exception as e:
            action_return_value.UpdateSep(False, 'Failed to change level {} head visibility at end {} with exception: {}'.format(level.Name, end_identifier, e))
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
        return_value.Update(show_head_end(doc, l, view, rdb.DatumEnds.End1, False))
        return_value.Update( show_head_end(doc, l, view, rdb.DatumEnds.End0, False))
    
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
        return_value.Update(show_head_end(doc, l, view, rdb.DatumEnds.End0, True))
    
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
        return_value.Update( show_head_end(doc, l, view, rdb.DatumEnds.End1, True))
    
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
                action_return_value.UpdateSep(True, 'Set level {} head to visible at end: {}.'.format(level.Name, end_identifier))
            else:
                level.HideBubbleInView(end_identifier, view)
                action_return_value.UpdateSep(True, 'Set level {} head to not visible at end: {}.'.format(level.Name, end_identifier))
        except Exception as e:
            action_return_value.UpdateSep(False, 'Failed to change level {} head visibility at end: {} with exception: {}'.format(level.Name, end_identifier, e))
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
        return_value.Update( toggle_head_end(doc, l, view, rdb.DatumEnds.End1))
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
        return_value.Update(toggle_head_end(doc, l, view, rdb.DatumEnds.End0))
    return return_value

# --------------------------------------------- utility functions ------------------

def GetLevelsListAscending(doc):
    '''
    Gets a filtered element collector of all levels in the model ascending by project elevation.

    Filters by category.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A filtered element collector of levels
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    collector = rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_Levels).WhereElementIsNotElementType().ToList().OrderBy(lambda l: l.ProjectElevation)
    return collector

# ------------------------------------------------------- Level reporting --------------------------------------------------------------------

def GetLevelReportData(doc, revitFilePath):
    '''
    Gets level data ready for being printed to file.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param revitFilePath: The file hostname, which is added to data returned.
    :type revitFilePath: str

    :return: list of list of revit level properties.
    :rtype: list of list of str
    '''

    data = []
    for p in rdb.FilteredElementCollector(doc).OfClass(rdb.Level):
        data.append([
            util.GetFileNameWithoutExt(revitFilePath), 
            str(p.Id.IntegerValue), 
            util.EncodeAscii(p.Name), 
            util.EncodeAscii(rWork.GetWorksetNameById(doc, p.WorksetId.IntegerValue)), 
            str(p.Elevation)])
    return data

# ------------------------------------------------- filters --------------------------------------------------------------------

def GetAllLevelHeadsByCategory(doc):
    '''
    Gets a filtered element collector of all level head types in the model.

    Filters by category.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector of level heads
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    collector = rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_LevelHeads).WhereElementIsElementType()
    return collector

def GetAllLevelTypesByCategory(doc):
    '''
    Gets a filtered element collector of all level types in the model.

    Filters by category.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector of level types.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    collector = rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_Levels).WhereElementIsElementType()
    return collector

def GetAllLevelTypeIdsByCategory(doc):
    '''
    Gets a list of all level type ids in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A list of all level type ids.
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    collector = rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_Levels).WhereElementIsElementType()
    ids = com.GetIdsFromElementCollector(collector)
    return ids

# -------------------------------------------------  purge --------------------------------------------------------------------

def GetUnusedLevelTypesForPurge(doc):
    '''
    Gets all ids of unused level types in the model.

    Unused: not one instance per level type is placed in the model.
    This method can be used to safely delete unused level types from the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A list of level type ids.
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    return com.GetUsedUnusedTypeIds(doc, GetAllLevelTypeIdsByCategory, 0, 6)

def GetUnusedLevelHeadFamilies(doc):
    '''
    Gets all ids of unused family symbols (types) of level head families.

    Unused: not one instance per symbol is placed in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A list of symbol ids.
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    usedTypes = com.GetUsedUnusedTypeIds(doc, GetAllLevelTypeIdsByCategory, 1, 6)
    headsInUseIds = []
    # get family symbol in use at level as symbol
    for lId in usedTypes:
        type = doc.GetElement(lId)
        id = rParaGet.get_built_in_parameter_value(type, rdb.BuiltInParameter.LEVEL_HEAD_TAG)
        if(id != None and id not in headsInUseIds):
            headsInUseIds.append(id)
    # get all level head symbols available
    allSymbolsInModel = GetAllLevelHeadsByCategory(doc)
    unusedSymbolIds = []
    # filter out unused level head symbols and add to list to be returned
    for  levelSymbolInModel in  allSymbolsInModel:
        if(levelSymbolInModel.Id not in headsInUseIds ):
            unusedSymbolIds.append(levelSymbolInModel.Id)
    return unusedSymbolIds

def GetAllLevelHeadFamilyTypeIds(doc):
    '''
    Gets ids of all level head family symbols (types) in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A list of symbol ids.
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    ids = []
    filter = rdb.ElementCategoryFilter(rdb.BuiltInCategory.OST_LevelHeads)
    col = rdb.FilteredElementCollector(doc).OfClass(rdb.FamilySymbol).WherePasses(filter)
    ids = com.GetIdsFromElementCollector(col)
    return ids

# doc             current document
def GetUnusedLevelHeadFamiliesForPurge(doc):
    '''
    Gets ids of all unused level head symbols and families.

    Unused: not one instance per level symbol is placed in the model.
    This method can be used to safely delete unused level symbols or families from the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    
    :return: A list of symbol and or family ids.
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    return rFamU.GetUnusedInPlaceIdsForPurge(doc, GetUnusedLevelHeadFamilies)