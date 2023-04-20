'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to purging Revit levels and level heads. 
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

from duHast.APISamples.Family import PurgeUnusedFamilyTypes as rFamPurge
from duHast.APISamples.Common import parameter_get_utils as rParaGet, purge_utils as rPurgeUtils
from duHast.APISamples.Levels import RevitLevels as rLevel

def get_unused_level_types_for_purge(doc):
    '''
    Gets all ids of unused level types in the model.
    Unused: not one instance per level type is placed in the model.
    This method can be used to safely delete unused level types from the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A list of level type ids.
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    return rPurgeUtils.get_used_unused_type_ids(doc, rLevel.get_all_level_type_ids_by_category, 0, 6)

def get_unused_level_head_families(doc):
    '''
    Gets all ids of unused family symbols (types) of level head families.
    Unused: not one instance per symbol is placed in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A list of symbol ids.
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    usedTypes = rPurgeUtils.get_used_unused_type_ids(doc, rLevel.get_all_level_type_ids_by_category, 1, 6)
    headsInUseIds = []
    # get family symbol in use at level as symbol
    for lId in usedTypes:
        type = doc.GetElement(lId)
        id = rParaGet.get_built_in_parameter_value(type, rdb.BuiltInParameter.LEVEL_HEAD_TAG)
        if(id != None and id not in headsInUseIds):
            headsInUseIds.append(id)
    # get all level head symbols available
    allSymbolsInModel = rLevel.get_all_level_heads_by_category(doc)
    unusedSymbolIds = []
    # filter out unused level head symbols and add to list to be returned
    for  levelSymbolInModel in  allSymbolsInModel:
        if(levelSymbolInModel.Id not in headsInUseIds ):
            unusedSymbolIds.append(levelSymbolInModel.Id)
    return unusedSymbolIds


def get_unused_level_head_families_for_purge(doc):
    '''
    Gets ids of all unused level head symbols and families.
    Unused: not one instance per level symbol is placed in the model.
    This method can be used to safely delete unused level symbols or families from the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A list of symbol and or family ids.
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    return rFamPurge.get_unused_in_place_ids_for_purge(doc, get_unused_level_head_families)