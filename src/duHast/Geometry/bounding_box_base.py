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
from duHast.Utilities.Objects import base
from duHast.Geometry.geometry_property_names import GeometryPropertyNames
class BoundingBoxBase(base):
    def __init__(self, j=None):


        # ini super class to allow multi inheritance in children!
        super(BoundingBoxBase, self).__init__()

       # Check if a JSON string / dictionary is provided
        if j:
            if isinstance(j, str):
                # Parse the JSON string
                j = json.loads(j)
            elif not isinstance(j, dict):
                raise TypeError("Input must be a JSON string or a dictionary.")
            
            # Validate presence of required keys
            if GeometryPropertyNames.POINT1.value not in j or GeometryPropertyNames.POINT2.value not in j:
                raise ValueError("JSON must contain 'point1' and 'point2' keys.")
            self._json_ini = j
        else:
            self._json_ini = None
            
        self.min_x = float('inf')
        self.max_x = float('-inf')
        self.min_y = float('inf')
        self.max_y = float('-inf')

    @property
    def json_ini(self):
        """Read-only property to access the parsed JSON data."""
        return self._json_ini
    
    def contains(self, point):
        raise NotImplementedError("Subclasses should implement this method")

    def __str__(self):
        return "BoundingBoxBase({}, {}, {}, {})".format(self.min_x, self.min_y, self.max_x, self.max_y)
