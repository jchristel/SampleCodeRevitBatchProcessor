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

import sys
sys.path.append('C:\Users\jchristel\Documents\deployRevitBP')

import RevitCommonAPI as com
import RevitFamilyUtils as rFam
import RevitAnnotation as rAnno
from timer import Timer

# import Autodesk
from Autodesk.Revit.DB import *
from Autodesk.Revit.DB.Architecture import *

clr.ImportExtensions(System.Linq)

# -------------------------------------------- common variables --------------------
# header used in reports
REPORT_GENERIC_ANNOTATIONS_HEADER = ['HOSTFILE', 'GENERICANNOTATIONTYPEID', 'GENERICANNOTATIONTYPENAME']


# --------------------------------------------- utility functions ------------------

# returns all  GenericAnnotation types in a model
# doc:   current model document
def GetAllGenericAnnotationTypesByCategory(doc):
    """ this will return a filtered element collector of all GenericAnnotation types in the model """
    collector = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_GenericAnnotation).WhereElementIsElementType()
    return collector

# returns all  GenericAnnotation types in a model
# doc:   current model document
def GetAllGenericAnnotationTypeIdsByCategory(doc):
    """ this will return a filtered element collector of all GenericAnnotation types (symbols) in the model excluding shared families"""
    ids = []
    col = GetAllGenericAnnotationTypesByCategory(doc)
    for c in col:
        parameterMatch = False
        # get the family object to checkwhether it is a shared family
        fam = c.Family
        paras = fam.GetOrderedParameters()
        for p in paras:
            if(p.Definition.BuiltInParameter == BuiltInParameter.FAMILY_SHARED):
                parameterMatch = True
                if(com.getParameterValue(p) == 'No' and c.Id not in ids):
                    ids.append(c.Id)
                    break
        if(parameterMatch == False):
            # family cant be of type shared...
            ids.append(c.Id)
    return ids
 
# collector   fltered element collector containing GenericAnnotation type elments of family symbols 
# dic         dictionary containing key: GenericAnnotation type family name, value: list of ids
def BuildGenericAnnotationTypesDictionary(collector, dic):
    """returns the dictionary passt in with keys and or values added retrieved from collector passt in"""
    for c in collector:
        if(dic.has_key(c.FamilyName)):
            if(c.Id not in dic[c.FamilyName]):
                dic[c.FamilyName].append(c.Id)
        else:
            dic[c.FamilyName] = [c.Id]
    return dic

# doc   current model document
def SortGenericAnnotationTypesByFamilyName(doc):
    # get all GenericAnnotation types
    wts_two = GetAllGenericAnnotationTypesByCategory(doc)
    usedWts = {}
    usedWts = BuildGenericAnnotationTypesDictionary(wts_two, usedWts)
    return usedWts


# doc   current model document
def GetUsedGenericAnnotationTypeIds(doc):
    """returns all used generic annotation symbol ids ( used in model as well as dimension types)"""
    ids = []
    # get ids from symbols used in dim types
    idsDimTypes = rAnno.GetSymbolIdsFromDimTypes(doc)
    # get ids from symbols used in spots
    idsSpots = rAnno.GetSymbolIdsFromSpotTypes(doc)
    # get detail types used in model
    idsUsedInModel = com.GetUsedUnusedTypeIds(doc, GetAllGenericAnnotationTypeIdsByCategory, 1)
    # build overall list
    for id in idsUsedInModel:
        ids.append(id)
    for id in idsDimTypes:
        if(id not in ids):
            ids.append(id)
    for id in idsSpots:
        if (id not in ids):
            ids.append(id)
    return ids
    
# doc   current model document
def GetUnusedGenericAnnotationTypeIds(doc):
    """returns all unsued annotation symbol ids ( unused in model as well as dimension types)"""
    ids = []
    idsUsed = GetUsedGenericAnnotationTypeIds(doc)
    idsAll = GetAllGenericAnnotationTypeIdsByCategory(doc)
    for id in idsAll:
        if (id not in idsUsed):
            ids.append(id)
    return ids

# --------------------------------------------- purge functions ------------------

# doc   current document
def GetUnusedGenericAnnotationIdsForPurge(doc):
    """returns symbol(type) ids and family ids (when no type is in use) of in generic anno familis which can be purged"""
    ids = rFam.GetUnusedInPlaceIdsForPurge(doc, GetUnusedGenericAnnotationTypeIds)
    return ids