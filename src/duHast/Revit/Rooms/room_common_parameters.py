"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Revit API utility functions for Rooms.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

#!/usr/bin/python
# -*- coding: utf-8 -*-
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

import System
import clr

clr.AddReference("System.Core")
from System import Linq

clr.ImportExtensions(Linq)

# import everything from Autodesk Revit DataBase namespace (Revit API)
import Autodesk.Revit.DB as rdb

from Autodesk.Revit.DB import (
    FilteredElementCollector,
    BuiltInCategory,
    BuiltInParameter,
    ViewType,
    SpatialElementBoundaryLocation,
    SpatialElementBoundaryOptions,
)
from Autodesk.Revit.DB.Architecture import Room

from duHast.Revit.Common.parameter_get_utils import param_is_empty_or_null
from duHast.Revit.Common.Geometry.geometry import (
    UV_pt_list_from_crv_list,
    point_in_polygon,
)
from duHast.Revit.Rooms.Geometry.geometry import get_room_boundary_loops
from duHast.Revit.Common.parameter_get_utils import get_built_in_parameter_value
from duHast.Revit.Common import (
    parameter_get_utils as rParaGet,
    phases as rPhase,
)

from duHast.Utilities.utility import encode_utf8


def get_room_number(room):
    """
    Get the room number of the room
    :param room: The room to get the number of
    :type room: Room
    :return: The room number of the room
    :rtype: str
    """

    number_param = get_built_in_parameter_value(
        element=room, built_in_parameter_def=BuiltInParameter.ROOM_NUMBER
    )
    return number_param


def get_room_name(room):
    """
    Get the room name of the room
    :param room: The room to get the name of
    :type room: Room
    :return: The room name of the room
    :rtype: str
    """
    name_param = get_built_in_parameter_value(
        element=room, built_in_parameter_def=BuiltInParameter.ROOM_NAME
    )
    return name_param


def get_room_phase(rvt_doc, room):
    """
    Get the phase of the room
    :param rvt_doc: The document to get the room from
    :type rvt_doc: Document
    :param room: The room to get the phase of
    :type room: Room
    :return: The phase of the room
    :rtype: str
    """
    phase_param = get_built_in_parameter_value(
        room,
        BuiltInParameter.ROOM_PHASE,
        rParaGet.get_parameter_value_as_element_id,
    )

    phase = encode_utf8(rPhase.get_phase_name_by_id(rvt_doc, phase_param))
    return phase


def get_room_level(rvt_doc, room):
    """
    Get the phase of the room
    :param rvt_doc: The document to get the room from
    :type rvt_doc: Document
    :param room: The room to get the phase of
    :type room: Room
    :return: The phase of the room
    :rtype: str
    """

    try:
        rm_level_name = rvt_doc.GetElement(room.LevelId).Name
    except Exception:
        rm_level_name = "Not placed in model"
    return rm_level_name


def get_room_num_variations(room):
    """
    Get a list of variations of room number
    e.g. 1.01, 101, 1-01
    :param room: The room to get the number of
    :type room: Room
    :return: The list of variations of room number
    :rtype: list
    """
    room_num = get_room_number(room)
    room_num_remove_fullstops = room_num.replace(".", "")
    return [room_num, room_num_remove_fullstops]


def get_room_num_name_comb(room):
    """
    Get a combination of room number and name in the format:
    '101 - Room Name'
    :param room: The room to get the number and name of
    :type room: Room
    :return: The combination of room number and name
    :rtype: str
    """
    return "{} - {}".format(get_room_number(room), get_room_name(room))


def get_rooms_in_view(document, targ_view):
    """
    Get all rooms in the view. This avoids using the FilteredElementCollector
    overload that takes a view id as an argument as this is has to generate
    graphics for all elements in the view which is very slow.
    :param document: The document to get the rooms from
    :type document: Document
    :param targ_view: The view to get the rooms from
    :type targ_view: View
    :return: The rooms in the view
    :rtype: list
    """
    view_specific_elements = (
        FilteredElementCollector(document)
        .WhereElementIsNotElementType()
        .OwnedByView(targ_view.Id)
        .ToElements()
    )
    return [el for el in view_specific_elements if el.GetType() == Room]


