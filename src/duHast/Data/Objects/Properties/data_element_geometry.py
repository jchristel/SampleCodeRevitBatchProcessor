"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Data storage base class used for geometry aspects of Revit elements.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- contains 

    - polygon
    - topology cell (WIP)

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

from duHast.Data.Objects.Properties.Geometry import geometry_polygon
from duHast.Data.Objects.Properties.Geometry import geometry_topo_cell

from duHast.Data.Objects.Properties.data_property_names import DataPropertyNames

class DataElementGeometryBase(base.Base):
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
        self.polygon = []
        self.topologic_cell = geometry_topo_cell.DataTopologyCell()

        # check valid j input
        if j != None and len(j) > 0:
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
                # check for polygon data
                polygon_data = j.get(geometry_polygon.DataPolygon.data_type, [])

                # this is stored as a list since there could be multiple polygons representing an object
                geometry_data_list = []
                for item in polygon_data:
                    if DataPropertyNames.DATA_TYPE in item:
                        if item[DataPropertyNames.DATA_TYPE]:
                            dummy = geometry_polygon.DataPolygon(item)
                            geometry_data_list.append(dummy)

                self.polygon = geometry_data_list

                self.topologic_cell = geometry_topo_cell.DataTopologyCell(
                    j.get(geometry_topo_cell.DataTopologyCell.data_type, {})
                )

            except Exception as e:
                raise ValueError(
                    "Node {} failed to initialise with: {}".format(self.data_type, e)
                )
