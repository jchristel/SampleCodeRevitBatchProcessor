"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A 3D point class.
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

from duHast.Geometry.point_base import PointBase
from duHast.Geometry.geometry_property_names import GeometryPropertyNames
from duHast.Utilities.compare import is_close

class Point3(PointBase):
    def __init__(self, x=None, y=None, z=None, j=None):
        """
        A #D point class.

        :param x: x-coordinate of point
        :type x: double
        :param y: y-coordinate of point
        :type y: double
        :param z: z-coordinate of point
        :type z: double
        """

        # ini super class to allow multi inheritance in children!
        super(Point3, self).__init__(x=x, y=y, j=j)

        # check first if a json string / dictionary is provided
        if j:
            # Validate presence of required keys (stored in base class json)
            if GeometryPropertyNames.Z not in self.json_ini:
                raise ValueError("JSON must contain 'z' key.")

            z = self.json_ini.get(GeometryPropertyNames.Z)

        # Type checking
        if not isinstance(z, float):
            raise TypeError("z expected float. Got {} instead.".format(type(z)))

        # store values
        self.z = z
    
    def __eq__(self, other):
        if not isinstance(other,Point3):
            return NotImplemented
        return is_close(self.x, other.x) and is_close(self.y, other.y)and is_close(self.z, other.z)
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __hash__(self):
        return hash((self.x, self.y, self.z))
