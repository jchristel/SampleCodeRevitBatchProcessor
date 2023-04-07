'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to Revit railing balusters. 
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

from duHast.APISamples.Common import RevitCommonAPI as com
from duHast.APISamples.Railings.Utility.MergeLists import MergeIntoUniqueList
from duHast.APISamples.Railings.RevitRailings import GetAllRailingTypeIdsInModelByClassAndCategory


def GetBalustersUsedInPattern(bPattern):
    '''
    Gets list of unique baluster family ids used in a pattern only.
    :param bPattern: A revit baluster pattern.
    :type bPattern: Autodesk.Revit.DB.Architecture.BalusterPattern 
    :return: List of element ids of baluster family ids.
    :rtype: list Autodesk.Revit.DB.ElementId
    '''

    ids = []
    for i in range(0, bPattern.GetBalusterCount()):
        balInfo = bPattern.GetBaluster(i)
        if(balInfo.BalusterFamilyId not in ids and balInfo.BalusterFamilyId != rdb.ElementId.InvalidElementId ):
            ids.append(balInfo.BalusterFamilyId)
    # add excess pattern baluster id
    if (bPattern.ExcessLengthFillBalusterId not in ids and bPattern.ExcessLengthFillBalusterId != rdb.ElementId.InvalidElementId):
        ids.append(bPattern.ExcessLengthFillBalusterId)
    return ids


def GetUsedBalusterPostIds(bPostPattern):
    '''
    Gets list of unique baluster posts ids only.
    Includes:
    - CornerPost
    - EndPost
    - StartPost
    :param bPostPattern: A revit post pattern.
    :type bPostPattern: Autodesk.Revit.DB.Architecture.PostPattern 
    :return: List of element ids of baluster family ids.
    :rtype: list Autodesk.Revit.DB.ElementId
    '''

    ids = []
    # get corner post
    if(bPostPattern.CornerPost.BalusterFamilyId != rdb.ElementId.InvalidElementId):
        ids.append(bPostPattern.CornerPost.BalusterFamilyId)
    # get end post id
    if(bPostPattern.EndPost.BalusterFamilyId != rdb.ElementId.InvalidElementId and bPostPattern.EndPost.BalusterFamilyId not in ids):
        ids.append(bPostPattern.EndPost.BalusterFamilyId)
    # get start post id
    if(bPostPattern.StartPost.BalusterFamilyId != rdb.ElementId.InvalidElementId and bPostPattern.StartPost.BalusterFamilyId not in ids):
        ids.append(bPostPattern.StartPost.BalusterFamilyId)
    return ids


def GetUsedBalusterPerTread(bPlacement):
    '''
    Gets the id of the baluster per stair tread.
    :param bPlacement: A baluster placement element.
    :type bPlacement: Autodesk.Revit.DB.Architecture.BalusterPlacement 
    :return: List of element ids of baluster family ids.
    :rtype: list Autodesk.Revit.DB.ElementId
    '''

    ids = []
    # get baluster per tread
    if(bPlacement.BalusterPerTreadFamilyId != rdb.ElementId.InvalidElementId):
        ids.append(bPlacement.BalusterPerTreadFamilyId)
    return ids


def GetAllBalusterSymbols(doc):
    '''
    Gets all baluster symbols (fam types) in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A filtered element collector of baluster symbols (types).
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    col = rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_StairsRailingBaluster).WhereElementIsElementType()
    return col


def GetAllBalusterSymbolIds(doc):
    '''
    Gets all baluster symbol (fam type) ids in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids of baluster family ids.
    :rtype: list Autodesk.Revit.DB.ElementId
    '''

    ids = []
    col = GetAllBalusterSymbols(doc)
    ids = com.GetIdsFromElementCollector (col)
    return ids


def GetBalusterTypesFromRailings(doc):
    '''
    Gets a list of unique baluster symbol (fam type) ids used in railing types in the model.
    Incl:
    - baluster patterns
    - baluster posts
    - baluster per stair 
    There can be additional baluster symbols in the model. Those belong to loaded families which are not used in\
        any railing type definition.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids of baluster family ids.
    :rtype: list Autodesk.Revit.DB.ElementId
    '''

    ids = []
    railingTypeIds = GetAllRailingTypeIdsInModelByClassAndCategory(doc)
    for rtId in railingTypeIds:
        el = doc.GetElement(rtId)
        # put into try catch since some rail types have no balusters ...top rail
        try:
            balusterPlacement = el.BalusterPlacement
            idsPattern = GetBalustersUsedInPattern(balusterPlacement.BalusterPattern)
            idsPosts = GetUsedBalusterPostIds(balusterPlacement.PostPattern)
            idsPerTread = GetUsedBalusterPerTread(balusterPlacement)
            # build overall ids list
            ids = MergeIntoUniqueList(ids, idsPattern)
            ids = MergeIntoUniqueList(ids, idsPosts)
            ids = MergeIntoUniqueList(ids, idsPerTread)
        except:
            pass
    return ids