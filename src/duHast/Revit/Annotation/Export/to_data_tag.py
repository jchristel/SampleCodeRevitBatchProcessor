"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Reads the tags in a view into :class:`.DataTag` instances.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- one collector per class of tag: independent tags (any category, keynotes included) and the
  spatial element tags (room, space, area), which are NOT independent tags in Revit
- reuses :mod:`independent_tags_tagged_elements` and :mod:`independent_tags_elbow_properties`
  rather than reading those again
- adds what those leave out: the tag's type and the tagged element's category, family name,
  type name and location (through the link transform for an element in a linked model)

Raw measurements only: millimetres in the model's own coordinates, as `DataItem` writes them.
Where a tag sits relative to its element is for the user of the data to work out.

A tag that cannot be read is skipped and named in `problems` (or `take_problems`), never half written.
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
    BuiltInCategory,
    Element,
    ElementId,
    FilteredElementCollector,
    IndependentTag,
    LocationPoint,
)

from duHast.Data.Objects.Collectors.data_tag import DataTag
from duHast.Data.Objects.Collectors.data_tag_type import DataTagType
from duHast.Revit.Common.element_id import get_el_id_int, get_element_id_from_int
from duHast.Data.Objects.Collectors.data_tagged_element import DataTaggedElement
from duHast.Data.Objects.Collectors.Properties.data_tag_kind_names import (
    DataTagKindNames,
)
from duHast.Data.Objects.Collectors.Properties.Geometry import geometry_base
from duHast.Geometry.matrix import Matrix
from duHast.Revit.Annotation.independent_tags_elbow_properties import (
    ELBOW_LOCATION,
    LEADER_END,
    LEADER_REFERENCE,
    LEADER_ELEMENT_REFERENCE_ID,
    LEADER_LINKED_ELEMENT_REFERENCE_ID,
    get_elbow_properties,
)
from duHast.Revit.Annotation.independent_tags_tagged_elements import (
    HOST_ELEMENT_ID,
    LINK_ELEMENT_ID,
    LINK_INSTANCE_ID,
    get_tagged_elements,
)
from duHast.Revit.Common.Geometry.points import (
    convert_XYZ_to_point3,
    get_point_as_doubles,
)

# the spatial element tags, by category: `OfClass(SpatialElementTag)` is an abstract class
SPATIAL_TAG_KINDS = [
    (BuiltInCategory.OST_RoomTags, DataTagKindNames.ROOM),
    (BuiltInCategory.OST_MEPSpaceTags, DataTagKindNames.SPACE),
    (BuiltInCategory.OST_AreaTags, DataTagKindNames.AREA),
]

NO_ID = -1

# Tags that could not be read, when the caller (a view export deep in a sheet export) had no
# list to hand in. Taken, and cleared, by `take_problems`.
_problems = []


def take_problems():
    """
    The lines for every tag skipped since the last call, and clears them.

    The viewport export reads tags without a list of its own to report into, so the skipped ones
    collect here and whoever started the export asks for them afterwards.

    :return: One line per skipped tag.
    :rtype: [str]
    """

    taken = list(_problems)
    del _problems[:]
    return taken


def _id_value(element_id):
    """An element id as an int, or -1 for none / invalid."""
    if element_id is None or element_id == ElementId.InvalidElementId:
        return NO_ID
    return get_el_id_int(element_id)


def _name_of(element):
    """An element's name, or an empty string when it has none."""
    try:
        return Element.Name.GetValue(element) or ""
    except Exception:
        return ""


def _category_name(element):
    try:
        return element.Category.Name or ""
    except Exception:
        return ""


def _family_and_type_names(doc, element):
    """`(family name, type name)` of an element, empty strings where unread."""
    try:
        element_type = doc.GetElement(element.GetTypeId())
    except Exception:
        return "", ""
    if element_type is None:
        return "", ""
    family_name = ""
    try:
        family_name = element_type.FamilyName or ""
    except Exception:
        pass
    return family_name, _name_of(element_type)


def pick_leader_entry(entries, host_id, link_id, index):
    """
    The leader properties belonging to one tagged element.

    Revit 2022 onwards gives one entry per tagged reference, each naming its element (and the
    linked element when it is in a link). Earlier versions give a single entry without ids.
    Matched on ids first; only when no entry names any id is the position used.

    :param entries: The output of `get_elbow_properties`.
    :type entries: [dict]
    :param host_id: Element id of the tagged element in this model, -1 when it is in a link.
    :type host_id: int
    :param link_id: Element id of the tagged element in the link, -1 when it is in this model.
    :type link_id: int
    :param index: Position of the tagged element in the tag's list.
    :type index: int

    :return: The matching entry, or None.
    :rtype: dict or None
    """

    if not entries:
        return None
    named = False
    for entry in entries:
        reference = entry.get(LEADER_REFERENCE) or {}
        element_id = reference.get(LEADER_ELEMENT_REFERENCE_ID)
        linked_id = reference.get(LEADER_LINKED_ELEMENT_REFERENCE_ID)
        if element_id is None and linked_id is None:
            continue
        named = True
        if link_id != NO_ID and linked_id == link_id:
            return entry
        if link_id == NO_ID and host_id != NO_ID and element_id == host_id:
            return entry
    if named:
        return None
    return entries[index] if index < len(entries) else None


