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

import RevitCommonAPI as com
import Result as res
import Utility as util

BASIC_RAMP_FAMILY_NAME = 'Ramp'

BUILTIN_RAMP_TYPE_FAMILY_NAMES = [
    BASIC_RAMP_FAMILY_NAME,
]

# import Autodesk
from Autodesk.Revit.DB import *

clr.ImportExtensions(System.Linq)

# -------------------------------------------- common variables --------------------
# header used in reports
REPORT_RAMPS_HEADER = ['HOSTFILE', 'RAMPTYPEID', 'RAMPTYPENAME']

# --------------------------------------------- utility functions ------------------

# returns all wall types in a model
# doc:   current model document
def GetAllRampTypesByCategory(doc):
    """ this will return a filtered element collector of all Ramp types in the model:
    - Ramp
    """
    collector = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Ramps).WhereElementIsElementType()
    return collector


# collector   fltered element collector containing Ramp type elments of family symbols representing in place families
# dic         dictionary containing key: wall type family name, value: list of ids
def BuildRampTypeDictionary(collector, dic):
    """returns the dictioanry passt in with keys and or values added retrieved from collector passt in"""
    for c in collector:
        if(dic.has_key(c.FamilyName)):
            # todo : check WallKind Enum???
            if(c.Id not in dic[c.FamilyName]):
                dic[c.FamilyName].append(c.Id)
        else:
            dic[c.FamilyName] = [c.Id]
    return dic

# doc   current model document
def SortRampTypesByFamilyName(doc):
    # get all Wall Type Elements
    #wts = GetRampTypesByClass(doc)
    # get all wall types including in place wall families
    wts_two = GetAllRampTypesByCategory(doc)
    usedWts = {}
    #usedWts = BuildRampTypeDictionary(wts, usedWts)
    usedWts = BuildRampTypeDictionary(wts_two, usedWts)
    return usedWts

# doc             current document
# useTyep         0, no dependent elements; 1: has dependent elements
# typeIdGetter    list of type ids to be checked for dependent elements
def GetUsedUnusedTypeIds(doc, typeIdGetter, useType = 0):
    # get all types elements available
    allWallTypeIds = typeIdGetter(doc)
    ids = []
    for wallTypeId in allWallTypeIds:
        wallType = doc.GetElement(wallTypeId)
        # set a threshold value of 4 for ramps
        # graphic style
        # element type
        # ramp type itself
        # ???
        hasDependents = com.HasDependentElements(doc, wallType, None, 4)
        if(hasDependents == useType):
            ids.append(wallTypeId)
    return ids

# -------------------------------- none in place Ramp types -------------------------------------------------------

# doc   current model document
def GetAllRampInstancesInModelByCategory(doc):
    """ returns all Ramp elements placed in model...ignores in place families"""
    return FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Ramps).WhereElementIsNotElementType()

# doc   current model document
def GetAllRampTypeIdsInModelByCategory(doc):
    """ returns all Ramp element type ids by category available in model """
    ids = []
    colCat = GetAllRampTypesByCategory(doc)
    ids = com.GetIdsFromElementCollector (colCat)
    return ids

# doc   current document
def GetUsedRampTypeIds(doc):
    """ returns all used in Ramp type ids """
    ids = GetUsedUnusedTypeIds(doc, GetAllRampTypeIdsInModelByCategory, 1)
    return ids

# famTypeIds        symbol(type) ids of a family
# usedTypeIds       symbol(type) ids in use in a project
def FamilyNoTypesInUse(famTypeIds,unUsedTypeIds):
    """ returns false if any symbols (types) of a family are in use in a model"""
    match = True
    for famTypeId in famTypeIds:
        if (famTypeId not in unUsedTypeIds):
            match = False
            break
    return match
 
# doc   current document
def GetUnusedNonInPlaceRampTypeIdsToPurge(doc):
    """ returns all unused Ramp type ids for:
    - Ramp 
    ramps do not have in place families ..."""
    # get unused type ids
    ids = GetUsedUnusedTypeIds(doc, GetAllRampTypeIdsInModelByCategory, 0)
    # make sure there is at least on Ramp type per system family left in model
    RampTypes = SortRampTypesByFamilyName(doc)
    for key, value in RampTypes.items():
        if(key in BUILTIN_RAMP_TYPE_FAMILY_NAMES):
            if(FamilyNoTypesInUse(value,ids) == True):
                # remove one type of this system family from unused list
                ids.remove(value[0])
    return ids

# -------------------------------- In place Ramp types -------------------------------------------------------
# no such thing in Revit!!