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

from duHast.Data.Objects.data_base import DataBase

from duHast.Data.Objects.Properties.data_property_names import DataPropertyNames
from duHast.Data.Objects.Properties.Geometry.geometry_bounding_box_2 import (
    DataBoundingBox2,
)


class DataTag(DataBase):

    data_type = "tag"

    def __init__(self, j=None):
        """
        Class constructor for a view_3d.

        :param j: A json formatted dictionary of this class, defaults to {}
        :type j: dict, optional
        """

        # initialise parent classes with values
        super(DataTag, self).__init__(data_type=DataTag.data_type)

        # set default values
        self.bounding_box = DataBoundingBox2()
        self.elbow_location = [0,0,0]
        self.leader_end = None
        self.leader_reference = None
        self.leader_element_reference_id =-1

        # check if any data was past in with constructor!
        if j != None and len(j) > 0:
            # check type of data that came in:
            if isinstance(j, str):
                # a string
                j = json.loads(j)
            elif isinstance(j, dict):
                # no action required
                pass
            else:
                raise TypeError(
                    "Argument j supplied must be of type string or type dictionary. Got {} instead.".format(
                        type(j)
                    )
                )

            # attempt to populate from json
            try:
                self.bounding_box = DataBoundingBox2(
                    j.get(DataPropertyNames.BOUNDING_BOX.value, {})
                )
                self.elbow_location = j.get(DataPropertyNames.TAG_ELBOW_LOCATION.value, self.elbow_location)
                self.leader_end = j.get(DataPropertyNames.TAG_LEADER_END.value, self.leader_end)
                self.leader_reference = j.get(DataPropertyNames.TAG_LEADER_REFERENCE.value, self.leader_reference)
                self.leader_element_reference_id =j.get(DataPropertyNames.TAG_LEADER_ELEMENT_REFERENCE_ID.value, self.leader_element_reference_id)

            except Exception as e:
                raise ValueError(
                    "Node {} failed to initialise with: {}".format(self.data_type, e)
                )
