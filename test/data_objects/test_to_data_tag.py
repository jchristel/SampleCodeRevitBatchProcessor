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

from duHast.Revit.Annotation.Export.to_data_tag import NO_ID, pick_leader_entry  # noqa: E402


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


if __name__ == "__main__":
    unittest.main()
