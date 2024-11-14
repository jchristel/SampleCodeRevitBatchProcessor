"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Data storage class for Revit element type properties.
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
from duHast.Data.Objects.Collectors import data_base
from duHast.Data.Objects.Collectors.Properties.data_property_names import DataPropertyNames
from duHast.Data.Objects.Collectors.Properties.data_property import DataProperty


class DataTypeProperties(data_base.DataBase):

    data_type = "type_properties"

    def __init__(self, j=None):
        """
        Class constructor

        :param j:  json formatted dictionary of this class, defaults to {}
        :type j: dict, optional
        """

        # store data type  in base class
        super(DataTypeProperties, self).__init__(DataTypeProperties.data_type)

        # set default values
        self.name = "-"
        self.id = -1
        self.properties = []

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
                self.name = json_var.get(DataPropertyNames.NAME, self.name)
                if not (isinstance(self.name, str)):
                    raise ValueError(
                        "name needs to be of type str, got {} instead.".format(
                            type(self.name)
                        )
                    )

                self.id = json_var.get(DataPropertyNames.ID, self.id)
                if not (isinstance(self.id, int)):
                    raise ValueError(
                        "id needs to be of type int, got {} instead.".format(
                            type(self.id)
                        )
                    )

                # needs to be converted to list of property objects!
                properties = json_var.get(DataPropertyNames.PROPERTIES, self.properties)
                for prop in properties:
                    self.properties.append(DataProperty(j=prop))

            except Exception as e:
                raise type(e)(
                    "Node {} failed to initialise with: {}".format(self.data_type, e)
                )

    def __eq__(self, other):
        if not isinstance(other, DataTypeProperties):
            return NotImplemented

        if not (self.name == other.name and self.id == other.id):
            return False

        # Check if properties lists are the same length
        if len(self.properties) != len(other.properties):
            return False

        # Check each property in the properties list regardless of order!
        return set(self.properties) == set(other.properties)

    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __hash__(self):
        return hash((self.name, self.id, self.properties))