def _location_of(element, transform):
    """
    The element's point location in mm as a `DataGeometryBase`, or None when it has none.

    `transform` is the link instance's total transform for an element in a linked model, so
    the point and the facing are in this model's coordinates; None for an element in this model.
    """

    location = element.Location
    if not isinstance(location, LocationPoint):
        return None
    data = geometry_base.DataGeometryBase(data_type="location_point")
    point = location.Point
    if transform is not None:
        point = transform.OfPoint(point)
    data.translation_coord = convert_XYZ_to_point3(point)
    try:
        own = element.GetTransform()
        vectors = [own.BasisX, own.BasisY, own.BasisZ]
        if transform is not None:
            vectors = [transform.OfVector(v) for v in vectors]
        data.rotation_coord = Matrix(
            rows=3,
            cols=3,
            elements=[get_point_as_doubles(v, include_z=True) for v in vectors],
        )
    except Exception:
        # not a family instance: the position is still worth having, the facing is left unread
        pass
    return data


def _tagged_element(doc, reference, index, leader_entries):
    """One `DataTaggedElement` from one entry of `get_tagged_elements`."""

    data = DataTaggedElement()
    if not isinstance(reference, dict):
        # get_tagged_elements answers with a bare invalid id when it could not read the tag
        return data
    data.host_element_id = _id_value(reference.get(HOST_ELEMENT_ID))
    data.link_element_id = _id_value(reference.get(LINK_ELEMENT_ID))
    data.link_instance_id = _id_value(reference.get(LINK_INSTANCE_ID))

    element = None
    transform = None
    element_doc = doc
    if data.host_element_id != NO_ID:
        element = doc.GetElement(get_element_id_from_int(data.host_element_id))
    elif data.link_instance_id != NO_ID:
        link_instance = doc.GetElement(get_element_id_from_int(data.link_instance_id))
        link_doc = link_instance.GetLinkDocument() if link_instance is not None else None
        # an unloaded link has no document: the ids are all there is
        if link_doc is not None and data.link_element_id != NO_ID:
            element_doc = link_doc
            element = link_doc.GetElement(get_element_id_from_int(data.link_element_id))
            transform = link_instance.GetTotalTransform()
    if element is not None:
        data.category = _category_name(element)
        data.family_name, data.type_name = _family_and_type_names(element_doc, element)
        data.location_point = _location_of(element, transform)

    entry = pick_leader_entry(leader_entries, data.host_element_id, data.link_element_id, index)
    if entry:
        elbow = entry.get(ELBOW_LOCATION)
        end = entry.get(LEADER_END)
        if elbow is not None:
            data.elbow_location = convert_XYZ_to_point3(elbow)
        if end is not None:
            data.leader_end = convert_XYZ_to_point3(end)
    return data


def _tag_type(doc, tag):
    data = DataTagType()
    data.category = _category_name(tag)
    data.family_name, data.type_name = _family_and_type_names(doc, tag)
    return data


def independent_tag_to_data(doc, tag):
    """
    Converts one independent tag.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param tag: The tag.
    :type tag: Autodesk.Revit.DB.IndependentTag

    :return: The tag as data.
    :rtype: :class:`.DataTag`
    """

    data = DataTag()
    data.id = _id_value(tag.Id)
    data.tag_kind = DataTagKindNames.INDEPENDENT
    data.tag_type = _tag_type(doc, tag)
    try:
        data.text = tag.TagText or ""
    except Exception:
        # reading the text can throw (a tag of a deleted parameter, say): leave it unread
        data.text = ""
    data.has_leader = bool(tag.HasLeader)
    data.rotation = float(tag.RotationAngle)
    data.orientation = str(tag.TagOrientation)
    data.point = convert_XYZ_to_point3(tag.TagHeadPosition)

    leader_entries = []
    if data.has_leader:
        data.leader_end_condition = str(tag.LeaderEndCondition)
        leader_entries = get_elbow_properties(doc=doc, tag=tag, points_as_double=False) or []

    references = get_tagged_elements(doc=doc, tag=tag) or []
    data.tagged_elements = [
        _tagged_element(doc, reference, i, leader_entries)
        for i, reference in enumerate(references)
    ]
    return data


