"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A bounding box base class.
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

import json
from duHast.Utilities.Objects.base import Base
from duHast.Geometry.geometry_property_names import GeometryPropertyNames
from duHast.Utilities.compare import is_close

#: A length at or below this counts as zero. Absolute, in the units of the box, since
#: a relative comparison never reports a very small number as close to zero.
ZERO_LENGTH_TOLERANCE = 1e-9


class BoundingBoxBase(Base):
    def __init__(self, j=None, **kwargs):
        """
        Base implementation of a bounding box.

        :raises TypeError: "Input must be a JSON string or a dictionary."
        :raises ValueError: "JSON must contain 'point1' and 'point2' keys."
        """
        # ini super class to allow multi inheritance in children!
        super(BoundingBoxBase, self).__init__(**kwargs)

        json_string=None
        # Check if a JSON string / dictionary is provided.
        # Tested against None rather than for truthiness: an EMPTY dictionary is json
        # which is missing its keys, not json which was never supplied, and it needs to
        # reach the check below and be reported as such rather than quietly leaving a
        # zero sized box behind.
        if j is not None:
            if isinstance(j, str):
                # Parse the JSON string
                json_string = json.loads(j)
            elif isinstance(j, dict):
                # make a copy
                json_string=j.copy()
            elif not isinstance(j, dict):
                raise TypeError("Input must be a JSON string or a dictionary.")

            # Validate presence of required keys
            if (
                GeometryPropertyNames.MAX_X not in json_string
                or GeometryPropertyNames.MAX_Y not in json_string
                or GeometryPropertyNames.MIN_X not in json_string
                or GeometryPropertyNames.MIN_Y not in json_string
            ):
                raise ValueError("JSON must contain 'max_x', 'max_y', 'min_x', 'min_y' keys.")
            self._json_ini = json_string
        else:
            self._json_ini = None

        # set default values
        self._min_x = 0.0
        self._max_x = 0.0
        self._min_y = 0.0
        self._max_y = 0.0

    @property
    def json_ini(self):
        """Read-only property to access the parsed JSON data."""
        return self._json_ini

    @property
    def min_x(self):
        """Read-only property for minimum x value."""
        return self._min_x

    @property
    def max_x(self):
        """Read-only property for maximum x value."""
        return self._max_x

    @property
    def min_y(self):
        """Read-only property for minimum y value."""
        return self._min_y

    @property
    def max_y(self):
        """Read-only property for maximum y value."""
        return self._max_y

    def contains(self, point):
        raise NotImplementedError("Subclasses should implement this method")

    def width(self):
        raise NotImplementedError("Subclasses should implement this method")

    def depth(self):
        raise NotImplementedError("Subclasses should implement this method")
    
    def ratio(self):
        """
        The length ratio of the bounding box edges, dividing the length in X by the
        length in Y.

        Implemented here rather than per subclass, since it is the same calculation for
        a 2D and a 3D box and only needs width() and depth() which the subclasses
        provide. BoundingBox3 previously had no ratio at all and inherited a
        NotImplementedError, while BoundingBox2 carried its own copy.

        :raises ValueError: If the depth is zero, which would be a division by zero.

        :return: Edge ratio.
        :rtype: float
        """

        depth = self.depth()
        # an ABSOLUTE tolerance is required here. is_close on its own compares
        # relatively, so a depth of 1e-18 is not "close to" 0.0 by that measure and an
        # exact != 0.0 test let it through to produce an enormous ratio.
        if is_close(depth, 0.0, abs_tol=ZERO_LENGTH_TOLERANCE):
            raise ValueError(
                "Can not calculate ratio since depth is {} and division by 0.0 is not allowed.".format(
                    depth
                )
            )
        return self.width() / depth


    def __str__(self):
        return "BoundingBoxBase({}, {}, {}, {})".format(
            self.min_x, self.min_y, self.max_x, self.max_y
        )

    def __eq__(self, other):
        if not isinstance(other, BoundingBoxBase):
            return NotImplemented
        return (is_close(self.min_x, other.min_x) and
                is_close(self.max_x, other.max_x) and
                is_close(self.min_y, other.min_y) and
                is_close(self.max_y, other.max_y))

    def __ne__(self, other):
        # via the == operator rather than __eq__ directly: calling __eq__ by hand
        # returns NotImplemented for an unrelated type, and negating that raises.
        return not (self == other)

    def __hash__(self):
        # constant per type. __eq__ compares with a tolerance, so two boxes can be
        # equal while their extents differ, and a hash built from those extents lets a
        # set keep two entries which compare equal to each other. Under a relative
        # tolerance no extent based hash can avoid that, so none is used.
        return hash(type(self).__name__)