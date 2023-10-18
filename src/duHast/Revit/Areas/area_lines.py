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

# required for ToList() call
import clr

clr.AddReference("System.Core")
from System import Linq

clr.ImportExtensions(Linq)

from duHast.Revit.Levels.levels import get_levels_in_model
from duHast.Revit.Common.transaction import in_transaction
from duHast.Utilities.Objects import result as res

from duHast.Revit.Areas.areas import get_area_scheme_by_name

from Autodesk.Revit.DB import (
    CurveElement,
    ElementId,
    ElementClassFilter,
    Transaction,
)


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
        level_names_by_id[l.Id] = l.Name
    # build level name to area lines dictionary
    area_lines_by_Level_name = {}
    for area_line in area_lines:
        if level_names_by_id[area_line.LevelId] in area_lines_by_Level_name:
            area_lines_by_Level_name[level_names_by_id[area_line.LevelId]].append(
                area_line
            )
        else:
            area_lines_by_Level_name[level_names_by_id[area_line.LevelId]] = [area_line]
    return area_lines_by_Level_name


def delete_area_lines_by_level_name(
    doc, level_name, area_lines, transaction_manager=in_transaction
):
    return_value = res.Result()
    area_lines_return = area_lines
    # sort area lines by level
    lines_by_level_name = sort_area_line_by_level_name(doc=doc, area_lines=area_lines)
    if level_name in lines_by_level_name:
        element_ids_to_delete = []
        # get the ids to delete
        for element in lines_by_level_name[level_name]:
            element_ids_to_delete.append(element.Id)

        # define delete action
        def action():
            action_return_value = res.Result()
            try:
                element_ids_deleted = doc.Delete(
                    element_ids_to_delete.ToList[ElementId]()
                )
                action_return_value.update_sep(
                    True,
                    "Deleted {} area lines on level{}.".format(
                        len(element_ids_deleted), level_name
                    ),
                )
                action_return_value.result.append(element_ids_deleted)
            except Exception as e:
                action_return_value.update_sep(
                    False,
                    "Failed to delete {} area separation line(s) on level {} with exception: {}".format(
                        len(element_ids_to_delete), level_name, e
                    ),
                )
            return action_return_value

        tranny = Transaction(doc, "Deleting area lines on level: {}".format(level_name))
        result_delete = transaction_manager(tranny, action, doc)
        return_value.update(result_delete)

        # return list of lines not deleted!
        if result_delete.status:
            lines_by_level_name.pop(level_name, None)
            area_lines_return = []
            for key, value in lines_by_level_name.items():
                area_lines_return.extend(value)
        return_value.result = [area_lines_return]

    else:
        return_value.update_sep(True, "No lines on level {} found.".format(level_name))
    return return_value


def copy_area_lines_to_level_name(
    doc, level_name, area_lines, transaction_manager=in_transaction
):
    return_value = res.Result()
    try:
        # sort area lines by level
        lines_by_level_name = sort_area_line_by_level_name(doc=doc, area_lines=area_lines)
        # make sure only one level was returned and its not the level to be copied to!
        if(len(lines_by_level_name)!= 1):
            raise ValueError ("Source area lines must all be on the same level. Found {} levels instead.".format(len(lines_by_level_name)))
        elif(level_name in lines_by_level_name):
            raise ValueError("Source {} and destination {} level are identical!".format(level_name))
        else:

            pass
    except Exception as e:
        return_value.update_sep(
                    False,
                    "Failed to copy {} area separation line(s) to level {} with exception: {}".format(
                        len(area_lines), level_name, e
                    ),
                )
    return return_value