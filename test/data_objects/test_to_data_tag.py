"""The Revit-free part of the tag converter: matching a tagged element to its leader.

Autodesk.Revit.DB is replaced by a mock module so the converter imports on CPython; reading
tags from a real model can only be checked in Revit.
"""

import os
import sys
import types
import unittest
from unittest import mock

for name in ("Autodesk", "Autodesk.Revit", "Autodesk.Revit.DB"):
    sys.modules.setdefault(name, mock.MagicMock())
if "System" not in sys.modules:
    system = types.ModuleType("System")
    system.Int64 = int
    sys.modules["System"] = system

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from duHast.Data.Objects.Collectors.Properties.data_tag_kind_names import DataTagKindNames  # noqa: E402
from duHast.Revit.Annotation.Export.to_data_tag import (  # noqa: E402
    HOST_ELEMENT_ID,
    LINK_ELEMENT_ID,
    NO_ID,
    _element_id,
    _spatial_reference,
    pick_leader_entry,
)


def entry(element_id, linked_id, label):
    return {
        "leader_reference": {"leader_element_reference_id": element_id, "leader_linked_element_reference_id": linked_id},
        "elbow_location": label,
    }


class PickLeaderEntry(unittest.TestCase):
    def test_matches_a_local_element_by_its_id(self):
        entries = [entry(1, -1, "a"), entry(2, -1, "b")]
        self.assertEqual("b", pick_leader_entry(entries, 2, NO_ID, 0)["elbow_location"])

    def test_matches_a_linked_element_by_the_link_id(self):
        entries = [entry(-1, 10, "a"), entry(-1, 20, "b")]
        self.assertEqual("b", pick_leader_entry(entries, NO_ID, 20, 0)["elbow_location"])

    def test_an_entry_naming_other_elements_is_not_used_by_position(self):
        self.assertIsNone(pick_leader_entry([entry(1, -1, "a")], 9, NO_ID, 0))

    def test_entries_without_ids_fall_back_to_position(self):
        entries = [{"elbow_location": "only"}]
        self.assertEqual("only", pick_leader_entry(entries, 5, NO_ID, 0)["elbow_location"])
        self.assertIsNone(pick_leader_entry(entries, 5, NO_ID, 1))

    def test_no_entries_is_none(self):
        self.assertIsNone(pick_leader_entry([], 1, NO_ID, 0))
        self.assertIsNone(pick_leader_entry(None, 1, NO_ID, 0))


class RoomTagLike(object):
    """A RoomTag of Revit 2026: it names its room by `Room` and has no tagged-id properties."""

    def __init__(self, room):
        self.Room = room


class SpatialReference(unittest.TestCase):
    def test_a_room_tag_is_read_through_its_room(self):
        room = types.SimpleNamespace(Id=2620712)
        reference = _spatial_reference(RoomTagLike(room), DataTagKindNames.ROOM)
        self.assertEqual(2620712, reference[HOST_ELEMENT_ID])

    def test_a_tag_with_no_room_and_no_id_properties_gives_none(self):
        self.assertIsNone(_spatial_reference(RoomTagLike(None), DataTagKindNames.ROOM))

    def test_a_space_tag_uses_space_and_an_area_tag_uses_area(self):
        tag = types.SimpleNamespace(Space=types.SimpleNamespace(Id=7), Area=types.SimpleNamespace(Id=8))
        self.assertEqual(7, _spatial_reference(tag, DataTagKindNames.SPACE)[HOST_ELEMENT_ID])
        self.assertEqual(8, _spatial_reference(tag, DataTagKindNames.AREA)[HOST_ELEMENT_ID])


class ElementIdFromInteger(unittest.TestCase):
    def test_the_integer_reaches_the_constructor_as_a_named_type(self):
        revit_element_id = sys.modules["Autodesk.Revit.DB"].ElementId
        revit_element_id.reset_mock()
        _element_id(42)
        revit_element_id.assert_called_once_with(int(42))


if __name__ == "__main__":
    unittest.main()
