"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains Revit family instance export to DataItem functions.

Covers placed family instances belonging to a caller-supplied list of categories
(furniture, equipment, specialty equipment, etc.).
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
    ElementCategoryFilter,
    FamilyInstance,
    FilteredElementCollector,
    LocationPoint,
    Options,
)

from duHast.Data.Objects.Collectors import data_item as dItem
from duHast.Data.Objects.Collectors.Properties.Geometry import geometry_base
from duHast.Data.Objects.Collectors.Properties.data_level import DataLevel
from duHast.Geometry.matrix import Matrix
from duHast.Revit.Common.Geometry.points import (
    convert_XYZ_to_point3,
    get_point_as_doubles,
)
from duHast.Revit.Common.Geometry.solids import (
    get_oriented_bounding_box_from_family_instance,
)
from duHast.Revit.Common.Geometry.to_data_conversion import (
    convert_bounding_box_to_flattened_2d_points,
    convert_xyz_in_data_geometry_polygons,
)
from duHast.Revit.Exports.export_data import (
    get_design_set_data,
    get_instance_properties,
    get_model_data,
    get_phasing_data,
    get_super_component_id,
    get_type_properties,
)
from duHast.Revit.Family.family_geometry import (
    get_solids_based_bounding_box_from_family_instance,
)
from duHast.Revit.Levels.levels import get_levels_list_ascending
from duHast.Utilities.unit_conversion import convert_imperial_feet_to_metric_mm
from duHast.Utilities.utility import encode_utf8


# ---------------------------------------------------------------------------
# Default category list - callers may supply their own instead.
# ---------------------------------------------------------------------------

DEFAULT_ITEM_CATEGORIES = [
    BuiltInCategory.OST_Furniture,
    BuiltInCategory.OST_FurnitureSystems,
    # Added 2026-09-05 because leaving it out exported the wrong half of the
    # model. Measured on a real document: 87 of 179 nested instances were
    # OST_Furniture components whose SuperComponent was Casework, all one
    # family (Handle_Joinery_FIJO_900). So the joinery HANDLES arrived as
    # first-class items while the casework runs they belong to were absent
    # entirely. Casework is furniture by every definition a room data sheet
    # uses, and a list that admits the components of a thing but not the thing
    # itself is harder to justify than either including or excluding both.
    BuiltInCategory.OST_Casework,
    BuiltInCategory.OST_MechanicalEquipment,
    BuiltInCategory.OST_ElectricalEquipment,
    BuiltInCategory.OST_ElectricalFixtures,
    BuiltInCategory.OST_PlumbingFixtures,
    BuiltInCategory.OST_SpecialityEquipment,
    BuiltInCategory.OST_GenericModel,
]


# ---------------------------------------------------------------------------
# Helper: location point + rotation
# ---------------------------------------------------------------------------

def get_location_data(revit_family_instance):
    """
    Extracts the placement location and orientation of a family instance and
    returns them as a populated :class:`.DataGeometryBase` instance.

    - ``translation_coord`` - x/y/z position converted to metric mm (:class:`.Point3`)
    - ``rotation_coord``    - 3 x 3 rotation matrix derived from the instance's
                              local transform (each row is a basis vector [x, y, z])

    Only :class:`Autodesk.Revit.DB.LocationPoint` instances are supported.
    Line-based placements (``LocationCurve``) return *None*.

    :param revit_family_instance: A placed Revit family instance.
    :type revit_family_instance: Autodesk.Revit.DB.FamilyInstance

    :return: A populated location data object, or *None* if the location type
             is not a point.
    :rtype: :class:`.DataGeometryBase` or None
    """

    location = revit_family_instance.Location
    if not isinstance(location, LocationPoint):
        return None

    loc_point = geometry_base.DataGeometryBase(data_type="location_point")

    # --- position (x/y/z in metric mm) ---
    loc_point.translation_coord = convert_XYZ_to_point3(location.Point)

    # --- orientation: rows of the local-to-world rotation matrix ---
    # GetTransform() returns the full local coordinate system of the instance.
    # BasisX / BasisY / BasisZ are unit vectors in world space describing how
    # the family's local axes are oriented. Together they form the 3x3 rotation
    # matrix that can be used to reconstruct the instance's facing direction.
    #
    # Stored as the Matrix the data class declares. A plain list of lists wrote json
    # which could not be read back, since Matrix is built from a dictionary.
    transform = revit_family_instance.GetTransform()
    basis_vectors = [
        get_point_as_doubles(transform.BasisX, include_z=True),
        get_point_as_doubles(transform.BasisY, include_z=True),
        get_point_as_doubles(transform.BasisZ, include_z=True),
    ]
    loc_point.rotation_coord = Matrix(rows=3, cols=3, elements=basis_vectors)

    return loc_point


# ---------------------------------------------------------------------------
# Helper: room ids
# ---------------------------------------------------------------------------

