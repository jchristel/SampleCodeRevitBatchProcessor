'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to purging Revit curtain wall elements. 
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

from duHast.APISamples.Family import RevitFamilyUtils as rFam
from duHast.APISamples.Common import RevitPurgeUtils as rPurgeUtils
from duHast.APISamples.Walls import RevitCurtainWallElements as rCurtainWallElem

def GetUsedCurtainWallElementTypeIds(doc):
    '''
    Gets all used Curtain Wall Element element type ids available in model.
    Used: at least one instance of this type is placed in the model.
    Includes:
    - curtain wall panels
    - curtain wall mullions
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids representing curtain wall element types.
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    ids = rPurgeUtils.GetUsedUnusedTypeIds(doc, rCurtainWallElem.GetAllCurtainWallElementTypeIdsInModelByCategory, 1)
    return ids

def FamilyNoTypesInUse(famTypeIds,unUsedTypeIds):
    '''
    Compares two lists of ids. True if any id is not in unUsedTypeIds.
    TODO: check for more generic list comparison and remove this function.
    :param famTypeIds: List of family type ids to check.
    :type famTypeIds: List of Autodesk.Revit.DB.ElementId
    :param unUsedTypeIds: Reference list of ids.
    :type unUsedTypeIds: List of Autodesk.Revit.DB.ElementId
    :return: True if any id from famTypeIds is not in unUsedTypeIds.
    :rtype: bool
    '''

    match = True
    for famTypeId in famTypeIds:
        if (famTypeId not in unUsedTypeIds):
            match = False
            break
    return match

def GetUnusedNonSymbolCurtainWallElementTypeIdsToPurge(doc):
    '''
    Gets all unused Curtain Wall Element element type ids which can be safely deleted from the model.
    This method can be used to safely delete unused in curtain wall element types. There is no requirement by Revit to have at least one\
        curtain wall element definition in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids representing unused in curtain wall element types.
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    # get unused type ids
    ids = rPurgeUtils.GetUsedUnusedTypeIds(doc, rCurtainWallElem.GetAllCurtainWallElementTypeIdsByCategoryExclSymbols, 0)
    # unlike other element types, here I do NOT make sure there is at least on curtain wall element type per system family left in model!!
    return ids

def GetUsedCurtainWallSymbolIds(doc):
    '''
    Gets a list of all used loadable, non shared, family symbols (types) in the model of categories:
    - curtain wall panels
    - curtain wall mullions
    Used: at least one family instance of this symbol (type) is placed in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids representing curtain wall family symbols.
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    ids = rPurgeUtils.GetUsedUnusedTypeIds(doc, rCurtainWallElem.GetAllCurtainWallNonSharedSymbolIdsByCategory, 1)
    return ids

def GetUnusedCurtainWallSymbolIds(doc):
    '''
    Gets a list of all used loadable, non shared, family symbols (types) in the model of categories:
    - curtain wall panels
    - curtain wall mullions
    Unused: Not one family instance of this symbol (type) is placed in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids representing curtain wall family symbols.
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    ids = rPurgeUtils.GetUsedUnusedTypeIds(doc, rCurtainWallElem.GetAllCurtainWallNonSharedSymbolIdsByCategory, 0)
    return ids

def GetUnusedICurtainWallSymbolIdsForPurge(doc):
    '''
    Gets symbol(type) ids and family ids (when no type is in use) of curtain wall element families which can be safely deleted from the model.
    This method can be used to safely delete unused curtain wall element types. There is no requirement by Revit to have at least one\
        in place wall definition in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids representing unused curtain wall element symbols (types) and families.
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    ids = rFam.GetUnusedInPlaceIdsForPurge(doc, GetUnusedCurtainWallSymbolIds)
    return ids