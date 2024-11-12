"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Revit room separation lines reports functions.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2024, Jan Christel
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


from duHast.Revit.Common.design_set_options import get_design_set_option_info
from duHast.Revit.Common.Geometry.curve import get_curve_level
from duHast.Revit.Common.Objects.design_set_property_names import DesignSetPropertyNames
from duHast.Revit.Rooms.room_lines import get_all_room_separation_lines_ids_with_warnings, get_all_room_separation_lines_ids_without_warnings



def _sort_room_lines_by_design_option(doc, room_line_ids):
    """
    Sorts room lines into a dictionary where key is the combination of the design set name and
    design option name and value is a list of room separation lines.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param room_line_ids: list of room separation line ids
    :type room_line_ids: [Autodesk.Revit.DB.ElementId]

    :return: Dictionary containing room separation lines by design set / option name
    :rtype: {str:[Autodesk.Revit.DB.ModelCurve]}
    """

    room_lines_by_design_option = {}

    # loop over ids, get the line and its design set / option data
    for id in room_line_ids:
        element = doc.GetElement(id)
        data_dic = get_design_set_option_info(doc=doc, element=element)
        key = DesignSetPropertyNames.combine_set_and_option_name(set_name=data_dic[DesignSetPropertyNames.DESIGN_SET_NAME], option_name=data_dic[DesignSetPropertyNames.DESIGN_OPTION_NAME])
        if key in room_lines_by_design_option:
            room_lines_by_design_option[key].append(element)
        else:
            room_lines_by_design_option[key] = [element]

    return room_lines_by_design_option


def _sort_room_lines_by_level(doc, room_lines_by_design_option):
    """
    Sorts the lines by level

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param room_lines_by_design_option: A dictioanry where key is the design set / option name and value is a list of room separation lines
    :type room_lines_by_design_option: {str:[Autodesk.Revit.DB.ModelCurve]}

    :return: A dictionary where key is a dictioanry where key is the design set / option name and value is another dictionary where key is the level name and value is a list of room separation lines
    :rtype: {str:{str:[Autodesk.Revit.DB.ModelCurve]}}
    """
    room_lines_by_design_option_and_level = {}

    # loop over dictionary and get the level information per line
    for design_set_option, lines in room_lines_by_design_option.items():
        curves_by_level_name = {}
        for line in lines:
            level = get_curve_level(doc=doc, curve=line)
            level_name = "Line is not associated to any level"
            if level:
                level_name = level.Name
            if level_name in curves_by_level_name:
                curves_by_level_name[level_name].append(line)
            else:
                curves_by_level_name[level_name] = [line]
        room_lines_by_design_option_and_level[design_set_option] = curves_by_level_name

    return room_lines_by_design_option_and_level



def _sort_room_sep_lines_by_design_option_and_level(doc, rooms_sep_line_ids):
    """
    Sort room lines by design option and by level

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param rooms_sep_line_ids: List of room separation line ids
    :type rooms_sep_line_ids: [Autodesk.Revit.ElementId]

    :return: A dictionary where key is the design option name and value is a nested dictionary where key is the level name and value is a list of room lines.
    :rtype: :rtype: {str: {str:[Autodesk.Revit.DB.ModelCurve]}}
    """

    # sort offending elements by design option
    room_lines_by_design_option = _sort_room_lines_by_design_option(
        doc=doc, room_line_ids=rooms_sep_line_ids
    )

    # sort offending elements by level
    room_line_instances_by_design_option_and_level = _sort_room_lines_by_level(
        doc=doc, room_lines_by_design_option=room_lines_by_design_option
    )

    return room_line_instances_by_design_option_and_level


def room_lines_with_warnings_by_design_option_and_level(doc):
    """
    Reports all room separation line with warnings by design option and level they belong too

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: dictionary where key is the design option name and value is a nested dictionary where key is the level name and value is a list of room lines.
    :rtype: {str: {str:[Autodesk.Revit.DB.ModelCurve]}}
    """

    room_line_instances_by_design_option_and_level = {}

    # get all ids which have warnings
    all_line_ids_with_warnings = get_all_room_separation_lines_ids_with_warnings(doc=doc)

    # check if any warning is present
    if len(all_line_ids_with_warnings) == 0:
        return room_line_instances_by_design_option_and_level

    # sort by design option and level
    room_line_instances_by_design_option_and_level = _sort_room_sep_lines_by_design_option_and_level (doc=doc, rooms_sep_line_ids= all_line_ids_with_warnings)
   

    return room_line_instances_by_design_option_and_level


def room_lines_without_warnings_by_design_option_and_level(doc):

    """
    Reports all room separation line without warnings by design option and level they belong too

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A dictionary where key is the design option name and value is a nested dictionary where key is the level name and value is a list of room lines.
    :rtype: {str: {str:[Autodesk.Revit.DB.ModelCurve]}}
    """

    room_line_instances_by_design_option_and_level = {}


    # get all room separation lines without warnings
    all_line_ids_without_warnings = get_all_room_separation_lines_ids_without_warnings(doc=doc)
    
    # check if any warning is present
    if len(all_line_ids_without_warnings) == 0:
        return room_line_instances_by_design_option_and_level

    # sort by design option and level
    room_line_instances_by_design_option_and_level = _sort_room_sep_lines_by_design_option_and_level (doc=doc, rooms_sep_line_ids= all_line_ids_without_warnings)
   

    return room_line_instances_by_design_option_and_level
  