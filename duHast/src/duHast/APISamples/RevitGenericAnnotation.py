'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Revit generic annotation helper functions.
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

import sys
#sys.path.append('C:\Users\jchristel\Documents\deployRevitBP')

from duHast.APISamples import RevitCommonAPI as com
from duHast.APISamples import RevitElementParameterGetUtils as rParaGet
from duHast.APISamples import RevitFamilyUtils as rFam
from duHast.APISamples import RevitAnnotation as rAnno

# import Autodesk
import Autodesk.Revit.DB as rdb

# -------------------------------------------- common variables --------------------
#: header used in reports
REPORT_GENERIC_ANNOTATIONS_HEADER = ['HOSTFILE', 'GENERICANNOTATIONTYPEID', 'GENERICANNOTATIONTYPENAME']


# --------------------------------------------- utility functions ------------------

# returns all  GenericAnnotation types in a model
# doc:   current model document
def GetAllGenericAnnotationTypesByCategory(doc):
    '''
    This will return a filtered element collector of all GenericAnnotation types in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: _description_
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    collector = rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_GenericAnnotation).WhereElementIsElementType()
    return collector

# returns all  GenericAnnotation types in a model
# doc:   current model document
def GetAllGenericAnnotationTypeIdsByCategory(doc):
    '''
    This will return a list of all GenericAnnotation types (symbols) id's in the model excluding shared families.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    
    :return: _description_
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    ids = []
    col = GetAllGenericAnnotationTypesByCategory(doc)
    for c in col:
        parameterMatch = False
        # get the family object to check whether it is a shared family
        fam = c.Family
        id =  rParaGet.get_built_in_parameter_value(fam, rdb.BuiltInParameter.FAMILY_SHARED)
        if(id != None):
            parameterMatch = True
            if(id == 'No' and c.Id not in ids):
                ids.append(c.Id)
        if(parameterMatch == False):
            # family cant be of type shared...
            ids.append(c.Id)
    return ids

def BuildGenericAnnotationTypesDictionary(collector, dic):
    '''
    Returns the dictionary past in with keys and or values added retrieved from collector past in.

    :param collector: Filtered element collector containing GenericAnnotation type elements of family symbols.
    :type collector: Autodesk.Revit.DB.FilteredElementCollector
    :param dic: Dictionary, the key is the family name and the value a list of element ids representing annotation types.
    :type dic: dic: key str, values list of Autodesk.Revit.DB.ElementId
    
    :return: Past in expanded by values from collector. Dictionary the key is the Family name and the value a list of element ids.
    :rtype: dic: key str, values list of Autodesk.Revit.DB.ElementId
    '''

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
    '''
    Returns all used generic annotation symbol ids ( used in model as well as dimension types)

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    
    :return: _description_
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

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
    '''
    Returns all unused annotation symbol ids ( unused in model as well as dimension types)

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: _description_
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

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
    '''
    returns symbol(type) ids and family ids (when no type is in use) of in generic anno families which can be purged

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: _description_
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    ids = rFam.GetUnusedInPlaceIdsForPurge(doc, GetUnusedGenericAnnotationTypeIds)
    return ids