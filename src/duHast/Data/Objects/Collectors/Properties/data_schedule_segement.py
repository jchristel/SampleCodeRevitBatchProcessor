"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Data storage class for Revit schedule segement properties.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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
from duHast.Data.Objects.Collectors.data_base import DataBase
from duHast.Data.Objects.Collectors.Properties.data_property_names import DataPropertyNames


class DataScheduleSegment(DataBase):

    data_type = "schedule segment"

    def __init__(self, j=None):
        """
        Class constructor

        :param j:  json formatted dictionary of this class, defaults to {}
        :type j: dict, optional
        """

        # store data type  in base class
        super(DataScheduleSegment, self).__init__(
            data_type=DataScheduleSegment.data_type
        )

        # set default values
        self.index = 0
        self.height = 0.0

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
                self.index = json_var.get(DataPropertyNames.INDEX, self.index)
                if not (isinstance(self.index, int)):
                    raise ValueError(
                        "index needs to be of type int, got {} instead.".format(
                            type(self.index)
                        )
                    )

                self.height = json_var.get(DataPropertyNames.HEIGHT, self.height)
                if not (isinstance(self.height, float)):
                    raise ValueError(
                        "height needs to be of type float, got {} instead.".format(
                            type(self.index)
                        )
                    )
            except Exception as e:
                raise type(e)(
                    "Node {} failed to initialise with: {}".format(self.data_type, e)
                )

    def __eq__(self, other):
        if not isinstance(other, DataScheduleSegment):
            return NotImplemented
        return self.index == other.index and self.height == other.height

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.index, self.height))