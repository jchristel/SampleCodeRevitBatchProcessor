"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Data storage base class used for geometry aspects of Revit elements.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- contains 

    - polygon

"""

#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2023, Jan Christel
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

from duHast.Data.Objects.Collectors.Properties.Geometry import geometry_polygon_2

from duHast.Data.Objects.Collectors.Properties.data_property_names import DataPropertyNames


class DataElementGeometryBase(base.Base):
    data_type = "element geometry base"

    def __init__(self, j, **kwargs):
        """
        Class constructor

        :param j: Json formatted string or dictionary
        :type j: str or dic

        :raises ValueError: 'Argument supplied must be of type string or type dictionary'
        """

        # ini super class to allow multi inheritance in children!
        # forwards all unused arguments
        super(DataElementGeometryBase, self).__init__(**kwargs)

        # set default values
        self.polygon = geometry_polygon_2.DataGeometryPolygon2()

        json_var = None
        # check valid j input
        if j is not None:
            # check type of data that came in:
            if isinstance(j, str):
                # a string
                json_var = json.loads(j)
            elif isinstance(j, dict):
                # no action required
                json_var = j.copy()
            else:
                raise TypeError(
                    "Argument j supplied must be of type string or type dictionary. Got {} instead.".format(
                        type(j)
                    )
                )

            # attempt to populate from json
            try:
                # check for polygon data
                polygon_data = json_var.get(DataPropertyNames.POLYGON, None)
                self.polygon = geometry_polygon_2.DataGeometryPolygon2(j=polygon_data)
            except Exception as e:
                raise type(e)(
                    "Node {} failed to initialise with: {}".format(self.data_type, e)
                )

    def __eq__(self, other):
        if not isinstance(other, DataElementGeometryBase):
            return NotImplemented
        return self.polygon == other.polygon

    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __hash__(self):
        return hash(self.polygon)
