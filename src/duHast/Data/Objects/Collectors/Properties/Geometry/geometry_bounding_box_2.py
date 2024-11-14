"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Geometry data bounding_box storage class.
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

import json
from duHast.Data.Objects.Collectors.Properties.Geometry import geometry_base
from duHast.Geometry.bounding_box_2 import BoundingBox2


class DataGeometryBoundingBox2(BoundingBox2, geometry_base.DataGeometryBase):
    data_type = "bounding box 2"

    def __init__(self, j=None, *args, **kwargs):
        """
        Class constructor for a 2D bounding box.

        :param j:  json formatted dictionary of this class, defaults to {}
        :type j: dict, optional
        """

        # store data type  in base class
        super(DataGeometryBoundingBox2, self).__init__(
            data_type=DataGeometryBoundingBox2.data_type, j=j, *args, **kwargs
        )

        # check if any data was past in with constructor!
        json_var = None
        if j is not None:
            # check type of data that came in:
            if isinstance(j, str):
                # a string
                json_var = json.loads(j)
            elif isinstance(j, dict):
                # no action required
                json_var=j.copy()
            else:
                raise TypeError(
                    "Argument j supplied must be of type string or type dictionary. Got {} instead.".format(
                        type(j)
                    )
                )

            # attempt to populate from json
            try:
                pass
                # get the bounding box
                #bbox = json_var.get(DataPropertyNames.BOUNDING_BOX, None)
                # check if we got None back...if so use what is the default
                # since a bounding box ini from an empty dictionary will fail
                #if bbox is not None:
                #    self.bounding_box = BoundingBox2(j=bbox)
            except Exception as e:
                raise type(e)(
                    "Node {} failed to initialise with: {}".format(self.data_type, e)
                )


    def __eq__(self, other):
        if not isinstance(other, DataGeometryBoundingBox2):
            return NotImplemented
        # Check equality of each superclass
        return BoundingBox2.__eq__(self, other) and geometry_base.DataGeometryBase.__eq__(self, other)
        #return self.bounding_box == other.bounding_box

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        # Combine the hash values of each base class
        return hash((BoundingBox2.__hash__(self), geometry_base.DataGeometryBase.__hash__(self)))