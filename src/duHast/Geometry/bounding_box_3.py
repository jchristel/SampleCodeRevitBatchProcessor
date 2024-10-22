"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A 3D bounding box base class.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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
from duHast.Geometry.bounding_box_base import BoundingBoxBase
from duHast.Geometry.point_3 import Point3
from duHast.Geometry.geometry_property_names import GeometryPropertyNames

class BoundingBox3D(BoundingBoxBase):
    def __init__(self, point1=None, point2=None, j=None):

        # ini super with json field
        super(BoundingBox3D, self).__init__(j=j)

         # check first if a json string / dictionary is provided
        if j:
            point1 = Point3(**self.json_ini[GeometryPropertyNames.POINT1.value])
            point2 = Point3(**self.json_ini[GeometryPropertyNames.POINT2.value])
        
        # If both point1 and point2 are None after handling JSON, raise an error
        if point1 is None or point2 is None:
            raise ValueError("Either two Point2 instances or a JSON string with point data needs to be provided.")

        # some type checking
        if not isinstance(point1,Point3):
            raise TypeError("point1 expected Point3 instance. Got {} instead:".format(type(point1)))
        if not isinstance(point2,Point3):
            raise TypeError("point3 expected Point3 instance. Got {} instead:".format(type(point1)))


        self.min_x = min(point1.x, point2.x)
        self.max_x = max(point1.x, point2.x)
        self.min_y = min(point1.y, point2.y)
        self.max_y = max(point1.y, point2.y)
        self.min_z = min(point1.z, point2.z)
        self.max_z = max(point1.z, point2.z)

    def contains(self, point):
        return (self.min_x <= point.x <= self.max_x and
                self.min_y <= point.y <= self.max_y and
                self.min_z <= point.z <= self.max_z)

    def __str__(self):
        return "BoundingBox3D({}, {}, {}, {}, {}, {})".format(
            self.min_x, self.min_y, self.min_z, self.max_x, self.max_y, self.max_z)
