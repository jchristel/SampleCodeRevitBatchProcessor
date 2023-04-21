'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to Revit ramps.
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
from duHast.Revit.Ramps.Utility import RevitRampsFilter as rRampFilter

# --------------------------------------------- utility functions ------------------

def get_all_ramp_types_by_category(doc):
    '''
    Gets a filtered element collector of all Ramp types in the model.

    :param doc: _description_
    :type doc: _type_

    :return: A filtered element collector containing ramp types.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    collector = rRampFilter._get_all_ramp_types_by_category(doc)
    return collector

# -------------------------------- none in place Ramp types -------------------------------------------------------

def get_all_ramp_instances_by_category(doc):
    '''
    Gets all ramp elements placed in model...ignores in place families (to be confirmed!)

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector containing ramp instances.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    return rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_Ramps).WhereElementIsNotElementType()

def get_all_ramp_types_ids_by_category(doc):
    '''
    Gets all ramp element type ids available in model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of element ids of ramp types.
    :rtype: List Autodesk.Revit.DB.ElementId
    '''

    ids = []
    col_cat = get_all_ramp_types_by_category(doc)
    ids = com.get_ids_from_element_collector (col_cat)
    return ids