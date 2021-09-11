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

# import common library modules
import RevitCommonAPI as com
import Result as res
import Utility as util

# import Autodesk
from Autodesk.Revit.DB import *

clr.ImportExtensions(System.Linq)

# -------------------------------------------- common variables --------------------
# header used in reports
REPORT_GROUPS_HEADER = ['HOSTFILE','ID', 'NAME', 'GROUP TYPE', 'NUMBER OF INSTANCES']

# --------------------------------------------- utility functions ------------------

# doc   current document
def GetModelGroups(doc):
    """returns a list of model groups from the model"""
    return FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_IOSModelGroups).WhereElementIsElementType().ToList()

# doc   current document
def GetDetailGroups(doc):
    """returns a list of detail groups from the model"""
    return FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_IOSDetailGroups).WhereElementIsElementType().ToList()

# doc   current document
def GetNestedDetailGroups(doc):
    """returns a list of nested detail groups from the model"""
    return FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_IOSAttachedDetailGroups).WhereElementIsElementType().ToList()

# doc   current document
def GetModelGroupIds(doc):
    """returns a list of model group ids from the model"""
    ids = []
    col = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_IOSModelGroups).WhereElementIsElementType()
    ids = com.GetIdsFromElementCollector(col)
    return ids

# doc   current document
def GetDetailGroupIds(doc):
    """returns a list of detail groups from the model"""
    ids = []
    rcol = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_IOSDetailGroups).WhereElementIsElementType()
    ids = com.GetIdsFromElementCollector(col)
    return ids

# doc   current document
def GetNestedDetailGroupIds(doc):
    """returns a list of nested detail groups from the model"""
    ids = []
    col = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_IOSAttachedDetailGroups).WhereElementIsElementType()
    ids = com.GetIdsFromElementCollector(col)
    return ids

# doc   current document
# groupCategory     either BuiltInCategory.OST_IOSDetailGroups or BuiltInCategory.OST_IOSModelGroups
def GetNotPlacedGroups(doc, groupCategory):
    """returns a list of unplaced groups from the model"""
    def getterTypes(doc):
        return FilteredElementCollector(doc).OfCategory(groupCategory).WhereElementIsElementType()
    def getterInstances(doc):
        return FilteredElementCollector(doc).OfCategory(groupCategory).WhereElementIsNotElementType()
    # get unplaced groups
    return com.GetNotPlacedTypes(
        doc, 
        getterTypes, 
        getterInstances)

# doc   current document
def GetUnplacedDetailGroups(doc):
    """returns a list of unplaced detail groups from the model
    this will not include any attached detail groups!!"""
    return GetNotPlacedGroups(doc, BuiltInCategory.OST_IOSDetailGroups)

# doc   current document
def GetUnplacedDetailGroupIds(doc):
    """returns a list of unplaced detail groups Ids from the model
    this will not include any attached detail groups!!"""
    unplacedGroups = GetNotPlacedGroups(doc, BuiltInCategory.OST_IOSDetailGroups)
    ids = []
    for unplaced in unplacedGroups:
        ids.append(unplaced.Id)
    return ids

# doc   current document
def GetUnplacedNestedDetailGroups(doc):
    """returns a list of unplaced nested detail groups from the model"""
    return GetNotPlacedGroups(doc, BuiltInCategory.OST_IOSAttachedDetailGroups)

# doc   current document
def GetUnplacedNestedDetailGroupIds(doc):
    """returns a list of unplaced nested detail group Ids from the model. This will not list any none nested detail groups!!"""
    unplacedGroups = GetNotPlacedGroups(doc, BuiltInCategory.OST_IOSAttachedDetailGroups)
    ids = []
    for unplaced in unplacedGroups:
        ids.append(unplaced.Id)
    return ids

# doc   current document
def GetUnplacedModelGroups(doc):
    """returns a list of unplaced model groups from the model"""
    return GetNotPlacedGroups(doc, BuiltInCategory.OST_IOSModelGroups)

# doc   current document
def GetUnplacedModelGroupIds(doc):
    """returns a list of unplaced model group Ids from the model"""
    unplacedGroups = GetNotPlacedGroups(doc, BuiltInCategory.OST_IOSModelGroups)
    ids = []
    for unplaced in unplacedGroups:
        ids.append(unplaced.Id)
    return ids