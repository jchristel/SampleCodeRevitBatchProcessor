"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of functions around data storage in Revit.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Data storage can be used to project wide settings not associated with a specific element. 

Obsolete in Revit 2025 ... 
"""

#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2025, Jan Christel
# All rights reserved.

"""
Facts read off placed family instances: the room or space an instance points at in a phase, where it sits, which way it faces,
what hosts it, and whether it is a component of another instance.

Wall hosted openings (doors, windows) and free standing items (furniture, equipment) are served by the same readers; what varies
is the category and the name of the room property.
"""

import math

from duHast.Revit.Common.element_id import get_el_id_int

from Autodesk.Revit.DB import ElementCategoryFilter, FamilyInstance, FilteredElementCollector


def get_room_or_space_id(instance, phase, property_name):
    """
    Returns the id of the room (or space) an instance points at in a phase.

    The phase indexed form of the property is reached through the CLR get_ accessor, because instance.FromRoom[phase] binds
    to the parameterless property (current phase) on some versions.

    :param instance: A placed family instance.
    :type instance: Autodesk.Revit.DB.FamilyInstance
    :param phase: The phase.
    :type phase: Autodesk.Revit.DB.Phase
    :param property_name: 'FromRoom' or 'ToRoom' (wall hosted categories), 'Room' or 'Space' (an instance in one room or space).
    :type property_name: str

    :return: The room or space id, None if the instance has none on that side (an external door is a normal case).
    :rtype: int or None
    """

    accessor = getattr(instance, "get_" + property_name, None)
    room = accessor(phase) if accessor is not None else getattr(instance, property_name)[phase]
    return get_el_id_int(room.Id) if room is not None else None


def get_family_name(instance):
    """
    Returns the name of the family an instance's type belongs to.

    :param instance: A placed family instance.
    :type instance: Autodesk.Revit.DB.FamilyInstance

    :return: The family name, None if unreadable.
    :rtype: str or None
    """

    try:
        symbol = instance.Symbol
        name = symbol.FamilyName if symbol is not None else None
        return str(name) if name else None
    except Exception:
        return None


def get_host_info(instance):
    """
    Returns what an instance is hosted on.

    FamilyInstance.Host is the host element (wall, floor, ceiling) and None for a level hosted instance.

    :param instance: A placed family instance.
    :type instance: Autodesk.Revit.DB.FamilyInstance

    :return: A dictionary with keys 'kind' (the host's category name), 'id' (int) and 'face_hosted' (bool); None when nothing hosts it.
    :rtype: dict or None
    """

    try:
        host = instance.Host
    except Exception:
        return None
    if host is None:
        return None
    try:
        kind = host.Category.Name if host.Category is not None else None
    except Exception:
        kind = None
    try:
        face_hosted = instance.HostFace is not None
    except Exception:
        face_hosted = False
    try:
        host_id = get_el_id_int(host.Id)
    except Exception:
        return None
    return {"kind": kind, "id": host_id, "face_hosted": face_hosted}


def get_insertion_point(instance):
    """
    Returns the plan position (Revit internal units, feet) of an instance's location point.

    :param instance: A placed family instance.
    :type instance: Autodesk.Revit.DB.FamilyInstance

    :return: A dictionary with keys 'x' and 'y'; None if the instance has no location point.
    :rtype: dict or None
    """

    location = getattr(instance, "Location", None)
    point = getattr(location, "Point", None) if location is not None else None
    if point is None:
        return None
    return {"x": float(point.X), "y": float(point.Y)}


def get_through_wall_normal(instance):
    """
    Returns the unit vector through the wall, from the from-room towards the to-room: the instance's FacingOrientation projected to plan.

    The facing and not the host wall's direction: Revit's ToRoom follows the facing, so the two cannot disagree.

    :param instance: A placed family instance.
    :type instance: Autodesk.Revit.DB.FamilyInstance

    :return: A dictionary with keys 'x' and 'y'; None if the facing has no plan component (a hatch in a floor).
    :rtype: dict or None
    """

    facing = getattr(instance, "FacingOrientation", None)
    if facing is None:
        return None
    x = float(facing.X)
    y = float(facing.Y)
    length = math.sqrt(x * x + y * y)
    if length < 1e-9:
        return None
    return {"x": x / length, "y": y / length}


def get_opening_placements(doc, phase, built_in_category):
    """
    Returns, per instance of a category, its room references in a phase, insertion point and through wall normal.

    One collector pass so the four facts describe the same instance. Each fact is read on its own: an unreadable room
    reference costs that reference and not the position or direction of the same instance.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param phase: The phase the room references are read in.
    :type phase: Autodesk.Revit.DB.Phase
    :param built_in_category: The category, e.g. OST_Doors.
    :type built_in_category: Autodesk.Revit.DB.BuiltInCategory

    :return: Instance id (int) mapped to {'from_room': int or None, 'to_room': int or None, 'insertion_point': dict or None, 'normal': dict or None}.
    :rtype: dict
    """

    placements = {}
    collector = FilteredElementCollector(doc).OfCategory(built_in_category).WhereElementIsNotElementType()
    for opening in collector:
        try:
            from_room = get_room_or_space_id(opening, phase, "FromRoom")
            to_room = get_room_or_space_id(opening, phase, "ToRoom")
        except Exception:
            from_room, to_room = None, None

        try:
            insertion_point = get_insertion_point(opening)
        except Exception:
            insertion_point = None

        try:
            normal = get_through_wall_normal(opening)
        except Exception:
            normal = None

        placements[get_el_id_int(opening.Id)] = {
            "from_room": from_room,
            "to_room": to_room,
            "insertion_point": insertion_point,
            "normal": normal,
        }
    return placements


def get_nested_instance_ids(doc, built_in_category):
    """
    Returns the ids of the instances of a category that are a component of another instance of the same category
    (the leaf and hardware of a door that is modelled as a nested shared family).

    Only the immediate SuperComponent is tested, and it is the parent's category that decides: a door hosting a window category
    sub component is left alone.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param built_in_category: The category, e.g. OST_Doors.
    :type built_in_category: Autodesk.Revit.DB.BuiltInCategory

    :return: The ids of the nested instances.
    :rtype: set of int
    """

    nested = set()
    collector = FilteredElementCollector(doc).OfCategory(built_in_category).WhereElementIsNotElementType()
    for instance in collector:
        parent = getattr(instance, "SuperComponent", None)
        if parent is None:
            continue
        parent_category = getattr(parent, "Category", None)
        own_category = getattr(instance, "Category", None)
        if parent_category is None or own_category is None:
            continue
        if get_el_id_int(parent_category.Id) == get_el_id_int(own_category.Id):
            nested.add(get_el_id_int(instance.Id))
    return nested


def get_item_facts(doc, phase, built_in_categories, identify_by="room"):
    """
    Returns, per family instance of the categories, the room or space it is in during a phase, its category name, family name and host.

    ONE spatial reference per instance: identify_by 'room' reads get_Room(phase), 'space' reads get_Space(phase) (a services model that
    holds spaces and no rooms). Never both, the walk is the slow half of an export. An instance whose lookup raises is recorded with no
    reference.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param phase: The phase the reference is read in.
    :type phase: Autodesk.Revit.DB.Phase
    :param built_in_categories: The categories to walk.
    :type built_in_categories: list of Autodesk.Revit.DB.BuiltInCategory
    :param identify_by: 'room' or 'space'.
    :type identify_by: str

    :raises ValueError: when identify_by is neither.

    :return: Instance id (int) mapped to {'reference': int or None, 'category': str or None, 'family_name': str or None, 'host': dict or None}.
    :rtype: dict
    """

    if identify_by not in ("room", "space"):
        raise ValueError("identify_by must be 'room' or 'space', got {!r}".format(identify_by))
    property_name = "Room" if identify_by == "room" else "Space"

    facts = {}
    for category in built_in_categories:
        collector = FilteredElementCollector(doc).OfClass(FamilyInstance).WherePasses(ElementCategoryFilter(category))
        for instance in collector:
            try:
                item_id = get_el_id_int(instance.Id)
            except Exception:
                continue

            try:
                reference = get_room_or_space_id(instance, phase, property_name)
            except Exception:
                reference = None

            try:
                own = getattr(instance, "Category", None)
                category_name = own.Name if own is not None else None
            except Exception:
                category_name = None

            facts[item_id] = {
                "reference": reference,
                "category": category_name,
                "family_name": get_family_name(instance),
                "host": get_host_info(instance),
            }
    return facts


def get_instances_by_room_id(doc, phase, built_in_categories, allowed_ids=None):
    """
    Returns the family instances of the categories grouped by the room they are in during a phase.

    An instance whose room can not be read, or which is in no room, is left out.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param phase: The phase the room is read in.
    :type phase: Autodesk.Revit.DB.Phase
    :param built_in_categories: The categories to walk.
    :type built_in_categories: list of Autodesk.Revit.DB.BuiltInCategory
    :param allowed_ids: Only instances with these ids (int) are considered; None considers all.
    :type allowed_ids: set of int or None

    :return: Room id (int) mapped to the instances in it.
    :rtype: dict
    """

    by_room = {}
    for category in built_in_categories:
        collector = FilteredElementCollector(doc).OfClass(FamilyInstance).WherePasses(ElementCategoryFilter(category))
        for instance in collector:
            try:
                if allowed_ids is not None and get_el_id_int(instance.Id) not in allowed_ids:
                    continue
                room_id = get_room_or_space_id(instance, phase, "Room")
            except Exception:
                continue
            if room_id is not None:
                by_room.setdefault(room_id, []).append(instance)
    return by_room
