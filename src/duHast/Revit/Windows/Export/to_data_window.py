"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a Revit window export to DATA class functions.
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

from Autodesk.Revit.DB import (
    BoundingBoxXYZ,
    BuiltInParameter,
    Options,
)


from duHast.Revit.Windows.windows import get_window_instances
from duHast.Data.Objects.Collectors import data_window as dWindow
from duHast.Revit.Common.Geometry.to_data_conversion import (
    convert_bounding_box_to_flattened_2d_points,
    convert_xyz_in_data_geometry_polygons,
)

from duHast.Revit.Common.Geometry.solids import (
    get_oriented_bounding_box_from_family_instance,
)
from duHast.Revit.Exports.export_data import (
    get_level_data,
    get_phasing_data,
    get_model_data,
    get_instance_properties,
    get_type_properties,
    get_design_set_data,
    get_super_component_id,
)
from duHast.Data.Objects.Collectors.Properties.data_room_to_phase import DataRoomToPhase


def _get_room_entries(doc, revit_window, get_room_fn):
    """
    Iterates all project phases and collects DataRoomToPhase entries by calling
    get_room_fn(phase) on the window for each phase.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param revit_window: A Revit window instance.
    :type revit_window: Autodesk.Revit.DB.FamilyInstance
    :param get_room_fn: Bound method accepting a Phase and returning a Room or None.
    :type get_room_fn: callable

    :return: List of room-to-phase pairings, one per phase that returned a room.
    :rtype: list[:class:`.DataRoomToPhase`]
    """
    entries = []
    seen = set()
    for phase in doc.Phases:
        try:
            room = get_room_fn(phase)
            if room is None:
                continue
            key = (phase.Id.Value, room.Id.Value)
            if key in seen:
                continue
            seen.add(key)
            entry = DataRoomToPhase()
            entry.phase_id = phase.Id.Value
            entry.room_id = room.Id.Value
            entries.append(entry)
        except Exception:
            pass
    return entries


def populate_data_window_object(doc, revit_window):
    """
    Returns a custom window data object populated with some data from the revit model window past in.

    - window id
    - window type name
    - window mark
    - window type mark
    - window level name
    - window level id
    - window offset from level

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param revit_window: A revit window instance.
    :type revit_window: Autodesk.Revit.DB.FamilyInstance

    :return: A data window object instance.
    :rtype: :class:`.DataWindow`
    """

    # set up data class object
    data_window = dWindow.DataWindow()
    # get window bounding box
    # set a default option
    opts = Options()

    # ORIENTED, so an instance placed at an angle keeps its angle. The world
    # aligned alternative is the right answer to "what extents does this
    # occupy" and the wrong one to "what shape is this": it is aligned to the
    # model axes, so a window in a wall running at 30 degrees comes out as an
    # upright rectangle lying across it. That cannot be corrected afterwards -
    # an axis aligned box no longer records the angle - so it has to be
    # measured in the instance's own frame here.
    #
    # The placement rides on the box Transform, which
    # convert_bounding_box_to_flattened_2d_points applies to the corners below.
    window_bounding_box = get_oriented_bounding_box_from_family_instance(
        revit_window, opts
    )
    # only export window data if 3D geometry is available
    # if no geometry is available, return None
    # some families of type window do not have any 3D geometry... ignore those for now
    if isinstance(window_bounding_box, BoundingBoxXYZ) == False:
        return None
    revit_window_data_geometry = convert_bounding_box_to_flattened_2d_points(
        window_bounding_box
    )

    if len(revit_window_data_geometry.outer_loop) > 0:
        window_point_groups_as_doubles = []
        data_geo_converted = convert_xyz_in_data_geometry_polygons(
            doc, revit_window_data_geometry
        )
        window_point_groups_as_doubles.append(data_geo_converted)
        data_window.polygon = window_point_groups_as_doubles

        # get design set data
        design_set = get_design_set_data(doc=doc, element=revit_window)
        data_window.design_set_and_option = design_set

        # get type properties
        type_props = get_type_properties(doc=doc, element=revit_window)
        data_window.type_properties = type_props

        # get instance properties
        instance_props = get_instance_properties(revit_window)
        data_window.instance_properties = instance_props

        # get level properties
        level = get_level_data(
            doc=doc,
            element=revit_window,
            built_in_parameter_def=BuiltInParameter.ASSOCIATED_LEVEL_OFFSET,  # TODO: check this parameter
        )
        data_window.level = level

        # get the model name
        model = get_model_data(doc=doc)
        data_window.revit_model = model

        # get phasing information
        phase = get_phasing_data(doc=doc, element=revit_window)
        data_window.phasing = phase

        # super component id (populated when window is a shared nested family)
        data_window.super_component_id = get_super_component_id(revit_window)

        # to-room and from-room per phase
        data_window.to_room = _get_room_entries(
            doc, revit_window, revit_window.get_ToRoom
        )
        data_window.from_room = _get_room_entries(
            doc, revit_window, revit_window.get_FromRoom
        )

        return data_window
    else:
        return None


def get_all_window_data(doc, filter_family_names=[]):
    """
    Gets a list of window data objects for each window element in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A list of data window instances.
    :rtype: list of :class:`.DataWindow`
    """

    all_window_data = []
    windows = get_window_instances(doc)
    for window in windows:
        # check if window is in filter list
        if len(filter_family_names) > 0:
            if window.Symbol.FamilyName not in filter_family_names:
                continue
        window_data = populate_data_window_object(doc, window)
        if window_data is not None:
            all_window_data.append(window_data)
    return all_window_data