def get_room_ids(doc, revit_family_instance):
    """
    Returns a list of unique room element ids that the family instance belongs to,
    resolved across all project phases.

    Lookup strategy (in order):

    1. **Phase-aware** - iterates ``doc.Phases`` and calls
       ``FamilyInstance.get_Room(phase)`` for each phase. This is the primary
       source and correctly handles items whose room assignment changes between
       construction phases.
    2. **Direct property** - ``FamilyInstance.Room`` is tried when the phase
       loop yields nothing (e.g. older family hosting types).
    3. **Point fallback** - if both of the above return nothing, the instance's
       ``LocationPoint`` is used with ``Document.GetRoomAtPoint`` to perform a
       spatial lookup against the last project phase.

    .. note::
        Doors and windows should use ``FamilyInstance.FromRoom`` /
        ``FamilyInstance.ToRoom`` instead.  Those categories are not included
        in :data:`DEFAULT_ITEM_CATEGORIES`, so this function does not handle
        that case.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param revit_family_instance: A placed Revit family instance.
    :type revit_family_instance: Autodesk.Revit.DB.FamilyInstance

    :return: Unique room element ids (integers), may be empty.
    :rtype: list[int]
    """

    room_ids = []

    # --- 1. phase-aware lookup ---
    for phase in doc.Phases:
        try:
            room = revit_family_instance.get_Room(phase)
            if room is not None:
                room_id = room.Id.Value
                if room_id not in room_ids:
                    room_ids.append(room_id)
        except Exception:
            pass  # some phases may not support room lookup for this element

    # --- 2. direct Room property ---
    if not room_ids:
        try:
            room = revit_family_instance.Room
            if room is not None:
                room_id = room.Id.Value
                if room_id not in room_ids:
                    room_ids.append(room_id)
        except Exception:
            pass

    # --- 3. point-based fallback using the last phase ---
    if not room_ids:
        try:
            location = revit_family_instance.Location
            if isinstance(location, LocationPoint):
                last_phase = doc.Phases.get_Item(doc.Phases.Size - 1)
                room = doc.GetRoomAtPoint(location.Point, last_phase)
                if room is not None:
                    room_ids.append(room.Id.Value)
        except Exception:
            pass

    return room_ids


# ---------------------------------------------------------------------------
# Helper: level from bounding box
# ---------------------------------------------------------------------------

def get_level_data_by_bounding_box(doc, revit_family_instance):
    """
    Determines the nearest level below a family instance by comparing the lowest
    Z coordinate of its solid geometry against the ascending list of project levels.

    Algorithm:

    1. Compute the solid-based bounding box of the instance.
    2. Take ``bbox.Min.Z`` (internal Revit feet) as the bottom of the item.
    3. Walk all levels sorted ascending by ``ProjectElevation`` and keep the
       last one whose elevation is at or below ``bbox.Min.Z``.
    4. If the item sits below every level (e.g. underground) the lowest level
       is used as a fallback.
    5. ``offset_from_level`` = ``bbox.Min.Z - level.ProjectElevation``, converted
       to metric mm.

    Returns a default empty :class:`.DataLevel` when no solid geometry or no
    levels are found in the document.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param revit_family_instance: A placed Revit family instance.
    :type revit_family_instance: Autodesk.Revit.DB.FamilyInstance

    :return: A populated data level instance.
    :rtype: :class:`.DataLevel`
    """

    level_d = DataLevel()

    # --- step 1: bounding box from solid geometry ---
    bbox = get_solids_based_bounding_box_from_family_instance(doc, revit_family_instance)
    if bbox is None:
        return level_d  # no solid geometry - return empty default

    bbox_min_z = bbox.Min.Z  # internal Revit units (feet)

    # --- step 2: find nearest level at or below bbox bottom ---
    best_level = None
    first_level = None  # fallback when item is below all levels

    for level in get_levels_list_ascending(doc):
        if first_level is None:
            first_level = level
        if level.ProjectElevation <= bbox_min_z:
            # keep updating - the last one still below wins
            best_level = level
        else:
            # levels are ascending; nothing further will be below bbox_min_z
            break

    # if item is below every level, use the lowest level as fallback
    if best_level is None:
        best_level = first_level

    if best_level is None:
        return level_d  # model has no levels at all

    # --- step 3: populate DataLevel ---
    level_d.name = encode_utf8(best_level.Name)
    level_d.id = best_level.Id.Value
    level_d.offset_from_level = convert_imperial_feet_to_metric_mm(
        bbox_min_z - best_level.ProjectElevation
    )

    return level_d


# ---------------------------------------------------------------------------
# Helper: footprint polygon
# ---------------------------------------------------------------------------

