"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Data storage class for Revit ceiling properties.
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

# from duHast.DataSamples import DataGeometry
from duHast.Data.Objects.Properties import data_design_set_option
from duHast.Data.Objects.Properties import data_phasing
from duHast.Data.Objects.Properties import data_level
from duHast.Data.Objects.Properties import data_type_properties
from duHast.Data.Objects.Properties import data_instance_properties
from duHast.Data.Objects.Properties import data_revit_model
from duHast.Data.Utils import data_base
from duHast.Data.Objects.Properties import data_element_geometry


class DataCeiling(data_base.DataBase, data_element_geometry.DataElementGeometryBase):

    data_type = "ceiling"

    def __init__(self, j=None):
        """
        Class constructor.

        :param j: A json formatted dictionary of this class, defaults to {}
        :type j: dict, optional
        """

        # store data type  in base class
        super(DataCeiling, self).__init__(data_type=DataCeiling.data_type, j=j)

        # set default values
        self.associated_elements = []
        self.instance_properties = data_instance_properties.DataInstanceProperties()
        self.type_properties = data_type_properties.DataTypeProperties()
        self.level = data_level.DataLevel()
        self.revit_model = data_revit_model.DataRevitModel()
        self.phasing = data_phasing.DataPhasing()
        self.design_set_and_option = data_design_set_option.DataDesignSetOption()

        # check if any data was past in with constructor!
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
                self.instance_properties = (
                    data_instance_properties.DataInstanceProperties(
                        j.get(
                            data_instance_properties.DataInstanceProperties.data_type,
                            {},
                        )
                    )
                )
                self.type_properties = data_type_properties.DataTypeProperties(
                    j.get(data_type_properties.DataTypeProperties.data_type, {})
                )
                self.level = data_level.DataLevel(
                    j.get(data_level.DataLevel.data_type, {})
                )
                self.revit_model = data_revit_model.DataRevitModel(
                    j.get(data_revit_model.DataRevitModel.data_type, {})
                )
                self.phasing = data_phasing.DataPhasing(
                    j.get(data_phasing.DataPhasing.data_type, {})
                )
                self.design_set_and_option = data_design_set_option.DataDesignSetOption(
                    j.get(data_design_set_option.DataDesignSetOption.data_type, {})
                )
                self.associated_elements = j.get(
                    "associated_elements", self.associated_elements
                )
            except Exception as e:
                raise ValueError(
                    "Node {} failed to initialise with: {}".format(self.data_type, e)
                )
