'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Revit groups helper functions.
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
clr.AddReference("System.Core")
from System import Linq
clr.ImportExtensions(Linq)
import System

# import common library modules
from duHast.APISamples import RevitCommonAPI as com

# import Autodesk
import Autodesk.Revit.DB as rdb

# -------------------------------------------- common variables --------------------
#: header used in reports
REPORT_GROUPS_HEADER = ['HOSTFILE','ID', 'NAME', 'GROUP TYPE', 'NUMBER OF INSTANCES']

# --------------------------------------------- utility functions ------------------

# doc   current document
def GetModelGroups(doc):
    '''
    Get all model group types from the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: list of model group types in the model
    :rtype: list of Autodesk.Revit.DB.
    '''

    return rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_IOSModelGroups).WhereElementIsElementType().ToList()

def GetDetailGroups(doc):
    '''
    Gets all detail groups in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A list containing detail group types.
    :rtype: list
    '''

    return rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_IOSDetailGroups).WhereElementIsElementType().ToList()

def GetNestedDetailGroups(doc):
    '''
    Gets all nested detail groups in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A list containing nested detail group types.
    :rtype: list
    '''

    return rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_IOSAttachedDetailGroups).WhereElementIsElementType().ToList()

def GetModelGroupIds(doc):
    '''
    Gets a list of all model group type ids in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of model group type ids
    :rtype: List of Autodesk.Revit.DB.ElementId
    '''

    ids = []
    col = rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_IOSModelGroups).WhereElementIsElementType()
    ids = com.GetIdsFromElementCollector(col)
    return ids

def GetDetailGroupIds(doc):
    '''
    Gets a list of all detail group types from the model.

    This will not include any attached detail groups.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of detail group type ids
    :rtype: List of Autodesk.Revit.DB.ElementId
    '''

    ids = []
    col = rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_IOSDetailGroups).WhereElementIsElementType()
    ids = com.GetIdsFromElementCollector(col)
    return ids

def GetNestedDetailGroupIds(doc):
    '''
    Gets a list of all nested detail group types from the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of nested detail group type ids
    :rtype: List of Autodesk.Revit.DB.ElementId
    '''

    ids = []
    col = rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_IOSAttachedDetailGroups).WhereElementIsElementType()
    ids = com.GetIdsFromElementCollector(col)
    return ids
   
def GetNotPlacedGroups(doc, groupCategory):
    '''
    Gets a list of unplaced groups from the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param groupCategory: A built in category defining the group category (model vs detail)
    :type groupCategory: either BuiltInCategory.OST_IOSDetailGroups or BuiltInCategory.OST_IOSModelGroups
    
    :return: List of unplaced group types
    :rtype: list
    '''

    def getterTypes(doc):
        return rdb.FilteredElementCollector(doc).OfCategory(groupCategory).WhereElementIsElementType()
    def getterInstances(doc):
        return rdb.FilteredElementCollector(doc).OfCategory(groupCategory).WhereElementIsNotElementType()
    # get unplaced groups
    return com.GetNotPlacedTypes(
        doc, 
        getterTypes, 
        getterInstances)

def GetUnplacedDetailGroups(doc):
    '''
    Gets a list of unplaced detail groups from the model
    
    This will not include any attached detail groups.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of unplaced detail group types
    :rtype: list
    '''

    return GetNotPlacedGroups(doc, rdb.BuiltInCategory.OST_IOSDetailGroups)

def GetUnplacedDetailGroupIds(doc):
    '''
    Gets a list of unplaced detail groups type Ids from the model.
    
    This will not include any attached detail groups.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of unplaced detail group type ids
    :rtype: List of Autodesk.Revit.DB.ElementId
    '''

    unplacedGroups = GetNotPlacedGroups(doc, rdb.BuiltInCategory.OST_IOSDetailGroups)
    ids = []
    for unplaced in unplacedGroups:
        ids.append(unplaced.Id)
    return ids

def GetUnplacedNestedDetailGroups(doc):
    '''
    Gets a list of unplaced nested detail groups from the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of unplaced nested detail group types
    :rtype: list
    '''

    return GetNotPlacedGroups(doc, rdb.BuiltInCategory.OST_IOSAttachedDetailGroups)

def GetUnplacedNestedDetailGroupIds(doc):
    '''
    Gets a list of unplaced nested detail group Ids from the model. 
    
    This will not list any none nested detail groups.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of unplaced model group type ids
    :rtype: List of Autodesk.Revit.DB.ElementId
    '''

    unplacedGroups = GetNotPlacedGroups(doc, rdb.BuiltInCategory.OST_IOSAttachedDetailGroups)
    ids = []
    for unplaced in unplacedGroups:
        ids.append(unplaced.Id)
    return ids

def GetUnplacedModelGroups(doc):
    '''
    Gets a list of unplaced model groups types from the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of unplaced model group types
    :rtype: list
    '''

    return GetNotPlacedGroups(doc, rdb.BuiltInCategory.OST_IOSModelGroups)

def GetUnplacedModelGroupIds(doc):
    '''
    Gets a list of unplaced model group type Ids from the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of unplaced model group type ids
    :rtype: List of Autodesk.Revit.DB.ElementId
    '''

    unplacedGroups = GetNotPlacedGroups(doc, rdb.BuiltInCategory.OST_IOSModelGroups)
    ids = []
    for unplaced in unplacedGroups:
        ids.append(unplaced.Id)
    return ids