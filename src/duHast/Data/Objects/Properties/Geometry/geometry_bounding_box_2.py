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
from duHast.Data.Objects.Properties.Geometry import geometry_base
from duHast.Data.Objects.Properties.data_property_names import DataPropertyNames
from duHast.Geometry.bounding_box_2 import BoundingBox2
from duHast.Geometry.point_2 import Point2


class DataBoundingBox2(geometry_base.DataGeometryBase):
    data_type = "bounding box 2"

    def __init__(self, j=None):
        """
        Class constructor for a 2D bounding box.

        :param j:  json formatted dictionary of this class, defaults to {}
        :type j: dict, optional
        """

        # store data type  in base class
        super(DataBoundingBox2, self).__init__(DataBoundingBox2.data_type, j)

        # set default values
        self.bounding_box = BoundingBox2(point1=Point2(0.0,0.0), point2=Point2(0.0,0.0))

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
                # get the bounding box
                bbox = j.get(DataPropertyNames.BOUNDING_BOX.value,{})
                self.bounding_box = BoundingBox2(j=bbox)
            except Exception as e:
                raise ValueError(
                    "Node {} failed to initialise with: {}".format(self.data_type, e)
                )
    
    def set_bounding_box_by_points(self, min, max):
        """
        Update the geometry bounding box with new values

        :param min: lower left corner of the bounding box
        :type min: :class:`.Point2`
        :param max: upper corner of the bounding box
        :type max: :class:`.Point2`
        :raises ValueError: _description_
        :raises ValueError: _description_
        """
        if isinstance(min, Point2)==False:
            raise ValueError ("Min needs to be a point2 instance, got {} instead:".format(type(min)))
        
        if isinstance(max, Point2)==False:
            raise ValueError ("Max needs to be a point2 instance, got {} instead:".format(type(min)))
        
        self.bounding_box.update(point1=min, point2=max)
