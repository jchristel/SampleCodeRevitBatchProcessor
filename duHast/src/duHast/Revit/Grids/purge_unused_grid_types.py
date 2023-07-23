"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to purging Revit grids and grid heads. 
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

from duHast.Revit.Family import purge_unused_family_types as rFamUPurge
from duHast.Revit.Common import (
    parameter_get_utils as rParaGet,
    purge_utils as rPurgeUtils,
)
from duHast.Revit.Grids import grids as rGrids


def get_unused_grid_types_for_purge(doc):
    """this will return all ids of unused grid types in the model to be purged"""
    return rPurgeUtils.get_used_unused_type_ids(
        doc, rGrids.get_all_grid_type_ids_by_category, 0, 8
    )


def get_unused_grid_head_families(doc):
    """this will return all ids of unused family symbols (types) of grid head families"""
    used_type_ids = rPurgeUtils.get_used_unused_type_ids(
        doc, rGrids.get_all_grid_type_ids_by_category, 1, 8
    )
    heads_in_use_ids = []
    for id in used_type_ids:
        type = doc.GetElement(id)
        id = rParaGet.get_built_in_parameter_value(
            type, rdb.BuiltInParameter.GRID_HEAD_TAG
        )
        if id != None and id not in heads_in_use_ids:
            heads_in_use_ids.append(id)
    all_symbols_in_model = rGrids.get_all_grid_heads_by_category(doc)
    unused_symbol_ids = []
    for symbol_in_model in all_symbols_in_model:
        if symbol_in_model.Id not in heads_in_use_ids:
            unused_symbol_ids.append(symbol_in_model.Id)
    return unused_symbol_ids


def get_unused_grid_head_families_for_purge(doc):
    """this will return all ids of unused grid head symbols and families to be purged"""
    return rFamUPurge.get_unused_in_place_ids_for_purge(
        doc, get_unused_grid_head_families
    )