def get_room_from_element(phase_dictionary, elem):
    """
    Get the room associated with the element. This should be updated
    by Revit as the element moves
    :param phase_dictionary: The dictionary of phases names to phase elements
    :type phase_dictionary: dict
    :param elem: The element to get the room of
    :type elem: Element
    :return: The room associated with the element
    :rtype: Room
    """
    el_phase = elem.get_Parameter(BuiltInParameter.PHASE_CREATED)
    if el_phase != None:
        el_phase_name = el_phase.AsValueString()
        if el_phase_name != "None":
            el_phase_elem = phase_dictionary[el_phase_name]
            el_room = elem.get_Room(el_phase_elem)
            # if theres a room associated with the element return it
            return (
                el_room if el_room != None else None
            )  #'Elem Id: {} has no room'.format(str(elem.Id.IntegerValue))
        else:
            return None

    else:
        print("Elem Id: {} has no phase".format(str(elem.Id.IntegerValue)))
        return None


def check_element_is_in_room(phase_dictionary, elem, room_to_check):
    """
    Check if the element is in the room
    :param phase_dictionary: The dictionary of phases names to phase elements
    :type phase_dictionary: dict
    :param el: The element to check
    :type el: Element
    :param room_to_check: The room to check if the element is in
    :type room_to_check: Room
    :return: True if the element is in the room, False otherwise
    :rtype: bool
    """
    el_room = get_room_from_element(phase_dictionary, elem)
    # First get the room number of the element
    if el_room != None:
        # if theres a room associated with the element return the number of it
        elem_room_num = get_room_number(el_room)
        # get the number of the exemplar room to compare
        exemplar_room_num = get_room_number(room_to_check)
        # if exemplar room and element room are same num
        return True if elem_room_num == exemplar_room_num else False

    else:
        print("Elem Id: {} has no room".format(str(elem.Id.IntegerValue)))
        return False


def get_room_from_selection(rvt_doc, id_list):
    """
    Get the first Room from a selection of element ids
    :param rvt_doc: The document to get the room from
    :type rvt_doc: Document
    :param id_list: The list of element ids to check
    :type id_list: list
    :return: The room from the selection
    :rtype: Room
    """
    selected_room = None

    for elem_id in id_list:
        sel_elem = rvt_doc.GetElement(elem_id)
        if sel_elem.GetType() == Room:
            return sel_elem

    return selected_room


def check_room_on_view_level(rvt_doc, room, view):
    """
    Check if the room is on the same level as the view
    :param rvt_doc: The document to get the room from
    :type rvt_doc: Document
    :param room: The room to check
    :type room: Room
    :param view: The view to check
    :type view: View
    :return: True if the room is on the same level as the view, False otherwise
    :rtype: bool
    """
    rm_level_name = rvt_doc.GetElement(room.LevelId).Name
    view_level_name = view.get_Parameter(BuiltInParameter.PLAN_VIEW_LEVEL).AsString()
    check = rm_level_name == view_level_name
    return check


def check_rm_pt_extents(rvt_doc, room_list, target_view, target_view_crop_bx_pts):
    """
    Check if all the points from the room boundary segments are within a view crop box
    for a list of rooms
    :param rvt_doc: The document to get the room from
    :type rvt_doc: Document
    :param room_list: The list of rooms to check
    :type room_list: list
    :param target_view: The view to check
    :type target_view: View
    :param target_view_crop_bx_pts: The points of the view crop box curves
    :type target_view_crop_bx_pts: list
    :return: The rooms that are entirely within the view crop box
    :rtype: list
    """
    entire_rooms = []
    for rm in room_list:
        rm_is_on_level = check_room_on_view_level(rvt_doc, rm, target_view)

        rm_crv_list = get_room_boundary_loops(rm)

        if rm_is_on_level:
            if len(rm_crv_list) > 0:
                rm_uv_list = UV_pt_list_from_crv_list(rm_crv_list)

                pt_in_rm = []

                for rm_pt in rm_uv_list:
                    pt_in_rm.append(point_in_polygon(rm_pt, target_view_crop_bx_pts))

                if all(pt_in_rm):
                    entire_rooms.append(rm)
            else:
                return []

    return entire_rooms


