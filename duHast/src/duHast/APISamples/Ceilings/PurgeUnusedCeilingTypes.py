'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to purging Revit ceilings. 
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

from duHast.APISamples.Family import PurgeUnusedFamilyTypes as rFamPurge
from duHast.APISamples.Common import RevitPurgeUtils as rPurgeUtils
from duHast.APISamples.Ceilings import RevitCeilings as rCeiling
from duHast.APISamples.Ceilings.Utility import RevitCeilingsTypeSorting as rCeilingTypeSort


#: Built in family name for compound ceilings
COMPOUND_CEILING_FAMILY_NAME = 'Compound Ceiling'

#: Built in family name for basic ceilings
BASIC_CEILING_FAMILY_NAME = 'Basic Ceiling'

#: Built in family name for roof soffits
ROOF_SOFFIT_FAMILY_NAME = 'Roof Soffit'

#: List of all Built in ceiling family names
BUILTIN_CEILING_TYPE_FAMILY_NAMES = [
    COMPOUND_CEILING_FAMILY_NAME,
    BASIC_CEILING_FAMILY_NAME,
    ROOF_SOFFIT_FAMILY_NAME
]


def get_used_ceiling_type_ids(doc):
    '''
    Gets all used ceiling type ids.
    Filters by category.
    Used: at least one instance of this type is placed in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids representing used ceiling types.
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    ids = rPurgeUtils.get_used_unused_type_ids(doc, rCeiling.get_all_ceiling_type_ids_in_model_by_category, 1)
    return ids


def family_no_types_in_use(famTypeIds,unUsedTypeIds):
    '''
    Compares two lists of ids. True if any id is not in unUsedTypeIds.
    TODO: check for more generic list comparison and remove this function.
    :param famTypeIds: List of family type ids to check.
    :type famTypeIds: List of Autodesk.Revit.DB.ElementId
    :param unUsedTypeIds: Reference list of ids.
    :type unUsedTypeIds: List of Autodesk.Revit.DB.ElementId
    :return: True if any id from famTypeIds is not in unUsedTypeIds.
    :rtype: bool
    '''

    match = True
    for famTypeId in famTypeIds:
        if (famTypeId not in unUsedTypeIds):
            match = False
            break
    return match


# -------------------------------- In place ceiling types -------------------------------------------------------

def get_unused_non_in_place_ceiling_type_ids_to_purge(doc):
    '''
    Gets all unused ceiling type id's.
    - Roof Soffit
    - Compound Ceiling
    - Basic Ceiling
    This method can be used to safely delete unused ceiling types:
    In the case that no ceiling instance using any of the types is placed this will return all but one type id since\
        Revit requires at least one ceiling type definition to be in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids representing not used ceiling types.
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    # get unused type ids
    ids = rPurgeUtils.get_used_unused_type_ids(doc,  rCeiling.get_all_ceiling_type_ids_in_model_by_class, 0)
    # make sure there is at least on ceiling type per system family left in model
    ceilingTypes = rCeilingTypeSort.sort_ceiling_types_by_family_name(doc)
    for key, value in ceilingTypes.items():
        if(key in BUILTIN_CEILING_TYPE_FAMILY_NAMES):
            if(family_no_types_in_use(value,ids) == True):
                # remove one type of this system family from unused list
                ids.remove(value[0])
    return ids


def get_used_in_place_ceiling_type_ids(doc):
    '''
    Gets all used in place ceiling type ids in the model.
    Used: at least one instance of this type is placed in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids representing used in place ceiling types.
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    ids = rPurgeUtils.get_used_unused_type_ids(doc, rCeiling.get_all_in_place_ceiling_type_ids_in_model, 1)
    return ids


def get_unused_in_place_ceiling_type_ids(doc):
    '''
    Gets all unused in place ceiling type ids in the model.
    Unused: Not one instance of this type is placed in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids representing unused in place ceiling types.
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    ids = rPurgeUtils.get_used_unused_type_ids(doc, rCeiling.get_all_in_place_ceiling_type_ids_in_model, 0)
    return ids


def get_unused_in_place_ceiling_ids_for_purge(doc):
    '''
    Gets symbol(type) ids and family ids (when no type is in use) of in place ceiling families which can be safely deleted from the model.
    This method can be used to safely delete unused in place ceiling types. There is no requirement by Revit to have at least one\
        in place ceiling definition in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids representing unused in place ceiling types and families.
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    ids = rFamPurge.GetUnusedInPlaceIdsForPurge(doc, get_unused_in_place_ceiling_type_ids)
    return ids

