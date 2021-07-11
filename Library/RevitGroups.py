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

# returns a list of model groups from the model
# doc   current document
def GetModelGroups(doc):
    return FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_IOSModelGroups).WhereElementIsElementType().ToList()

# returns a list of detail groups from the model
# doc   current document
def GetDetailGroups(doc):
    return FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_IOSDetailGroups).WhereElementIsElementType().ToList()

# returns a list of nested detail groups from the model
# doc   current document
def GetNestedDetailGroups(doc):
    return FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_IOSAttachedDetailGroups).WhereElementIsElementType().ToList()

# returns a list of unplaced groups from the model
# doc   current document
# groupCategory     either BuiltInCategory.OST_IOSDetailGroups or BuiltInCategory.OST_IOSModelGroups
def GetNotPlacedGroups(doc, groupCategory):
    groupTypes = FilteredElementCollector(doc).OfCategory(groupCategory).WhereElementIsElementType().ToList()
    groupInstances = FilteredElementCollector(doc).OfCategory(groupCategory).WhereElementIsNotElementType().ToList()
    notPlaced = []
    allreadyChecked = []
    # loop over all types and check for matching instances
    for gt in groupTypes:
        match = False
        for gi in groupInstances:
            # check if we had this group type checked allready, if so ignore and move to next
            if(gi.GetTypeId() not in allreadyChecked):
                #  check for type id match
                if(gi.GetTypeId() == gt.Id):
                    # add to allready checked and verified as match list
                    allreadyChecked.append(gi.GetTypeId())
                    match = True
                    break
        if(match == False):
            notPlaced.append(gt)
    return notPlaced

# returns a list of unplaced detail groups from the model
# this will not include any attached detail groups!!
# doc   current document
def GetUnplacedDetailGroups(doc):
    return GetNotPlacedGroups(doc, BuiltInCategory.OST_IOSDetailGroups)

# returns a list of unplaced nested detail groups from the model
# this will not list any none nested detail groups!!
# doc   current document
def GetUnplacedNestedDetailGroups(doc):
    return GetNotPlacedGroups(doc, BuiltInCategory.OST_IOSAttachedDetailGroups)

# returns a list of unplaced model groups from the model
# doc   current document
def GetUnplacedModelGroups(doc):
    return GetNotPlacedGroups(doc, BuiltInCategory.OST_IOSModelGroups)