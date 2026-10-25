"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Data storage base class used for element tags in views.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- contains 

    - the view id
    - the element tagged id
    - tag location
    - has tag leader
    - has tag elbow
    - elbow location
    - tag kind, tag type (category, family name, type name), text, rotation, orientation
    - the elements tagged, each with its own leader (see DataTaggedElement)

    Positions are millimetres in the model's own coordinates. `point` is the tag head; the
    `elbow_location`, `leader_end`, `leader_reference` and `leader_element_reference_id`
    fields are the earlier single-reference form and stay for readers written against it.
    Raw measurements only: where a tag sits relative to its element is worked out by the user
    of the data.

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

import json

from duHast.Data.Objects.Collectors.data_base import DataBase
from duHast.Geometry.point_3 import Point3
from duHast.Data.Objects.Collectors.Properties.data_property_names import (
    DataPropertyNames,
)
from duHast.Data.Objects.Collectors.Properties.data_tag_kind_names import (
    DataTagKindNames,
)
from duHast.Data.Objects.Collectors.data_tag_type import DataTagType
from duHast.Data.Objects.Collectors.data_tagged_element import DataTaggedElement
from duHast.Data.Objects.Collectors.Properties.Geometry.geometry_bounding_box_2 import (
    DataGeometryBoundingBox2,
)


class DataTag(DataBase):

    data_type = "tag"

    def __init__(self, j=None):
        """
        Class constructor for a annotation tag.

        :param j: A json formatted dictionary of this class, defaults to None
        :type j: dict, optional
        """

        # initialise parent classes with values
        super(DataTag, self).__init__(data_type=DataTag.data_type)

        # set default values
        self.bounding_box = DataGeometryBoundingBox2()
        self.elbow_location = Point3(0.0, 0.0, 0.0)
        self.point = Point3(0.0, 0.0, 0.0)
        self.leader_end = None
        self.leader_reference = None
        self.leader_element_reference_id = -1
        # the tag element's id in its model (-1 unread)
        self.id = -1
        self.tag_kind = DataTagKindNames.INDEPENDENT
        self.tag_type = DataTagType()
        # unread / no text is an empty string; a tag whose text could not be read says so
        self.text = ""
        self.rotation = 0.0
        self.orientation = ""
        self.has_leader = False
        self.leader_end_condition = ""
        self.tagged_elements = []

        json_var = None
        # check if any data was past in with constructor!
        if j is not None:
            # check type of data that came in:
            if isinstance(j, str):
                # a string
                json_var = json.loads(j)
            elif isinstance(j, dict):
                # no action required
                json_var = j.copy()
            else:
                raise TypeError(
                    "Argument j supplied must be of type string or type dictionary. Got {} instead.".format(
                        type(j)
                    )
                )

            # attempt to populate from json
            try:
                self.bounding_box = DataGeometryBoundingBox2(
                    json_var.get(DataPropertyNames.BOUNDING_BOX, None)
                )

                # get the point location
                point = json_var.get(DataPropertyNames.POINT, None)
                if point:
                    self.point = Point3(j=point)

                # get the elbow location
                elbow_location = json_var.get(
                    DataPropertyNames.TAG_ELBOW_LOCATION, None
                )
                if elbow_location:
                    self.elbow_location = Point3(j=elbow_location)

                self.leader_end = json_var.get(
                    DataPropertyNames.TAG_LEADER_END, self.leader_end
                )
                self.leader_reference = json_var.get(
                    DataPropertyNames.TAG_LEADER_REFERENCE, self.leader_reference
                )

                self.leader_element_reference_id = json_var.get(
                    DataPropertyNames.TAG_LEADER_ELEMENT_REFERENCE_ID,
                    self.leader_element_reference_id,
                )
                if not isinstance(self.leader_element_reference_id, int):
                    raise TypeError(
                        "Expected 'leader_element_reference_id' to be an int, got {}".format(
                            type(self.leader_element_reference_id)
                        )
                    )

                self.id = json_var.get(DataPropertyNames.ID, self.id)
                self.tag_kind = json_var.get(DataPropertyNames.TAG_KIND, self.tag_kind)
                self.tag_type = DataTagType(json_var.get(DataPropertyNames.TAG_TYPE, None))
                self.text = json_var.get(DataPropertyNames.TAG_TEXT, self.text)
                self.rotation = json_var.get(DataPropertyNames.TAG_ROTATION, self.rotation)
                self.orientation = json_var.get(DataPropertyNames.TAG_ORIENTATION, self.orientation)
                self.has_leader = json_var.get(DataPropertyNames.TAG_HAS_LEADER, self.has_leader)
                self.leader_end_condition = json_var.get(
                    DataPropertyNames.TAG_LEADER_END_CONDITION, self.leader_end_condition
                )
                self.tagged_elements = [
                    DataTaggedElement(j=t)
                    for t in json_var.get(DataPropertyNames.TAGGED_ELEMENTS, [])
                ]

            except Exception as e:
                raise type(e)(
                    "Node {} failed to initialise with: {}".format(self.data_type, e)
                )

    def __eq__(self, other):
        """
        equal compare

        Args:
            other (DataTag): another DataTag instance

        Returns:
            bool: True if equal, otherwise False
        """
        if not isinstance(other, DataTag):
            return NotImplemented
        return (
            self.bounding_box == other.bounding_box
            and self.elbow_location == other.elbow_location
            and self.point == other.point
            and self.leader_end == other.leader_end
            and self.leader_reference == other.leader_reference
            and self.leader_element_reference_id == other.leader_element_reference_id
            and self.id == other.id
            and self.tag_kind == other.tag_kind
            and self.tag_type == other.tag_type
            and self.text == other.text
            and self.rotation == other.rotation
            and self.orientation == other.orientation
            and self.has_leader == other.has_leader
            and self.leader_end_condition == other.leader_end_condition
            and self.tagged_elements == other.tagged_elements
        )

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(
            (
                self.bounding_box,
                self.elbow_location,
                self.point,
                self.leader_end,
                self.leader_reference,
                self.leader_element_reference_id,
                self.id,
                self.tag_kind,
                self.tag_type,
                tuple(self.tagged_elements),
            )
        )
