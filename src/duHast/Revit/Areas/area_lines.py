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

from duHast.Revit.Levels.levels import get_levels_in_model, get_level_elevation_by_name
from duHast.Revit.Common.parameter_get_utils import get_built_in_parameter_value
from duHast.Revit.Common.transaction import in_transaction
from duHast.Revit.Common.Geometry.curve import translate_curves_in_elevation
from duHast.Utilities.Objects import result as res

from duHast.Revit.Areas.areas import get_area_scheme_by_name

from Autodesk.Revit.DB import (
    BuiltInParameter,
    CurveElement,
    ElementId,
    ElementClassFilter,
    Transaction,
)


def get_area_lines_by_area_scheme_name(doc, scheme_name):
    """
    Returns a list of Revit model lines that are associated with a specific area scheme.

    Args:
        doc (Revit Document): The Revit document object.
        scheme_name (str): The name of the area scheme.

    Returns:
        list: A list of Revit elements representing the area lines associated with the specified area scheme.
    """
    return_value = []
    area_scheme = get_area_scheme_by_name(doc=doc, area_scheme_name=scheme_name)
    if area_scheme:
        filter = ElementClassFilter(CurveElement)
        dependent_element_ids = area_scheme.GetDependentElements(filter)
        for id in dependent_element_ids:
            element = doc.GetElement(id)
            return_value.append(element)
    return return_value


def get_area_lines_by_scheme_and_level_name(doc, scheme_name, level_name):
    """
    Returns a list of area lines based on the area scheme and level name.

    Args:
        doc (Document): The current model document.
        scheme_name (str): The name of the area scheme.
        level_name (str): The name of the level.

    Returns:
        list: A list of area lines based on the area scheme and level name or None if no area lines attached to scheme and level.
    """

    # get all area lines by scheme name
    area_lines_by_scheme_name = get_area_lines_by_area_scheme_name(
        doc=doc, scheme_name=scheme_name
    )

    # check if we got area lines
    if len(area_lines_by_scheme_name) == 0:
        return None

    # sort area lines by level
    sorted_area_lines = sort_area_line_by_level_name(
        doc=doc, area_lines=area_lines_by_scheme_name
    )

    # check if we got area lines on the level
    if level_name in sorted_area_lines:
        return sorted_area_lines[level_name]
    else:
        return None


def sort_area_line_by_level_name(doc, area_lines):
    """
    Sorts the area lines based on their associated level names and returns a dictionary where the keys are the level names and the values are lists of area lines.

    Args:
        doc (Document): The current model document.
        area_lines (list): A list of area lines.

    Returns:
        dict: A dictionary where the keys are the level names and the values are lists of area lines.
    """
    levels = get_levels_in_model(doc)
    # build level id to level name dictionary
    level_names_by_id = {}
    for l in levels:
        level_names_by_id[l.Id] = l.Name
    # add edge case: line is not associated with a level ( maybe in a group?)
    level_names_by_id[ElementId.InvalidElementId] = "This curve has no level associated"
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
    """
    Deletes area lines in a Revit model based on their associated level name.

    Args:
        doc (Document): The current model document.
        level_name (str): The name of the level to delete area lines from.
        area_lines (list): A list of area lines to be deleted.
        transaction_manager (function, optional): A function that manages the transaction. Defaults to `in_transaction`.

    Returns:
        Result: A `Result` class instance containing the following attributes:
            - status (bool): True if the delete operation was successful, False otherwise.
            - message (str): A message indicating the status of the delete operation.
            - result (list): A list of remaining area lines after the delete operation.
    """
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
        result_delete = transaction_manager(tranny, action)
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


