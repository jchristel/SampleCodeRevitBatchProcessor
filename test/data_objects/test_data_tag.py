"""Round trip of the tag data classes: object -> json -> object, on CPython.

`duHast.Utilities.Objects.base` imports `System.Int64`, which only exists under .NET, so a
stand-in is registered first. Nothing here touches Revit.
"""

import json
import os
import sys
import types
import unittest

if "System" not in sys.modules:
    system = types.ModuleType("System")
    system.Int64 = int
    sys.modules["System"] = system

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from duHast.Data.Objects.Collectors.data_tag import DataTag  # noqa: E402
from duHast.Data.Objects.Collectors.data_tag_type import DataTagType  # noqa: E402
from duHast.Data.Objects.Collectors.data_tagged_element import DataTaggedElement  # noqa: E402
from duHast.Data.Objects.Collectors.data_view_plan import DataViewPlan  # noqa: E402
from duHast.Data.Objects.Collectors.Properties.Geometry import geometry_base  # noqa: E402
from duHast.Geometry.point_3 import Point3  # noqa: E402


def round_trip(obj, cls):
    return cls(j=json.loads(obj.to_json()))


def a_tagged_element():
    el = DataTaggedElement()
    el.host_element_id = 4711
    el.category = "Furniture"
    el.family_name = "Bed"
    el.type_name = "Queen"
    el.location_point = geometry_base.DataGeometryBase(data_type="location_point")
    el.location_point.translation_coord = Point3(1000.0, 2000.0, 0.0)
    el.elbow_location = Point3(1100.0, 2100.0, 0.0)
    return el


def a_tag():
    tag = DataTag()
    tag.id = 99
    tag.tag_kind = "independent"
    tag.tag_type = DataTagType()
    tag.tag_type.category = "Furniture Tags"
    tag.tag_type.family_name = "M_Furniture Tag"
    tag.tag_type.type_name = "Standard"
    tag.text = "BED"
    tag.rotation = 0.5
    tag.orientation = "Horizontal"
    tag.has_leader = True
    tag.leader_end_condition = "Free"
    tag.point = Point3(1500.0, 2500.0, 0.0)
    tag.tagged_elements = [a_tagged_element()]
    return tag


class TagRoundTrip(unittest.TestCase):
    def test_a_tag_survives_json(self):
        tag = a_tag()
        back = round_trip(tag, DataTag)
        self.assertEqual(tag, back)
        self.assertEqual("M_Furniture Tag", back.tag_type.family_name)
        self.assertEqual("Queen", back.tagged_elements[0].type_name)
        self.assertEqual(1000.0, back.tagged_elements[0].location_point.translation_coord.x)

    def test_unread_stays_unread(self):
        el = DataTaggedElement()
        back = round_trip(el, DataTaggedElement)
        self.assertIsNone(back.location_point)
        self.assertIsNone(back.elbow_location)
        self.assertEqual(-1, back.host_element_id)

    def test_a_linked_element_keeps_its_link_ids(self):
        el = DataTaggedElement()
        el.link_element_id = 12
        el.link_instance_id = 34
        back = round_trip(el, DataTaggedElement)
        self.assertEqual((-1, 12, 34), (back.host_element_id, back.link_element_id, back.link_instance_id))

    def test_a_tag_written_before_the_new_fields_still_reads(self):
        old = {"point": {"x": 1.0, "y": 2.0, "z": 0.0}, "leader_element_reference_id": 5}
        tag = DataTag(j=old)
        self.assertEqual(5, tag.leader_element_reference_id)
        self.assertEqual([], tag.tagged_elements)
        self.assertEqual("", tag.tag_type.family_name)

    def test_a_view_carries_its_tags_and_scale(self):
        view = DataViewPlan()
        view.view_scale = 50
        view.tags = [a_tag()]
        back = round_trip(view, DataViewPlan)
        self.assertEqual(50, back.view_scale)
        self.assertEqual(view.tags, back.tags)

    def test_views_with_the_same_tags_in_another_order_are_equal(self):
        a, b = a_tag(), a_tag()
        b.id = 100
        one, two = DataViewPlan(), DataViewPlan()
        one.tags = [a, b]
        two.tags = [b, a]
        self.assertEqual(one, two)


if __name__ == "__main__":
    unittest.main()
