'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to Revit roofs. 
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

# import Autodesk
import Autodesk.Revit.DB as rdb

from duHast.Revit.Common import common as com
from duHast.Revit.Family import family_utils as rFam
from duHast.Revit.Roofs.Utility import RevitRoofsFilter as rRoofFilter

# --------------------------------------------- utility functions ------------------

def get_all_roof_types_by_category(doc):
    '''
    Gets a filtered element collector of all roof types in the model.

    - Basic Roof
    - In place families or loaded families
    - sloped glazing

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector containing roof types.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    collector = rRoofFilter._get_all_roof_types_by_category(doc)
    return collector

def get_all_roof_types_by_class(doc):
    '''
    Gets a filtered element collector of all Roof types in the model:

    - Basic Roof
    - sloped glazing

    Since this is based of class roof it will therefore not return any in place family types!

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector containing roof types.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    collector = rRoofFilter._get_roof_types_by_class(doc)
    return  collector

# -------------------------------- none in place Roof types -------------------------------------------------------

def get_all_roof_instances_by_category(doc):
    '''
    Gets all Roof elements placed in model...ignores in place families (to be confirmed!)

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector containing roof instances.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    return rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_Roofs).WhereElementIsNotElementType()

def get_all_roof_instances_by_class(doc):
    '''
    Gets all Roof elements placed in model...ignores roof soffits(???)

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector containing roof instances.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    return rdb.FilteredElementCollector(doc).OfClass(rdb.Roof).WhereElementIsNotElementType()

def get_all_roof_type_ids_by_category(doc):
    '''
    Gets all Roof element type ids available in model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of element ids of roof types.
    :rtype: List Autodesk.Revit.DB.ElementId
    '''

    ids = []
    col_cat = get_all_roof_types_by_category(doc)
    ids = com.get_ids_from_element_collector (col_cat)
    return ids

def get_all_roof_type_ids_by_class(doc):
    '''
    Gets all Roof element type ids available in model.

    :param doc: _description_
    :type doc: _type_

    :return: List of element ids of roof types.
    :rtype: List Autodesk.Revit.DB.ElementId
    '''

    ids = []
    col_class = get_all_roof_types_by_class(doc)
    ids = com.get_ids_from_element_collector(col_class)
    return ids

# -------------------------------- In place Roof types -------------------------------------------------------

def get_in_place_roof_family_instances(doc):
    '''
    Gets all instances of in place families of category roof in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector containing roof family instances.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''
    
    filter = rdb.ElementCategoryFilter(rdb.BuiltInCategory.OST_Roofs)
    return rdb.FilteredElementCollector(doc).OfClass(rdb.FamilyInstance).WherePasses(filter)

def get_all_in_place_roof_type_ids(doc):
    '''
    Gets type ids off all available in place families of category roof in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of element ids of in place roof types.
    :rtype: List Autodesk.Revit.DB.ElementId
    '''

    ids = rFam.get_all_in_place_type_ids_in_model_of_category(doc, rdb.BuiltInCategory.OST_Roofs)
    return ids