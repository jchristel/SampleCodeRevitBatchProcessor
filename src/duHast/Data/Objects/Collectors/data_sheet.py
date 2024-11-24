"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Data storage base class used for Revit sheets.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- contains 

    - the title block
    - a list of view ports
    - a list of all sheet properties (instance and type)

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

from duHast.Data.Objects.Collectors import data_base
from duHast.Data.Objects.Collectors.Properties import data_type_properties
from duHast.Data.Objects.Collectors.Properties import data_instance_properties
from duHast.Data.Objects.Collectors.Properties.Geometry.geometry_bounding_box_2 import (
    DataGeometryBoundingBox2,
)
from duHast.Data.Objects.Collectors.data_sheet_view_port import DataSheetViewPort
from duHast.Data.Objects.Collectors.Properties.data_property_names import (
    DataPropertyNames,
)


class DataSheet(data_base.DataBase):

    data_type = "sheet"

    def __init__(self, j=None):
        """
        Class constructor.

        :param j: A json formatted dictionary of this class, defaults to {}
        :type j: dict, optional
        """

        # initialise parent classes with values
        super(DataSheet, self).__init__(data_type=DataSheet.data_type)

        # set default values
        self.instance_properties = data_instance_properties.DataInstanceProperties()
        self.type_properties = data_type_properties.DataTypeProperties()
        self.view_ports = []
        self.bounding_box = DataGeometryBoundingBox2()
        self.sheet_size = None

        json_var = None
        # check if any data was past in with constructor!
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
                self.instance_properties = (
                    data_instance_properties.DataInstanceProperties(
                        json_var.get(
                            data_instance_properties.DataInstanceProperties.data_type,
                            None,
                        )
                    )
                )
                self.type_properties = data_type_properties.DataTypeProperties(
                    json_var.get(
                        data_type_properties.DataTypeProperties.data_type, None
                    )
                )
                self.bounding_box = DataGeometryBoundingBox2(
                    json_var.get(DataPropertyNames.BOUNDING_BOX, None)
                )

                # get sheet view port data
                view_port_data = json_var.get(DataPropertyNames.VIEW_PORTS, None)
                if view_port_data:
                    for vp in view_port_data:
                        self.view_ports.append(DataSheetViewPort(j=vp))

                # get sheet size data
                self.sheet_size = json_var.get(DataPropertyNames.SHEET_SIZE, None)
                if self.sheet_size is not None and not isinstance(self.sheet_size, str):
                    raise ValueError(
                        "sheet size needs to be of type str or None, got {} instead.".format(
                            type(self.name)
                        )
                    )

            except Exception as e:
                raise type(e)(
                    "Node {} failed to initialise with: {}".format(self.data_type, e)
                )

    def __eq__(self, other):
        """
        equal compare

        Args:
            other (DataSheet): another DataSheet instance

        Returns:
            bool: True if equal, otherwise False
        """
        if not isinstance(other, DataSheet):
            return NotImplemented
        return (
            self.instance_properties == other.instance_properties
            and self.type_properties == other.type_properties
            and self.view_ports == other.view_ports
            and self.bounding_box == other.bounding_box
            and self.sheet_size == other.sheet_size
        )

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(
            (
                self.instance_properties,
                self.type_properties,
                self.view_ports,
                self.bounding_box,
                self.sheet_size,
            )
        )
