"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A 2D vector class.
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

from duHast.Geometry.vector_base import VectorBase
from duHast.Utilities.compare import is_close

class Vector2(VectorBase):
    def __init__(self, x, y):
        """
        A 2D vector class

        :param x: Delta x
        :type x: double
        :param y: Delta y
        :type y: double
        """
        super(Vector2, self).__init__(x, y)

    @property
    def x(self):
        return self.components[0]

    @property
    def y(self):
        return self.components[1]

    def __add__(self, other):
        if not isinstance(other, Vector2):
            raise TypeError("Expected vector, got: {}".format(type(other).__name__))
        self._check_dimension_compatibility(other)
        return Vector2(*(v + w for v, w in zip(self.components, other.components)))

    def __radd__(self, other):
        if not isinstance(
            other, (list, tuple)
        ):  # Assuming Sequence means list or tuple
            raise TypeError("Expected list or tuple, got: {}".format(type(other).__name__))
        return Vector2(*(w + v for v, w in zip(self.components, other)))

    def __sub__(self, other):
        if not isinstance(other, Vector2):
            return NotImplemented
        self._check_dimension_compatibility(other)
        return Vector2(*(v - w for v, w in zip(self.components, other.components)))

    def __rsub__(self, other):
        if not isinstance(other, (list, tuple)):
            raise TypeError("Expected list or tuple, got: {}".format(type(other).__name__))
        return Vector2(*(w - v for v, w in zip(self.components, other)))

    def __neg__(self):
        return Vector2(*(-v for v in self.components))
    
    def __str__(self):
        return "Vector3D({}, {}, {})".format(self.x, self.y, self.z)

    def __mul__(self, s):
        return Vector2(*(v * s for v in self.components))

    def __truediv__(self, s):
        return Vector2(*(v / s for v in self.components))

    def __floordiv__(self, s):
        return Vector2(*(v // s for v in self.components))

    def __str__(self):
        return "Vector2D({}, {})".format(self.x, self.y)

    def __eq__(self, other):
        """
        Compares two 2D vectors using is_close() function.

        """
        if not isinstance(other, Vector2):
            raise TypeError("Expected vector2, got: {}".format(type(other).__name__))
        return is_close(self.x, other.x) and is_close(self.y, other.y)
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __hash__(self):
        return hash((self.x, self.y))