def get_footprint_polygons(doc, revit_family_instance):
    """
    Returns the item's footprint as the list of polygons DataItem.polygon takes,
    or an empty list when there is no solid geometry to measure.

    ORIENTED, so an instance placed at an angle keeps its angle. The world aligned
    alternative is the right answer to "what extents does this occupy" and the wrong
    one to "what shape is this": a desk rotated thirty degrees would come out as an
    upright rectangle lying across it. That cannot be corrected afterwards, since an
    axis aligned box no longer records the angle, so it has to be measured in the
    instance's own frame in the first place.

    Sub-components are included, which is where this parts company with doors and
    windows. A casework run's handles and a fixture's tap are SHARED nested
    families: separate elements, absent from their host's own geometry. Measuring
    the host alone returns the carcass, which is not the footprint of the thing on
    the schedule. A door's nested content is the opposite case - its hardware is not
    the door - which is why the flag is per caller and not a default.

    Decimal feet, via get_point_as_doubles, matching doors, rooms and the rest of
    the polygon geometry. Deliberately NOT the millimetres location_point carries:
    the two units sit side by side in one record, and the polygon is the one that
    has to line up with every other footprint.

    An empty list is an ordinary state rather than a failure, and the reason this
    returns one where to_data_door rejects the element outright. A family with no 3D
    geometry still has a location, a level and its properties, all worth exporting;
    a consumer draws it at its insertion point instead.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param revit_family_instance: A placed Revit family instance.
    :type revit_family_instance: Autodesk.Revit.DB.FamilyInstance

    :return: A list of polygon instances, empty when nothing could be measured.
    :rtype: list[:class:`.DataGeometryPolygon2`]
    """

    # the placement rides on the box Transform, which
    # convert_bounding_box_to_flattened_2d_points applies to the corners, so the
    # points come back world placed and rotated
    bounding_box = get_oriented_bounding_box_from_family_instance(
        revit_family_instance, Options(), include_sub_components=True
    )
    if bounding_box is None:
        return []

    flattened = convert_bounding_box_to_flattened_2d_points(bounding_box)
    if len(flattened.outer_loop) == 0:
        return []

    return [convert_xyz_in_data_geometry_polygons(doc, flattened)]


# ---------------------------------------------------------------------------
# Core populate function
# ---------------------------------------------------------------------------

def populate_data_item_object(doc, revit_family_instance):
    """
    Returns a :class:`.DataItem` populated from a single placed family instance.

    Populated fields:

    - instance id and instance parameters
    - type name and type parameters
    - level name, level id, and offset from level
    - location point (x/y/z in mm) and rotation matrix
    - footprint polygon (oriented, in decimal feet), when the family has solids
    - phasing (created / demolished)
    - design set / option membership
    - model name

    Returns *None* when the instance has no valid :class:`LocationPoint`
    (e.g. line-based families).

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param revit_family_instance: A placed Revit family instance.
    :type revit_family_instance: Autodesk.Revit.DB.FamilyInstance

    :return: A populated data item object, or *None*.
    :rtype: :class:`.DataItem` or None
    """

    # resolve location first - skip line-based placements
    location_data = get_location_data(revit_family_instance)
    if location_data is None:
        return None

    data_i = dItem.DataItem()
    data_i.location_point = location_data

    # footprint, measured in the instance's own frame so a rotated item keeps its
    # angle. Empty when the family carries no solid geometry, which is not grounds
    # for dropping the item - see get_footprint_polygons.
    data_i.polygon = get_footprint_polygons(doc, revit_family_instance)

    # rooms this item belongs to (phase-aware)
    data_i.rooms = get_room_ids(doc, revit_family_instance)

    # instance properties
    data_i.instance_properties = get_instance_properties(revit_family_instance)

    # type properties
    data_i.type_properties = get_type_properties(doc=doc, element=revit_family_instance)

    # level + offset from level
    # Derived from solid geometry bounding box rather than a Revit parameter,
    # so it works consistently across all family hosting types.
    data_i.level = get_level_data_by_bounding_box(doc, revit_family_instance)

    # model, phasing, design set
    data_i.revit_model = get_model_data(doc=doc)
    data_i.phasing = get_phasing_data(doc=doc, element=revit_family_instance)
    data_i.design_set_and_option = get_design_set_data(
        doc=doc, element=revit_family_instance
    )

    # super component id (populated when instance is a shared nested family)
    data_i.super_component_id = get_super_component_id(revit_family_instance)

    return data_i


# ---------------------------------------------------------------------------
# Collector
# ---------------------------------------------------------------------------

def get_all_item_data(doc, categories=None):
    """
    Collects all placed :class:`Autodesk.Revit.DB.FamilyInstance` elements
    belonging to the given list of categories and returns a list of
    :class:`.DataItem` objects.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param categories: List of :class:`Autodesk.Revit.DB.BuiltInCategory` values
        to collect from.  Defaults to :data:`DEFAULT_ITEM_CATEGORIES` when
        *None* is supplied.
    :type categories: list[Autodesk.Revit.DB.BuiltInCategory] or None

    :return: A list of populated data item instances.
    :rtype: list[:class:`.DataItem`]
    """

    if categories is None:
        categories = DEFAULT_ITEM_CATEGORIES

    all_item_data = []

    for category in categories:
        category_filter = ElementCategoryFilter(category)
        instances = (
            FilteredElementCollector(doc)
            .OfClass(FamilyInstance)
            .WherePasses(category_filter)
        )

        for instance in instances:
            item_data = populate_data_item_object(doc, instance)
            if item_data is not None:
                all_item_data.append(item_data)

    return all_item_data