# The property a spatial element tag names its element by, per kind. Revit 2026's RoomTag has
# no TaggedLocalElementId / TaggedElementId (those are on IndependentTag): measured, not assumed.
_SPATIAL_ELEMENT_PROPERTY = {
    DataTagKindNames.ROOM: "Room",
    DataTagKindNames.SPACE: "Space",
    DataTagKindNames.AREA: "Area",
}


def _spatial_reference(tag, kind):
    """
    The one room, space or area a spatial tag refers to, as the reference dictionary
    `_tagged_element` reads, or None when this tag gives no way to find it.

    The element property (`Room`, `Space`, `Area`) is read first: it is the one that exists on
    every version seen. The older id properties are tried only when it gives nothing, which is
    also the case for an element that lives in a link.

    :param tag: The tag.
    :type tag: Autodesk.Revit.DB.SpatialElementTag
    :param kind: One of :class:`.DataTagKindNames`.
    :type kind: str

    :return: The reference, or None.
    :rtype: {str:Autodesk.Revit.DB.ElementId} or None
    """

    invalid = ElementId.InvalidElementId
    reference = {HOST_ELEMENT_ID: invalid, LINK_ELEMENT_ID: invalid, LINK_INSTANCE_ID: invalid}

    name = _SPATIAL_ELEMENT_PROPERTY.get(kind)
    if name:
        try:
            element = getattr(tag, name)
        except Exception:
            element = None
        if element is not None:
            reference[HOST_ELEMENT_ID] = element.Id
            return reference

    try:
        local = tag.TaggedLocalElementId
        if local != invalid:
            reference[HOST_ELEMENT_ID] = local
            return reference
        tagged = tag.TaggedElementId
        reference[LINK_ELEMENT_ID] = tagged.LinkedElementId
        reference[LINK_INSTANCE_ID] = tagged.LinkInstanceId
        return reference
    except Exception:
        # neither way of naming the element exists here: the tag is kept with no tagged element
        return None


def spatial_tag_to_data(doc, tag, kind):
    """
    Converts one room, space or area tag.

    The Revit API for these differs from independent tags: they refer to one spatial element,
    have a single leader, and no rotation. Anything not available on a version is left unread.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param tag: The tag.
    :type tag: Autodesk.Revit.DB.SpatialElementTag
    :param kind: One of :class:`.DataTagKindNames`.
    :type kind: str

    :return: The tag as data.
    :rtype: :class:`.DataTag`
    """

    data = DataTag()
    data.id = _id_value(tag.Id)
    data.tag_kind = kind
    data.tag_type = _tag_type(doc, tag)
    data.point = convert_XYZ_to_point3(tag.TagHeadPosition)
    data.has_leader = bool(tag.HasLeader)

    leader = {}
    if data.has_leader:
        try:
            data.leader_end_condition = str(tag.LeaderEndCondition)
        except Exception:
            pass
        try:
            if tag.HasElbow:
                leader[ELBOW_LOCATION] = tag.LeaderElbow
        except Exception:
            pass
        try:
            leader[LEADER_END] = tag.LeaderEnd
        except Exception:
            pass

    # the tagged room / space / area: local to this model, or in a link
    reference = _spatial_reference(tag, kind)
    if reference is not None:
        data.tagged_elements = [_tagged_element(doc, reference, 0, [leader] if leader else [])]
    return data


def get_tags_in_view(doc, view, problems=None):
    """
    All tags drawn in a view, of every class this reads.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param view: The view.
    :type view: Autodesk.Revit.DB.View
    :param problems: Receives a line for each tag that could not be read, defaults to the module's own list (see `take_problems`)
    :type problems: list of str, optional

    :return: The tags, in the order Revit gives them.
    :rtype: [:class:`.DataTag`]
    """

    tags = []
    if problems is None:
        problems = _problems

    def attempt(convert, tag):
        try:
            tags.append(convert())
        except Exception as e:
            problems.append("tag {} in view {}: {}".format(_id_value(tag.Id), _id_value(view.Id), e))

    for tag in FilteredElementCollector(doc, view.Id).OfClass(IndependentTag):
        attempt(lambda: independent_tag_to_data(doc, tag), tag)

    for category, kind in SPATIAL_TAG_KINDS:
        collector = FilteredElementCollector(doc, view.Id).OfCategory(category).WhereElementIsNotElementType()
        for tag in collector:
            attempt(lambda: spatial_tag_to_data(doc, tag, kind), tag)
    return tags
