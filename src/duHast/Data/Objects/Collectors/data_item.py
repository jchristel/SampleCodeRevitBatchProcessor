"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Data storage class for Revit item (furniture, equipment etc.) properties.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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

from duHast.Data.Objects.Collectors.Properties import data_design_set_option
from duHast.Data.Objects.Collectors.Properties import data_phasing
from duHast.Data.Objects.Collectors.Properties import data_level
from duHast.Data.Objects.Collectors.Properties import data_type_properties
from duHast.Data.Objects.Collectors.Properties import data_instance_properties
from duHast.Data.Objects.Collectors.Properties import data_revit_model
from duHast.Data.Objects.Collectors import data_base
from duHast.Data.Objects.Collectors.Properties.Geometry import geometry_base
from duHast.Data.Objects.Collectors.Properties.data_property_names import (
    DataPropertyNames,
)


class DataItem(data_base.DataBase):

    data_type = "item"

    def __init__(self, j=None):
        """
        Class constructor.

        Items represent placed family instances such as furniture and equipment.

        :param j: A json formatted dictionary of this class, defaults to None
        :type j: dict, optional
        """

        # store data type in base class
        super(DataItem, self).__init__(data_type=DataItem.data_type, j=j)

        # set default values
        self.super_component_id = -1
        # list of room element ids this item belongs to (can be more than one when phasing is applied)
        self.rooms = []
        # location in the model: x/y/z position (translation_coord) and facing direction (rotation_coord)
        self.location_point = geometry_base.DataGeometryBase(data_type="location_point")
        self.instance_properties = data_instance_properties.DataInstanceProperties()
        self.type_properties = data_type_properties.DataTypeProperties()
        self.level = data_level.DataLevel()
        self.revit_model = data_revit_model.DataRevitModel()
        self.phasing = data_phasing.DataPhasing()
        self.design_set_and_option = data_design_set_option.DataDesignSetOption()

        json_var = None
        # check if any data was passed in with constructor
        if j is not None:
            # check type of data that came in:
            if isinstance(j, str):
                json_var = json.loads(j)
            elif isinstance(j, dict):
                json_var = j.copy()
            else:
                raise TypeError(
                    "Argument j supplied must be of type string or type dictionary. Got {} instead.".format(
                        type(j)
                    )
                )

            # attempt to populate from json
            try:
                self.super_component_id = json_var.get(
                    DataPropertyNames.SUPER_COMPONENT_ID, -1
                )
                # rooms: list of integer element ids
                self.rooms = json_var.get(DataPropertyNames.ROOMS, [])

                # location point: translation (x/y/z) + rotation
                location_point_data = json_var.get(DataPropertyNames.LOCATION_POINT, None)
                if location_point_data is not None:
                    self.location_point = geometry_base.DataGeometryBase(
                        data_type="location_point", j=location_point_data
                    )

                self.instance_properties = (
                    data_instance_properties.DataInstanceProperties(
                        json_var.get(
                            data_instance_properties.DataInstanceProperties.data_type,
                            {},
                        )
                    )
                )
                self.type_properties = data_type_properties.DataTypeProperties(
                    json_var.get(
                        data_type_properties.DataTypeProperties.data_type, None
                    )
                )
                self.level = data_level.DataLevel(
                    json_var.get(data_level.DataLevel.data_type, None)
                )
                self.revit_model = data_revit_model.DataRevitModel(
                    json_var.get(data_revit_model.DataRevitModel.data_type, None)
                )
                self.phasing = data_phasing.DataPhasing(
                    json_var.get(data_phasing.DataPhasing.data_type, None)
                )
                self.design_set_and_option = data_design_set_option.DataDesignSetOption(
                    json_var.get(
                        data_design_set_option.DataDesignSetOption.data_type, None
                    )
                )

            except Exception as e:
                raise type(e)(
                    "Node {} failed to initialise with: {}".format(self.data_type, e)
                )

    def __eq__(self, other):
        """
        Equal compare (ignores rooms property).

        :param other: Another DataItem instance
        :type other: DataItem

        :return: True if equal, otherwise False
        :rtype: bool
        """

        if not isinstance(other, DataItem):
            return NotImplemented
        return (
            self.location_point == other.location_point
            and self.instance_properties == other.instance_properties
            and self.type_properties == other.type_properties
            and self.level == other.level
            and self.revit_model == other.revit_model
            and self.phasing == other.phasing
            and self.design_set_and_option == other.design_set_and_option
        )

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        """
        Hash (ignores rooms property).

        :return: hash value
        """

        return hash(
            (
                self.location_point,
                self.instance_properties,
                self.type_properties,
                self.level,
                self.revit_model,
                self.phasing,
                self.design_set_and_option,
            )
        )
