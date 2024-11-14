"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A 3D vector class.
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

class Vector3(VectorBase):

    def __init__(self, x, y, z):
        """
        A 3D vector class

        :param x: Delta x
        :type x: double
        :param y: Delta y
        :type y: double
        :param z: Delta z
        :type z: double
        """
        super(Vector3, self).__init__(x, y, z)

    @property
    def x(self):
        return self.components[0]

    @property
    def y(self):
        return self.components[1]

    @property
    def z(self):
        return self.components[2]

    def __add__(self, other):
        if not isinstance(other, Vector3):
            raise TypeError("Expected vector3, got: {}".format(type(other).__name__))
        self._check_dimension_compatibility(other)
        return Vector3(*(v + w for v, w in zip(self.components, other.components)))

    def __radd__(self, other):
        if not isinstance(
            other, (list, tuple)
        ):  # Assuming Sequence means list or tuple
            raise TypeError("Expected list or tuple, got: {}".format(type(other).__name__))
        return Vector3(*(w + v for v, w in zip(self.components, other)))

    def __sub__(self, other):
        if not isinstance(other, Vector3):
            return NotImplemented
        self._check_dimension_compatibility(other)
        return Vector3(*(v - w for v, w in zip(self.components, other.components)))

    def __rsub__(self, other):
        if not isinstance(other, (list, tuple)):
            raise TypeError("Expected list or tuple, got: {}".format(type(other).__name__))
        return Vector3(*(w - v for v, w in zip(self.components, other)))

    def __neg__(self):
        return Vector3(*(-v for v in self.components))
    
    def __str__(self):
        return "Vector3D({}, {}, {})".format(self.x, self.y, self.z)

    def __mul__(self, s):
        return Vector3(*(v * s for v in self.components))

    def __truediv__(self, s):
        return Vector3(*(v / s for v in self.components))

    def __floordiv__(self, s):
        return Vector3(*(v // s for v in self.components))
    
    def __str__(self):
        return "Vector3D({}, {}, {})".format(self.x, self.y, self.z)
    
    def __eq__(self, other):
        if not isinstance(other, Vector3):
            raise TypeError("Expected vector3, got: {}".format(type(other).__name__))
        return is_close(self.x, other.x) and is_close(self.y, other.y) and is_close(self.z, other.z)
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __hash__(self):
        return hash((self.x, self.y, self.z))
