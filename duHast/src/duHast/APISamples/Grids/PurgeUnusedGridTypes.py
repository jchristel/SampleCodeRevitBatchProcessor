'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to purging Revit grids and grid heads. 
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

import Autodesk.Revit.DB as rdb

from duHast.APISamples.Family import PurgeUnusedFamilyTypes as rFamUPurge
from duHast.APISamples.Common import RevitPurgeUtils as rPurgeUtils, RevitElementParameterGetUtils as rParaGet
from duHast.APISamples.Grids import RevitGrids as rGrids 

def get_unused_grid_types_for_purge(doc):
    ''' this will return all ids of unused grid types in the model to be purged'''
    return rPurgeUtils.get_used_unused_type_ids(doc, rGrids.get_all_grid_type_ids_by_category, 0, 8)


def get_unused_grid_head_families(doc):
    ''' this will return all ids of unused family symbols (types) of grid head families'''
    usedTypes = rPurgeUtils.get_used_unused_type_ids(doc, rGrids.get_all_grid_type_ids_by_category, 1, 8)
    headsInUseIds = []
    for Id in usedTypes:
        type = doc.GetElement(Id)
        id = rParaGet.get_built_in_parameter_value(type, rdb.BuiltInParameter.GRID_HEAD_TAG)
        if (id != None and id not in headsInUseIds):
            headsInUseIds.append(id)
    allSymbolsInModel = rGrids.get_all_grid_heads_by_category(doc)
    unusedSymbolIds = []
    for  symbolInModel in  allSymbolsInModel:
        if(symbolInModel.Id not in headsInUseIds ):
            unusedSymbolIds.append(symbolInModel.Id)
    return unusedSymbolIds


def get_unused_grid_head_families_for_purge(doc):
    ''' this will return all ids of unused grid head symbols and families to be purged'''
    return rFamUPurge.get_unused_in_place_ids_for_purge(doc, get_unused_grid_head_families)