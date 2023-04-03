'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of functions around Revit detail items.
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

import clr

clr.AddReference("System.Core")
from System import Linq
clr.ImportExtensions(Linq)

# import common library modules
from duHast.APISamples.Common import RevitElementParameterGetUtils as rParaGet
from duHast.APISamples.DetailItems.Utility import RevitDetailItemsTypeSorting as rDetailItemTypeSort

# import Autodesk
import Autodesk.Revit.DB as rdb



#: class name Autodesk.Revit.DB.ElementType
ELEMENT_TYPE = 'Autodesk.Revit.DB.ElementType'
#: class name Autodesk.Revit.DB.FilledRegionType
FILLED_REGION_TYPE = 'Autodesk.Revit.DB.FilledRegionType'
#: class name Autodesk.Revit.DB.FamilySymbol
FAMILY_SYMBOL = 'Autodesk.Revit.DB.FamilySymbol'

#: List of class names which can be detailed components
DETAIL_COMPONENT_TYPES = [
    ELEMENT_TYPE,
    FILLED_REGION_TYPE,
    FAMILY_SYMBOL
]

# --------------------------------------------- filled region ------------------

def GetFilledRegionsInModel(doc):
    '''
    Gets all filled region instances in a model.

    Filters by class.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A list containing floor instances.
    :rtype: list Autodesk.Revit.DB.FilledRegion
    '''

    return rdb.FilteredElementCollector(doc).OfClass(rdb.FilledRegion).ToList()



def GetAllFilledRegionTypeIdsAvailable(doc):
    '''
    Gets all filled region types ids in model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A list of element ids representing filled region types.
    :rtype: list Autodesk.Revit.DB.ElementIds
    '''

    dic = rDetailItemTypeSort.BuildDetailTypeIdsDictionary(GetAllDetailTypesByCategory(doc))
    if (dic.has_key(FILLED_REGION_TYPE)):
        return dic[FILLED_REGION_TYPE]
    else:
        return []

'''
TODO: check for actual class...
'''

# -------------------------------- detail components -------------------------------------------------------

def GetAllDetailTypesByCategory(doc):
    '''
    Gets all detail component types in the model.

    Filters by built in category.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector containing detail component types.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    collector = rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_DetailComponents).WhereElementIsElementType()
    return collector

# -------------------------------- repeating detail types -------------------------------------------------------

def GetAllRepeatingDetailTypeIdsAvailable(doc):
    '''
    Get all repeating detail type id's in model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A list of element ids representing repeating detail types.
    :rtype: list Autodesk.Revit.DB.ElementIds
    '''

    dic = rDetailItemTypeSort.BuildDetailTypeIdsDictionary(GetAllDetailTypesByCategory(doc))
    if (dic.has_key(ELEMENT_TYPE)):
        return dic[ELEMENT_TYPE]
    else:
        return []

# -------------------------------- Detail families -------------------------------------------------------

def GetAllDetailSymbolIdsAvailable(doc):
    '''
    Gets all detail symbol (types) ids in model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A list of element ids representing detail symbols.
    :rtype: list Autodesk.Revit.DB.ElementIds
    '''

    dic = rDetailItemTypeSort.BuildDetailTypeIdsDictionary(GetAllDetailTypesByCategory(doc))
    if (dic.has_key(FAMILY_SYMBOL)):
        return dic[FAMILY_SYMBOL]
    else:
        return []

def GetDetailSymbolsUsedInRepeatingDetails(doc, idsRepeatDet):
    '''
    Gets the ids of all symbols used in repeating details.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param idsRepeatDet: List of repeating detail type ids.
    :type idsRepeatDet: list Autodesk.Revit.DB.ElementIds

    :return: List of family symbol (type) ids.
    :rtype: list Autodesk.Revit.DB.ElementIds
    '''

    ids = []
    for idR in idsRepeatDet:
        repeatDetail = doc.GetElement(idR)
        id = rParaGet.get_built_in_parameter_value(repeatDetail, rdb.BuiltInParameter.REPEATING_DETAIL_ELEMENT)
        if(id not in ids and id != rdb.ElementId.InvalidElementId and id != None):
            ids.append(id)
    return ids


