"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A point base class.
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
from duHast.Utilities.Objects import base
from duHast.Geometry.geometry_property_names import GeometryPropertyNames
from duHast.Utilities.compare import is_close

class PointBase(base.Base):
    def __init__(self, x=None, y=None, j=None):
        """
        A point base class. Should not be used directly.

        :param x: x-coordinate of point
        :type x: double
        :param y: y-coordinate of point
        :type y: double
        """

        # ini super class to allow multi inheritance in children!
        super(PointBase, self).__init__()

        # Check if a JSON string / dictionary is provided
        if j:
            if isinstance(j, str):
                # Parse the JSON string
                j = json.loads(j)
            elif not isinstance(j, dict):
                raise TypeError("Input must be a JSON string or a dictionary.")

            # Validate presence of required keys
            if (
                GeometryPropertyNames.X not in j
                or GeometryPropertyNames.Y not in j
            ):
                raise ValueError("JSON must contain 'x' and 'y' keys.")

            x = j.get(GeometryPropertyNames.X)
            y = j.get(GeometryPropertyNames.Y)

            self._json_ini = j
        else:
            self._json_ini = None

        # Type checking
        if not isinstance(x, float):
            raise TypeError("x expected float. Got {} instead.".format(type(x)))
        if not isinstance(y, float):
            raise TypeError("y expected float. Got {} instead.".format(type(y)))

        # store values
        self.x = x
        self.y = y

    @property
    def json_ini(self):
        """Read-only property to access the parsed JSON data."""
        return self._json_ini

    def __eq__(self, other):
        if not isinstance(other,PointBase):
            return NotImplemented
        return is_close(self.x, other.x) and is_close(self.y, other.y)
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __hash__(self):
        return hash((self.x, self.y))