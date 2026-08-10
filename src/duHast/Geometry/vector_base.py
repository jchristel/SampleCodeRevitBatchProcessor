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

from duHast.Utilities.Objects.base import Base
from duHast.Geometry.Exceptions.incompatible_vector_dimension import (
    IncompatibleVectorDimensions,
)
from duHast.Utilities.compare import is_close

class VectorBase(Base):
    def __init__(self, *components):
        """
        A vector base class.
        """
        # ini super class to allow multi inheritance in children!
        super(VectorBase, self).__init__()
        
        # check components are either int ort floats
        for component in components:
            if not isinstance(component, (float, int)):
                raise TypeError(
                    "All components must be of type float or int, got {} instead.".format(type(component).__name__)
                )

        self.components = components

    def _check_dimension_compatibility(self, other):
        if len(self.components) != len(other.components):
            raise IncompatibleVectorDimensions(
                "Dimension mismatch: {} vs {}".format(
                    len(self.components), len(other.components)
                ),
                other,
            )

    def magnitude(self):
        return math.sqrt(sum(c**2 for c in self.components))

    def __str__(self):
        return "Vector ({})".format(", ".join(map(str, self.components)))

    def __rmul__(self, s):
        return self.__mul__(s)

    def __neg__(self):
        # Raise a NotImplementedError to force child classes to implement their own
        raise NotImplementedError("Negation is not implemented in VectorBase; child classes must provide their own implementation.")

    def __pos__(self):
        return self

    def __abs__(self):
        return self.magnitude()

    def __eq__(self, other):
        if not isinstance(other, VectorBase):
            return NotImplemented
        # a 2D and a 3D vector are not equal, which is an ANSWER rather than an error.
        # _check_dimension_compatibility raises, which is right for arithmetic - there
        # is no sensible sum of a 2D and a 3D vector - but asking whether two objects
        # are equal must never blow up.
        if len(self.components) != len(other.components):
            return False
        return all(is_close(a, b) for a, b in zip(self.components, other.components))

    def __ne__(self, other):
        # via the == operator rather than __eq__ directly: calling __eq__ by hand
        # returns NotImplemented for an unrelated type, and negating that raises.
        return not (self == other)

    def __hash__(self):
        # constant per type. __eq__ compares with a tolerance, so equal vectors can
        # hold differing components, and any hash built from those components lets a
        # set keep two entries which compare equal. Under a relative tolerance no
        # component based hash can avoid that, so none is used.
        return hash(type(self).__name__)