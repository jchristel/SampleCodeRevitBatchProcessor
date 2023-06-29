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
# Copyright (c) 2022  Jan Christel
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#

import json
from duHast.Utilities.Objects import base

from duHast.Data.Objects.Properties.Geometry import geometry_polygon
from duHast.Data.Objects.Properties.Geometry import geometry_topo_cell


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
        # check valid j input
        if j != None and len(j) > 0:
            # check type of data that came in:
            if type(j) == str:
                # a string
                j = json.loads(j)
            elif type(j) == dict:
                # no action required
                pass
            else:
                raise ValueError(
                    "Argument supplied must be of type string or type dictionary"
                )

            # check for polygon data
            # this is stored as a list since there could be multiple polygons representing an object
            geometry_data_list = []
            if geometry_polygon.DataPolygon.data_type in j:
                for item in j[geometry_polygon.DataPolygon.data_type]:
                    if "data_type" in item:
                        if item["data_type"]:
                            dummy = geometry_polygon.DataPolygon(item)
                            geometry_data_list.append(dummy)
                    else:
                        print("no data type in item")
            self.polygon = geometry_data_list

            # check for topo cell data
            if geometry_topo_cell.DataTopologyCell.data_type in j:
                self.topologic_cell = geometry_topo_cell.DataTopologyCell(
                    j[geometry_topo_cell.DataTopologyCell.DataType]
                )
            else:
                self.topologic_cell = geometry_topo_cell.DataTopologyCell()

        else:
            # initialise classes with default values
            self.polygon = []
            self.topologic_cell = geometry_topo_cell.DataTopologyCell()
