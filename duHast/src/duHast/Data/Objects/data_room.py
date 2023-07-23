"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Data storage class for Revit room properties.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright © 2023, Jan Christel
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

from duHast.Data.Objects.Properties import data_design_set_option
from duHast.Data.Objects.Properties import data_phasing
from duHast.Data.Objects.Properties import data_level
from duHast.Data.Objects.Properties import data_instance_properties
from duHast.Data.Objects.Properties import data_revit_model
from duHast.Data.Utils import data_base
from duHast.Data.Objects.Properties import data_element_geometry


class DataRoom(data_base.DataBase, data_element_geometry.DataElementGeometryBase):
    data_type = "room"

    def __init__(self, j={}):
        """
        Class constructor.

        :param j: A json formatted dictionary of this class, defaults to {}
        :type j: dict, optional
        """

        # initialise parent classes with values
        super(DataRoom, self).__init__(data_type=DataRoom.data_type, j=j)

        # check if any data was past in with constructor!
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

            if data_instance_properties.DataInstanceProperties.data_type in j:
                self.instance_properties = (
                    data_instance_properties.DataInstanceProperties(
                        j[data_instance_properties.DataInstanceProperties.data_type]
                    )
                )
            else:
                self.instance_properties = (
                    data_instance_properties.DataInstanceProperties()
                )

            if data_design_set_option.DataDesignSetOption.data_type in j:
                self.design_set_and_option = data_design_set_option.DataDesignSetOption(
                    j[data_design_set_option.DataDesignSetOption.data_type]
                )
            else:
                self.design_set_and_option = (
                    data_design_set_option.DataDesignSetOption()
                )

            if "associated_elements" in j:
                self.associated_elements = j["associated_elements"]
            else:
                self.associated_elements = []

            if data_level.DataLevel.data_type in j:
                self.level = data_level.DataLevel(j[data_level.DataLevel.data_type])
            else:
                self.level = data_level.DataLevel()

            if data_revit_model.DataRevitModel.data_type in j:
                self.revit_model = data_revit_model.DataRevitModel(
                    j[data_revit_model.DataRevitModel.data_type]
                )
            else:
                self.revit_model = data_revit_model.DataRevitModel()

            if data_phasing.DataPhasing.data_type in j:
                self.phasing = data_phasing.DataPhasing(
                    j[data_phasing.DataPhasing.data_type]
                )
            else:
                self.phasing = data_phasing.DataPhasing()
        else:
            # initialise classes with default values
            self.associated_elements = []
            self.instance_properties = data_instance_properties.DataInstanceProperties()
            self.level = data_level.DataLevel()
            self.revit_model = data_revit_model.DataRevitModel()
            self.phasing = data_phasing.DataPhasing()
            self.design_set_and_option = data_design_set_option.DataDesignSetOption()
