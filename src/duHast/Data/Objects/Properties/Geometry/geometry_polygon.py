"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Polygon geometry data storage class.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A polygon consists, as a minimym, of an outer loop, but may also have any number of inner loops. Those inner loops describe holes in the surface the outer loop decribes.

Loops are made up of a numer of 2D points.


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
from duHast.Data.Objects.Properties.Geometry import geometry_base
from duHast.Data.Objects.Properties.data_property_names import DataPropertyNames
from duHast.Geometry.point_2 import Point2


class DataPolygon(geometry_base.DataGeometryBase):
    data_type = "polygon"

    def __init__(self, j=None):
        """
        Class constructor for a 2d polygon.

        :param j:  json formatted dictionary of this class, defaults to {}
        :type j: dict, optional
        """

        # store data type  in base class and pass on json string!!!
        super(DataPolygon, self).__init__(DataPolygon.data_type, j)

        # set default values
        self.outer_loop = []
        self.inner_loops = []

        # check if any data was past in with constructor!
        if j is not None:
            # check type of data that came in:
            if isinstance(j, str):
                # a string
                j = json.loads(j)
            elif isinstance(j, dict):
                # no action required
                pass
            else:
                raise TypeError(
                    "Argument j supplied must be of type string or type dictionary. Got {} instead.".format(
                        type(j)
                    )
                )

            # attempt to populate from json
            try:
                # get outer points loop
                outer_loop = j.get(DataPropertyNames.OUTER_LOOP.value, [])
                if len(outer_loop) > 0:
                    for p in outer_loop:
                        self.outer_loop.append(Point2(j=p))
                else:
                    # a polygon must contain at least an outer loop...
                    raise ValueError("Json did not contain any outer loop data")

                # get inner loops
                inner_loops = j.get(DataPropertyNames.INNER_LOOPS.value, [])
                if len(inner_loops) > 0:
                    for loop in inner_loops:
                        loop_points = []
                        for p in loop:
                            loop_points.append(Point2(j=p))
                        self.inner_loops.append(loop_points)

            except Exception as e:
                raise type(e)(
                    "Node {} failed to initialise with: {}".format(self.data_type, e)
                ) from e
