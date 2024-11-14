"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Data storage class for Revit project level properties.
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
from duHast.Data.Objects.Collectors.Properties.data_level_base import DataLevelBase
from duHast.Data.Objects.Collectors.Properties.data_property_names import DataPropertyNames
from duHast.Data.Objects.Collectors.Properties import data_revit_model


class DataLevelBuilding(DataLevelBase):

    data_type = "building level"

    def __init__(self, j=None):
        """
        Class constructor

        :param j:  json formatted dictionary of this class, defaults to {}
        :type j: dict, optional
        """

        # store data type  in base class
        super(DataLevelBuilding, self).__init__(j=j)

        # set default values
        self.elevation = 0.0
        self.revit_model = data_revit_model.DataRevitModel()

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
                self.elevation = json_var.get(
                    DataPropertyNames.ELEVATION, self.elevation
                )

                if not (isinstance(self.elevation, float)):
                    raise TypeError(
                        "Expected 'elevation' to be a float, got {}".format(
                            type(self.elevation)
                        )
                    )

                self.revit_model = data_revit_model.DataRevitModel(
                    json_var.get(data_revit_model.DataRevitModel.data_type, None)
                )

            except Exception as e:
                raise type(e)(
                    "Node {} failed to initialise with: {}".format(self.data_type, e)
                )

    def __eq__(self, other):
        if not isinstance(other, DataLevelBuilding):
            return NotImplemented
        return (
            self.elevation == other.elevation and self.revit_model == other.revit_model
        )

    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __hash__(self):
        return hash((self.elevation, self.revit_model))
