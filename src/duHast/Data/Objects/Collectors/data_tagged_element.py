"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Data storage class for one element a tag refers to.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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

from duHast.Data.Objects.Collectors import data_base
from duHast.Data.Objects.Collectors.Properties.Geometry import geometry_base
from duHast.Data.Objects.Collectors.Properties.data_property_names import (
    DataPropertyNames,
)
from duHast.Geometry.point_3 import Point3


class DataTaggedElement(data_base.DataBase):

    data_type = "tagged_element"

    def __init__(self, j=None):
        """
        Class constructor for an element a tag refers to.

        A tag can refer to several elements (a multi category tag, Revit 2022 onwards) and
        each reference carries its own leader, so the leader is stored here and not on the tag.

        **Raw measurements only.** Positions are millimetres in the model's own coordinates,
        as `DataItem.location_point` is. Where a tag sits relative to its element is worked out
        by whoever uses it, so the rule for that can change without re-exporting.

        **The ids say where an observation came from; they are never how it is found again.**
        A blueprint places NEW elements, which get new ids, so a rule for a tag is looked up by
        what the element is (category, family name, type name), and those names are stored here
        on purpose even though the FF&E export holds them too.

        An element in a linked model has `link_element_id` and `link_instance_id` set and
        `host_element_id` at -1.

        :param j: A json formatted dictionary of this class, defaults to None
        :type j: dict, optional
        """

        super(DataTaggedElement, self).__init__(data_type=DataTaggedElement.data_type)

        self.host_element_id = -1
        self.link_element_id = -1
        self.link_instance_id = -1
        # empty string is unread, never guessed
        self.category = ""
        self.family_name = ""
        self.type_name = ""
        # None is unknown: an element with no point location (a wall, say) has none
        self.location_point = None
        # None is no elbow / no free end, not the origin
        self.elbow_location = None
        self.leader_end = None

        if j is not None:
            if isinstance(j, str):
                json_var = json.loads(j)
            elif isinstance(j, dict):
                json_var = j.copy()
            else:
                raise TypeError(
                    "Argument j supplied must be of type string or type dictionary. Got {} instead.".format(
                        type(j)
                    )
                )
            try:
                self.host_element_id = json_var.get(DataPropertyNames.HOST_ELEMENT_ID, self.host_element_id)
                self.link_element_id = json_var.get(DataPropertyNames.LINK_ELEMENT_ID, self.link_element_id)
                self.link_instance_id = json_var.get(DataPropertyNames.LINK_INSTANCE_ID, self.link_instance_id)
                self.category = json_var.get(DataPropertyNames.CATEGORY, self.category)
                self.family_name = json_var.get(DataPropertyNames.FAMILY_NAME, self.family_name)
                self.type_name = json_var.get(DataPropertyNames.TYPE_NAME, self.type_name)

                location = json_var.get(DataPropertyNames.LOCATION_POINT, None)
                if location is not None:
                    self.location_point = geometry_base.DataGeometryBase(
                        data_type="location_point", j=location
                    )
                elbow = json_var.get(DataPropertyNames.TAG_ELBOW_LOCATION, None)
                if elbow is not None:
                    self.elbow_location = Point3(j=elbow)
                end = json_var.get(DataPropertyNames.TAG_LEADER_END, None)
                if end is not None:
                    self.leader_end = Point3(j=end)
            except Exception as e:
                raise type(e)(
                    "Node {} failed to initialise with: {}".format(self.data_type, e)
                )

    def _key(self):
        return (
            self.host_element_id,
            self.link_element_id,
            self.link_instance_id,
            self.category,
            self.family_name,
            self.type_name,
            self.location_point,
            self.elbow_location,
            self.leader_end,
        )

    def __eq__(self, other):
        if not isinstance(other, DataTaggedElement):
            return NotImplemented
        return self._key() == other._key()

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.host_element_id, self.link_element_id, self.link_instance_id))
