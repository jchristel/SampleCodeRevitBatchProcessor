"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Revit areas helper functions.
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

from duHast.Revit.Levels.levels import get_levels_in_model

from Autodesk.Revit.DB import (
    BuiltInCategory,
    CurveElement,
    ElementClassFilter,
    FilteredElementCollector,
    ModelLine,
)


def get_areas_by_scheme_name(doc, scheme_name):
    return_value = []
    areas = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Areas)
    for area in areas:
        if area.AreaScheme.Name == scheme_name:
            return_value.append(area)
    return return_value


def get_area_schemes(doc):
    area_schemes = FilteredElementCollector(doc).OfCategory(
        BuiltInCategory.OST_AreaSchemes
    )
    return area_schemes


def get_area_scheme_by_name(doc, area_scheme_name):
    return_value = None
    area_schemes = get_area_schemes(doc=doc)
    if any(area_schemes):
        for area_scheme in area_schemes:
            if area_scheme.Name == area_scheme_name:
                return area_scheme
    return return_value


def get_area_lines_by_area_scheme_name(doc, scheme_name):
    return_value = []
    area_scheme = get_area_scheme_by_name(doc=doc, area_scheme_name=scheme_name)
    if area_scheme:
        filter = ElementClassFilter(CurveElement)
        dependent_element_ids = area_scheme.GetDependentElements(filter)
        for id in dependent_element_ids:
            element = doc.GetElement(id)
            return_value.append(element)
    return return_value


def sort_area_line_by_level_name(doc, area_lines):
    levels = get_levels_in_model(doc)
    # build level id to level name dictionary
    level_names_by_id = {}
    for l in levels:
        level_names_by_id[l.Id]=l.Name
    # build level name to area lines dictionary
    area_lines_by_Level_name = {}
    for area_line in area_lines:
        if level_names_by_id[area_line.LevelId] in area_lines_by_Level_name:
            area_lines_by_Level_name[level_names_by_id[area_line.LevelId]].append(area_line)
        else:
            area_lines_by_Level_name[level_names_by_id[area_line.LevelId]]=[area_line]
    return area_lines_by_Level_name
