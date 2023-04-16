'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Revit building pads helper functions.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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
from duHast.APISamples.BuildingPads.Utility import RevitBuildingPadsFilter as rBuildingPadFilter

# import Autodesk
import Autodesk.Revit.DB as rdb

# --------------------------------------------- utility functions ------------------

def get_all_building_pad_types_by_category(doc):
    '''
    Gets a filtered element collector of all BuildingPad types in the model.
    
    - Basic BuildingPad
    
    Filters by category.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector containing building pad types.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    collector = rBuildingPadFilter._get_all_building_pad_types_by_category(doc)
    return collector

def get_building_pad_types_by_class(doc):
    '''
    Gets a filtered element collector of all building pad types in the model:

    - Basic BuildingPad
    
    Filters by class.
    Since there are no in place families of type building pad possible, this should return the same elements as the by category filter.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector containing building pad types.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    collector =  rBuildingPadFilter._get_building_pad_types_by_class(doc)
    return  collector

# -------------------------------- none in place BuildingPad types -------------------------------------------------------

def get_all_building_pad_instances_in_model_by_category(doc):
    '''
    Gets all building pad elements placed in model.

    Filters by category.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector containing ceiling instances.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''
    
    return rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_BuildingPad).WhereElementIsNotElementType()
    
def get_all_building_pad_instances_in_model_by_class(doc):
    '''
    Gets all building pad elements placed in model.

    Filters by class.
    Since there are no in place families of type building pad possible, this should return the same elements as the by category filter.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector containing ceiling instances.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''
   
    return rdb.FilteredElementCollector(doc).OfClass(rdb.BuildingPad).WhereElementIsNotElementType()

def get_all_building_pad_type_ids_in_model_by_category(doc):
    '''
    Gets all building pad element type ids available in model.

    Filters by category.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector containing building pad type ids.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    ids = []
    col_cat = get_all_building_pad_types_by_category(doc)
    ids = com.get_ids_from_element_collector (col_cat)
    return ids

def get_all_building_pad_type_ids_in_model_by_class(doc):
    '''
    Gets all building pad element type ids available in model.

    Filters by class.
    Since there are no in place families of type building pad possible, this should return the same elements as the by category filter.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    
    :return: A filtered element collector containing building pad type ids.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    ids = []
    col_class = get_building_pad_types_by_class(doc)
    ids = com.get_ids_from_element_collector (col_class)
    return ids


