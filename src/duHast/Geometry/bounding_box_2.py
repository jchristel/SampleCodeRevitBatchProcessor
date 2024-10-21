"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A 2D bounding box base class.
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
from duHast.Geometry.point_2 import Point2

class BoundingBox2(BoundingBoxBase):
    def __init__(self, point1, point2):
        super(BoundingBox2, self).__init__()

        # some type checking
        if not isinstance(point1,Point2):
            raise TypeError("point1 expected Point2 instance. Got {} instead:".format(type(point1)))
        if not isinstance(point2,Point2):
            raise TypeError("point3 expected Point2 instance. Got {} instead:".format(type(point1)))
        
        self.min_x = min(point1.x, point2.x)
        self.max_x = max(point1.x, point2.x)
        self.min_y = min(point1.y, point2.y)
        self.max_y = max(point1.y, point2.y)

    def contains(self, point):
        return (self.min_x <= point.x <= self.max_x and
                self.min_y <= point.y <= self.max_y)

    def __str__(self):
        return "BoundingBox2D({}, {}, {}, {})".format(self.min_x, self.min_y, self.max_x, self.max_y)
