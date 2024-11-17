"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Data storage base class used for Revit views.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- contains 

    - the view bounding box in model coordinates

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

from duHast.Data.Objects.Collectors.data_view_base import DataViewBase
from duHast.Data.Objects.Collectors.data_tag import DataTag
from duHast.Data.Objects.Collectors.Properties.data_property_names import DataPropertyNames
from duHast.Data.Objects.Collectors.Properties.Geometry.geometry_bounding_box_2 import (
    DataGeometryBoundingBox2,
)


class DataViewElevation(DataViewBase):

    data_type = "view_elevation"

    def __init__(self, j=None):
        """
        Class constructor for a view_elevation.

        :param j: A json formatted dictionary of this class, defaults to {}
        :type j: dict, optional
        """

        # initialise parent classes with values
        super(DataViewElevation, self).__init__(
            data_type=DataViewElevation.data_type, j=j
        )

        # set default values
        self.bounding_box = DataGeometryBoundingBox2()
        self.tags = []

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

                # get any tags
                tags = json_var.get(DataPropertyNames.TAGS, [])
                for tag in tags:
                    data_tag = DataTag(j=tag)
                    self.tags.append(data_tag)

            except Exception as e:
                raise type(e)(
                    "Node {} failed to initialise with: {}".format(self.data_type, e)
                )

    def __eq__(self, other):
        """
        equal compare

        Args:
            other (DataViewElevation): another DataViewElevation instance

        Returns:
            bool: True if equal, otherwise False
        """
        if not isinstance(other, DataViewElevation):
            return NotImplemented
        return self.bounding_box == other.bounding_box and sorted(
            self.tags, key=lambda data_tag: data_tag.leader_element_reference_id
        ) == sorted(
            other.tags, key=lambda data_tag: data_tag.leader_element_reference_id
        )

    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __hash__(self):
        return hash((self.bounding_box, self.tags))