def check_rm_loc_point(room_list, target_view_crop_bx_pts):
    """
    Check if the location crosshairs of a room is within a view crop box
    for a list of rooms
    :param room_list: The list of rooms to check
    :type room_list: list
    :param target_view_crop_bx_pts: The points of the view crop box curves
    :type target_view_crop_bx_pts: list
    :return: The rooms that have their location point within the view crop box
    :rtype: list
    """
    loc_pt_in = []
    for rm in room_list:
        rm_loc_pt = rm.Location.Point
        rm_loc_UV = (rm_loc_pt.X, rm_loc_pt.Y)

        if point_in_polygon(rm_loc_UV, target_view_crop_bx_pts):
            loc_pt_in.append(rm)

    return loc_pt_in


def get_only_entire_rooms(rvt_doc, rm_list, view, check_rm_edges=False):
    """
    Get only the rooms that are entirely within the view crop box
    :param rvt_doc: The document to get the room from
    :type rvt_doc: Document
    :param rm_list: The list of rooms to check
    :type rm_list: list
    :param view: The view to check
    :type view: View
    :param check_rm_edges: True: Check if the entire room boundary segments are in the view crop box
    False: Check if the location crosshair is in the view crop box
    :type check_rm_edges: bool
    :return: The rooms that are entirely within the view crop box
    :rtype: list
    """

    if view.CropBoxActive == False:
        return rm_list
    else:
        crop_reg = view.GetCropRegionShapeManager()
        crv_list = crop_reg.GetCropShape()

        if len(list(crv_list)) > 0:
            # TODO: Adaption required to handle rooms with multiple boundary segment
            # loops. Currently only handles the first loop
            view_pt_list = UV_pt_list_from_crv_list(crv_list[0])

            if check_rm_edges:
                return check_rm_pt_extents(rvt_doc, rm_list, view, view_pt_list)
            else:
                return check_rm_loc_point(rm_list, view, view_pt_list)

        else:
            return []


def get_all_rooms_in_plan_views(rvt_doc, view_list):
    """
    Get all rooms in the plan views
    :param rvt_doc: The document to get the room from
    :type rvt_doc: Document
    :param view_list: The list of views to check
    :type view_list: list
    :return: The rooms in the plan views
    :rtype: list
    """
    rooms = []

    for view in view_list:
        rooms_in_view = (
            FilteredElementCollector(rvt_doc, view.Id)
            .OfCategory(BuiltInCategory.OST_Rooms)
            .ToElements()
        )
        entire_rms = get_only_entire_rooms(rvt_doc, rooms_in_view, view)
        if len(entire_rms) > 0:
            rooms.extend(entire_rms)

    return rooms


def get_rooms_from_sheet_obj_list(rvt_doc, sheet_obj_list):
    """
    Get all rooms from the sheet object list
    :param rvt_doc: The document to get the room from
    :type rvt_doc: Document
    :param sheet_obj_list: The list of ViewSheetBaseObject objects to check
    :type sheet_obj_list: list
    :return: The rooms from the sheet object list
    :rtype: list
    """

    rms_on_sel_shts = []

    for sht_obj in sheet_obj_list:
        sht = sht_obj.sheet
        rms_on_sel_shts.extend(get_all_rooms_in_plan_views(rvt_doc, [sht]))

    return rms_on_sel_shts
