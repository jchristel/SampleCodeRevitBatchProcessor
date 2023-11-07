"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of functions around Revit doors.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2023, Jan Christel
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

from Autodesk.Revit.DB import (
    BuiltInCategory,
    BuiltInParameter,
    CopyPasteOptions,
    Dimension,
    Element,
    ElementCategoryFilter,
    ElementClassFilter,
    ElementId,
    ElementTransformUtils,
    FamilySymbol,
    FilteredElementCollector,
    FamilyInstance,
    Grid,
    Panel,
    SpotDimension,
    Transaction,
    Transform,
    ViewType,
    WallKind,
)


def get_curtain_wall_door_symbols(doc, ignore_families=[]):
    # get all door symbols in model
    curtain_wall_door_symbols = []
    filter = ElementCategoryFilter(BuiltInCategory.OST_Doors)
    door_symbols_in_model = (
        FilteredElementCollector(doc).OfClass(FamilySymbol).WherePasses(filter)
    )
    # get all panel symbols in model
    filter_panels = ElementCategoryFilter(BuiltInCategory.OST_CurtainWallPanels)
    panels_in_model = (
        FilteredElementCollector(doc).OfClass(FamilySymbol).WherePasses(filter_panels)
    )
    # convert panel symbols to ids
    panel_ids = []
    for panel in panels_in_model:
        panel_ids.append(panel.Id)

    # check if similar type query returns any panel id...if so then this is a curtain wall door
    for door_symbol in door_symbols_in_model:
        similar_type_ids = door_symbol.GetSimilarTypes()
        for panel_id in panel_ids:
            if panel_id in similar_type_ids:
                # found a curtain wall door
                if Element.Name.GetValue(door_symbol.Family) not in ignore_families:
                    curtain_wall_door_symbols.append(door_symbol)
    return curtain_wall_door_symbols

def get_basic_wall_door_symbols(doc, ignore_families=[]):
    # get all door symbols in model
    basic_wall_door_symbols = []
    filter = ElementCategoryFilter(BuiltInCategory.OST_Doors)
    door_symbols_in_model = (
        FilteredElementCollector(doc).OfClass(FamilySymbol).WherePasses(filter)
    )
    # get curtain wall door symbols
    curtain_wall_door_symbols = get_curtain_wall_door_symbols(
        doc=doc, ignore_families=ignore_families
    )
    # get curtain wall door symbol ids
    curtain_wall_door_symbol_ids = get_ids_from_element_collector(
        curtain_wall_door_symbols
    )
    # compare all door symbols in model with curtain wall door symbol ids
    for door_symbol in door_symbols_in_model:
        if door_symbol.Id not in curtain_wall_door_symbol_ids:
            basic_wall_door_symbols.append(door_symbol)
    return basic_wall_door_symbols
