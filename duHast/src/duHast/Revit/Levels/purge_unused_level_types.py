"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to purging Revit levels and level heads. 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright © 2023, Jan Christel
# All rights reserved.

# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

# - Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# - Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# - Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
#
# This software is provided by the copyright holder "as is" and any express or implied warranties, including, but not limited to, the implied warranties of merchantability and fitness for a particular purpose are disclaimed. 
# In no event shall the copyright holder be liable for any direct, indirect, incidental, special, exemplary, or consequential damages (including, but not limited to, procurement of substitute goods or services; loss of use, data, or profits; 
# or business interruption) however caused and on any theory of liability, whether in contract, strict liability, or tort (including negligence or otherwise) arising in any way out of the use of this software, even if advised of the possibility of such damage.
#
#
#

import Autodesk.Revit.DB as rdb

from duHast.Revit.Family import purge_unused_family_types as rFamPurge
from duHast.Revit.Common import (
    parameter_get_utils as rParaGet,
    purge_utils as rPurgeUtils,
)
from duHast.Revit.Levels import levels as rLevel


def get_unused_level_types_for_purge(doc):
    """
    Gets all ids of unused level types in the model.
    Unused: not one instance per level type is placed in the model.
    This method can be used to safely delete unused level types from the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A list of level type ids.
    :rtype: list of Autodesk.Revit.DB.ElementId
    """

    return rPurgeUtils.get_used_unused_type_ids(
        doc, rLevel.get_all_level_type_ids_by_category, 0, 6
    )


def get_unused_level_head_families(doc):
    """
    Gets all ids of unused family symbols (types) of level head families.
    Unused: not one instance per symbol is placed in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A list of symbol ids.
    :rtype: list of Autodesk.Revit.DB.ElementId
    """

    usedTypes = rPurgeUtils.get_used_unused_type_ids(
        doc, rLevel.get_all_level_type_ids_by_category, 1, 6
    )
    headsInUseIds = []
    # get family symbol in use at level as symbol
    for lId in usedTypes:
        type = doc.GetElement(lId)
        id = rParaGet.get_built_in_parameter_value(
            type, rdb.BuiltInParameter.LEVEL_HEAD_TAG
        )
        if id != None and id not in headsInUseIds:
            headsInUseIds.append(id)
    # get all level head symbols available
    allSymbolsInModel = rLevel.get_all_level_heads_by_category(doc)
    unusedSymbolIds = []
    # filter out unused level head symbols and add to list to be returned
    for levelSymbolInModel in allSymbolsInModel:
        if levelSymbolInModel.Id not in headsInUseIds:
            unusedSymbolIds.append(levelSymbolInModel.Id)
    return unusedSymbolIds


def get_unused_level_head_families_for_purge(doc):
    """
    Gets ids of all unused level head symbols and families.
    Unused: not one instance per level symbol is placed in the model.
    This method can be used to safely delete unused level symbols or families from the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A list of symbol and or family ids.
    :rtype: list of Autodesk.Revit.DB.ElementId
    """

    return rFamPurge.get_unused_in_place_ids_for_purge(
        doc, get_unused_level_head_families
    )