def create_new_area_outlines(doc, curves, view, transaction_manager=in_transaction):
    """
    Create new area separation lines in a specified view in Autodesk Revit.

    Args:
        doc (Revit Document): The Revit document in which the area separation lines will be created.
        curves (list): A list of curves representing the area separation lines.
        view (Revit View): The view in which the area separation lines will be created.
        transaction_manager (function, optional): A transaction manager function that wraps the creation of area separation lines in a Revit transaction. Default is `in_transaction`.

    Returns:
        Result: A `Result` object that contains the status of the transaction and any error or success messages.
    """
    return_value = res.Result()

    def action():
        action_return_value = res.Result()
        try:
            for t in curves:
                doc.Create.NewAreaBoundaryLine(view.SketchPlane, t, view)
            action_return_value.append_message(
                "Created new area separation line(s) in view {}".format(view.Name)
            )
        except Exception as e:
            action_return_value.update_sep(
                False,
                "Failed to create area separation line(s) in view {} with exception: {}".format(
                    view.Name, e
                ),
            )
        return action_return_value

    tranny = Transaction(
        doc, "Creating new area separation line(s) in view ".format(view.Name)
    )
    result_create = transaction_manager(tranny, action)
    return_value.update(result_create)
    return return_value


def copy_area_lines_to_level_name(
    doc, view, area_lines, transaction_manager=in_transaction
):
    """
    Copy area separation lines from one level to another in Autodesk Revit.

    Args:
        doc (Revit Document): The Revit document in which the area separation lines exist.
        view (Revit View): The view in which the area separation lines will be created.
        area_lines (list): A list of area separation lines to be copied.
        transaction_manager (function, optional): A transaction manager function that wraps the creation of area separation lines in a Revit transaction. Default is `in_transaction`.

    Returns:
        Result: A `Result` object that contains the status of the transaction and any error or success messages.
    """
    return_value = res.Result()
    try:
        # sort area lines by level
        lines_by_level_name = sort_area_line_by_level_name(
            doc=doc, area_lines=area_lines
        )
        level_name = get_built_in_parameter_value(
            view, BuiltInParameter.PLAN_VIEW_LEVEL
        )
        # make sure only one level was returned and its not the level to be copied to!
        if len(lines_by_level_name) != 1:
            raise ValueError(
                "Source area lines must all be on the same level. Found {} levels instead.".format(
                    len(lines_by_level_name)
                )
            )
        elif level_name in lines_by_level_name:
            raise ValueError(
                "Source {} and destination {} level are identical!".format(level_name)
            )
        else:
            # get curve geometry from model lines
            curves = [m_line.GeometryCurve for m_line in area_lines]
            # check if we got curves
            if any(curves):
                # get source elevation (the elevations the area lines are on)
                source_elevation = get_level_elevation_by_name(
                    doc=doc, level_name=lines_by_level_name.iterkeys().next()
                )
                # check if we got a source elevation
                if source_elevation != None:
                    # get target elevation
                    target_elevation = get_level_elevation_by_name(
                        doc=doc, level_name=level_name
                    )
                    # check if we got a target elevation
                    if target_elevation != None:
                        # translate curves from source level to target levels
                        translate_result = translate_curves_in_elevation(
                            doc=doc,
                            original_curves=curves,
                            source_elevation=source_elevation,
                            target_elevation=target_elevation,
                        )

                        # check if we got translated curves...
                        if translate_result.status:
                            # this is an Autodesk.Revit.DB.CurveArray
                            curve_array = translate_result.result[0]
                            create_result = create_new_area_outlines(
                                doc=doc,
                                curves=curve_array,
                                view=view,
                                transaction_manager=transaction_manager,
                            )
                            return_value.update(create_result)
                        else:
                            raise ValueError(translate_result.message)
                    else:
                        raise ValueError(
                            "Failed to get an elevation for level: {}".format(
                                level_name
                            )
                        )
                else:
                    raise ValueError(
                        "Failed to get an elevation for level: {}".format(
                            lines_by_level_name.iterkeys().next()
                        )
                    )
            else:
                raise ValueError("Failed to get curves from area lines.")

    except Exception as e:
        return_value.update_sep(
            False,
            "Failed to copy {} area separation line(s) to level(s) with exception: {}".format(
                len(area_lines), e
            ),
        )
    return return_value
