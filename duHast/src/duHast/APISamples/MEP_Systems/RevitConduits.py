'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to Revit conduits.
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
# 

import Autodesk.Revit.DB as rdb
import Autodesk.Revit.DB.Electrical as rdbE

from duHast.APISamples.MEP_Systems.Utility.SymbolsInSystemTypes import get_symbol_ids_of_mep_system_types, get_unique_ids_of_used_symbols_from_system_type_ids
from duHast.APISamples.MEP_Systems.Utility.RevitMEPSystemCategories import CATS_LOADABLE_CONDUITS
from duHast.APISamples.Common import RevitCommonAPI as com


def get_all_conduit_types_by_category(doc):
    '''
    Gets a filtered element collector of all conduit types in the model.
    - with fittings
    - without fittings
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A filtered element collector of conduit types
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    collector = rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_Conduit).WhereElementIsElementType()
    return collector


def get_all_conduit_types_by_class(doc):
    '''
    Gets a filtered element collector of all conduit types in the model.
    - with fittings
    - without fittings
    Will exclude in place families.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A filtered element collector of conduit types
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    return  rdb.FilteredElementCollector(doc).OfClass(rdbE.ConduitType)

def get_all_conduit_instances_by_category(doc):
    '''
    Gets all conduit elements placed in model.
    TODO: check these actually work...
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A filtered element collector of conduit instances
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    collector = rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_Conduit).WhereElementIsNotElementType()
    return collector


def get_all_conduit_instances_by_class(doc):
    '''
    Gets all conduit elements placed in model.
    Will exclude in place families.
    TODO: check these actually work...
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A filtered element collector of conduit instances
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    return  rdb.FilteredElementCollector(doc).OfClass(rdbE.ConduitType).WhereElementIsNotElementType()

def get_all_conduit_type_ids_in_model_by_category(doc):
    '''
    Gets all conduit type ids available in model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A list of ids representing conduit types.
    :rtype: List Autodesk.Revit.DB.ElementId
    '''

    ids = []
    col_cat = get_all_conduit_types_by_category(doc)
    ids = com.get_ids_from_element_collector (col_cat)
    return ids


def get_all_conduit_type_ids_in_model_by_class(doc):
    '''
    Gets all conduit type ids available in model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A list of ids representing conduit types.
    :rtype: List Autodesk.Revit.DB.ElementId
    '''

    ids = []
    col_class = get_all_conduit_types_by_class(doc)
    ids = com.get_ids_from_element_collector (col_class)
    return ids


def get_symbol_ids_used_in_conduit_types(doc):
    '''
    Gets a list of unique symbol ids used in system type properties of conduit types.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of unique ids representing family symbols used in conduit systems.
    :rtype: list  Autodesk.Revit.DB.ElementId
    '''

    ids = []
    tye_ids = get_all_conduit_type_ids_in_model_by_category(doc)
    ids = get_unique_ids_of_used_symbols_from_system_type_ids(doc, tye_ids)
    return ids


def get_symbol_ids_for_conduit_types_in_model(doc):
    '''
    Gets list of symbol ids of the following categories:
    - BuiltInCategory.OST_ConduitFitting
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of ids representing family symbols.
    :rtype: list  Autodesk.Revit.DB.ElementId
    '''

    ids = get_symbol_ids_of_mep_system_types(doc, CATS_LOADABLE_CONDUITS, 'GetSymbolIdsForConduitTypes')
    return ids