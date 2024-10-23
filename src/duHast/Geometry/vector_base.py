"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A vector base class.
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

import math

from duHast.Utilities.Objects import base
from duHast.Geometry.Exceptions.incompatible_vector_dimension import (
    IncompatibleVectorDimensions,
)


class VectorBase(base):
    def __init__(self, *components):
        """
        A vector base class.
        """
        # ini super class to allow multi inheritance in children!
        super(VectorBase, self).__init__()

        self.components = components

    def magnitude(self):
        return math.sqrt(sum(c**2 for c in self.components))

    def _check_dimension_compatibility(self, other):
        if len(self.components) != len(other.components):
            raise IncompatibleVectorDimensions("Vectors are incompatible", other)

    def _check_dimension_compatibility(self, other):
        if len(self.components) != len(other.components):
            raise IncompatibleVectorDimensions(
                "Dimension mismatch: {} vs {}".format(
                    len(self.components), len(other.components)
                ),
                other,
            )

    def __add__(self, other):
        if not isinstance(other, VectorBase):
            raise TypeError("Expected vector, got: {}".format(type(other).__name__))
        self._check_dimension_compatibility(other)
        return VectorBase(*(v + w for v, w in zip(self.components, other.components)))

    def __radd__(self, other):
        if not isinstance(
            other, (list, tuple)
        ):  # Assuming Sequence means list or tuple
            return NotImplemented
        return VectorBase(*(w + v for v, w in zip(self.components, other)))

    def __sub__(self, other):
        if not isinstance(other, VectorBase):
            return NotImplemented
        self._check_dimension_compatibility(other)
        return VectorBase(*(v - w for v, w in zip(self.components, other.components)))

    def __rsub__(self, other):
        if not isinstance(other, (list, tuple)):
            return NotImplemented
        return VectorBase(*(w - v for v, w in zip(self.components, other)))

    def __str__(self):
        return f"Vector({', '.join(map(str, self.components))})"

    def __mul__(self, s):
        return VectorBase(*(v * s for v in self.components))

    def __rmul__(self, s):
        return self.__mul__(s)

    def __truediv__(self, s):
        return VectorBase(*(v / s for v in self.components))

    def __floordiv__(self, s):
        return VectorBase(*(v // s for v in self.components))

    def __neg__(self):
        return self * -1

    def __pos__(self):
        return self

    def __abs__(self):
        return self.magnitude()