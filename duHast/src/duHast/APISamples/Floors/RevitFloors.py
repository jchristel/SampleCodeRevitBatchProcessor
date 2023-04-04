'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Revit floors helper functions.
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
import System

from duHast.APISamples.Common import RevitCommonAPI as com
from duHast.APISamples.Family import RevitFamilyUtils as rFam

# import Autodesk
import Autodesk.Revit.DB as rdb

from duHast.APISamples.Floors.Utility import RevitFloorsFilter as rFloorFilter

#: Built in family name for standard floor
FLOOR_FAMILY_NAME = 'Floor'
#: Built in family name for a foundation slab
FOUNDATION_SLAB_FAMILY_NAME = 'Foundation Slab'

#: List of all Built in floor family names
BUILTIN_FLOOR_TYPE_FAMILY_NAMES = [
    FLOOR_FAMILY_NAME,
    FOUNDATION_SLAB_FAMILY_NAME
]

# --------------------------------------------- utility functions ------------------

def GetAllFloorTypesByCategory(doc):
    '''
    Gets a filtered element collector of all ceiling types in the model:

    - Compound Ceiling
    - In place families or loaded families
    - Basic Ceiling

    Filters by category.
    It will therefore not return any roof soffit types ..

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector containing ceiling types.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    collector = rFloorFilter._get_all_ceiling_types_by_category(doc)
    return collector

def GetFloorTypesByClass(doc):
    '''
    Gets a filtered element collector of all ceiling types in the model:

    - Roof Soffit
    - Compound Ceiling
    - Basic Ceiling

    Filters by class.
    It will therefore not return any in place family types.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector containing ceiling types.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    collector = rFloorFilter._get_ceiling_types_by_class(doc)
    return  collector

# -------------------------------- none in place Floor types -------------------------------------------------------

def GetAllFloorInstancesInModelByCategory(doc):
    '''
    Gets all floor elements placed in model...ignores in foundation slabs.

    Filters by builtin category.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector containing floor instances.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    return rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_Floors).WhereElementIsNotElementType()

def GetAllFloorInstancesInModelByClass(doc):
    '''
    Gets all floor elements placed in model...ignores in place families of category floor.

    Filters by class.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector containing floor instances.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    return rdb.FilteredElementCollector(doc).OfClass(rdb.Floor).WhereElementIsNotElementType()

def GetAllFloorTypeIdsInModelByCategory(doc):
    '''
    Returns all Floor element types available in model.

    Filters by builtin category.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector containing floor types.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    ids = []
    colCat = GetAllFloorTypesByCategory(doc)
    ids = com.GetIdsFromElementCollector (colCat)
    return ids

def GetAllFloorTypeIdsInModelByClass(doc):
    '''
    Returns all Floor element types available in model.

    Filters by class.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector containing floor types.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    ids = []
    colClass = GetFloorTypesByClass(doc)
    ids = com.GetIdsFromElementCollector(colClass)
    return ids

# -------------------------------- In place Floor types -------------------------------------------------------

def GetInPlaceFloorFamilyInstances(doc):
    '''
    Gets all instances of in place families of category floor.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector containing floor family instances.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    filter = rdb.ElementCategoryFilter(rdb.BuiltInCategory.OST_Floors)
    return rdb.FilteredElementCollector(doc).OfClass(rdb.FamilyInstance).WherePasses(filter)

def GetAllInPlaceFloorTypeIdsInModel(doc):
    '''
    Gets type ids off all available in place families symbols (types) of category floor.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of element ids representing in place floor symbols (types).
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    ids = rFam.GetAllInPlaceTypeIdsInModelOfCategory(doc, rdb.BuiltInCategory.OST_Floors)
    return ids