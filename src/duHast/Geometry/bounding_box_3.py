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
from duHast.Utilities.compare import is_close


class BoundingBox3(BoundingBoxBase):
    def __init__(self, point1=None, point2=None, j=None, **kwargs):
        """
        A 3D bounding box class.

        :param point1: A 3D point describing a corner of bounding box, defaults to None
        :type point1: :class:`.Point3`, optional
        :param point2: A 3D point describing diagonal opposite corner of bounding box, defaults to None
        :type point2: :class:`.Point3`, optional
        :param j: A json formatted string, representing an instance of this class, defaults to None
        :type j: [str], optional
        :raises ValueError: "Either two Point2 instances or a JSON string with point data needs to be provided."
        :raises TypeError: "point1 expected Point3 instance. Got type instead."
        :raises TypeError: "point2 expected Point3 instance. Got type instead."
        """

        # ini super with json field
        super(BoundingBox3, self).__init__(j=j, **kwargs)

        # the base class only defaults the x and y extents, being 2D
        self._min_z = 0.0
        self._max_z = 0.0

        # check first if a json string / dictionary is provided
        if j:
            # the base class validates the x and y keys only, so the z keys have to be
            # checked here. Without this the lookups below raise a bare KeyError rather
            # than saying what is actually wrong with the json.
            if (
                GeometryPropertyNames.MIN_Z not in self.json_ini
                or GeometryPropertyNames.MAX_Z not in self.json_ini
            ):
                raise ValueError("JSON must contain 'min_z' and 'max_z' keys.")

            point1 = Point3(
                x=self.json_ini[GeometryPropertyNames.MIN_X],
                y=self.json_ini[GeometryPropertyNames.MIN_Y],
                z=self.json_ini[GeometryPropertyNames.MIN_Z],
            )
            point2 = Point3(
                x=self.json_ini[GeometryPropertyNames.MAX_X],
                y=self.json_ini[GeometryPropertyNames.MAX_Y],
                z=self.json_ini[GeometryPropertyNames.MAX_Z],
            )

        # Supplying neither point is allowed and leaves the box at its zero default,
        # matching BoundingBox2. Supplying only ONE is a mistake.
        if (point1 is None) != (point2 is None):
            raise ValueError(
                "Both point1 and point2 must be provided, or neither. Got point1={}, point2={}.".format(
                    type(point1), type(point2)
                )
            )

        if point1 is not None and point2 is not None:
            self.update(point1=point1, point2=point2)

    @property
    def min_z(self):
        """Read-only property for minimum z value."""
        return self._min_z

    @property
    def max_z(self):
        """Read-only property for maximum z value."""
        return self._max_z

    def update(self, point1, point2):
        """
        Update the size of the bounding box by points

        :param point1: min point on bounding box
        :type point1: :class:`.Point3`
        :param point2: max point of bounding box
        :type point2: :class:`.Point3`
        :raises TypeError: _description_
        :raises TypeError: _description_
        """
        # check if both points are provided
        if point1 is None or point2 is None:
            raise ValueError("Both point1 and point2 must be provided.")

        # Type checking
        if not isinstance(point1, Point3):
            raise TypeError(
                "point1 expected Point3 instance. Got {} instead.".format(type(point1))
            )
        if not isinstance(point2, Point3):
            raise TypeError(
                "point2 expected Point3 instance. Got {} instead.".format(type(point2))
            )

        self._min_x = min(point1.x, point2.x)
        self._max_x = max(point1.x, point2.x)

        self._min_y = min(point1.y, point2.y)
        self._max_y = max(point1.y, point2.y)

        self._min_z = min(point1.z, point2.z)
        self._max_z = max(point1.z, point2.z)

    def contains(self, point):
        return (
            self.min_x <= point.x <= self.max_x
            and self.min_y <= point.y <= self.max_y
            and self.min_z <= point.z <= self.max_z
        )

    def width(self):
        """
        The length of the bounding box in X direction.

        Returns:
            float: Length in X
        """
        return self.max_x - self.min_x

    def depth(self):
        """
        The length of the bounding box in Y direction.

        Returns:
            float: Length in Y
        """
        return self.max_y - self.min_y

    def height(self):
        """
        The length of the bounding box in Z direction.

        Returns:
            float: Length in Z
        """
        return self.max_z - self.min_z

    def __str__(self):
        return "BoundingBox3D({}, {}, {}, {}, {}, {})".format(
            self.min_x, self.min_y, self.min_z, self.max_x, self.max_y, self.max_z
        )

    def __eq__(self, other):
        if not isinstance(other, BoundingBox3):
            return NotImplemented
        return (
            is_close(self.min_x, other.min_x)
            and is_close(self.max_x, other.max_x)
            and is_close(self.min_y, other.min_y)
            and is_close(self.max_y, other.max_y)
            and is_close(self.min_z, other.min_z)
            and is_close(self.max_z, other.max_z)
        )

    def __ne__(self, other):
        # via the == operator, so an unrelated type answers True rather than raising
        return not (self == other)

    def __hash__(self):
        # constant per type - see BoundingBoxBase.__hash__ for why an extent based
        # hash cannot be made to agree with a tolerant __eq__
        return hash(type(self).__name__)
