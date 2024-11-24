"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Data sheet size class.
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
from duHast.Utilities.Objects.base import Base
from duHast.Data.Objects.Collectors.Properties.data_property_names import (
    DataPropertyNames,
)


class DataSheetSize(Base):
    data_type = "sheet_size"

    def __init__(self, name=None, width=0.0, height=0.0, j=None,**kwargs):
        """
        Class constructor

        :param j:  json formatted dictionary of this class, defaults to {}
        :type j: dict, optional
        """

        # store data type  in base class
        super(DataSheetSize, self).__init__(**kwargs)

        json_var = None
        # check if any json data was past in with constructor!
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
                self.name = json_var.get(DataPropertyNames.NAME, None)
                if not (isinstance(self.name, str)):
                    raise ValueError(
                        "name needs to be of type str, got {} instead.".format(
                            type(self.name)
                        )
                    )

                self.width = json_var.get(DataPropertyNames.WIDTH, 0.0)
                if not (isinstance(self.width, float)):
                    raise ValueError(
                        "width needs to be of type float, got {} instead.".format(
                            type(self.name)
                        )
                    )

                self.height = json_var.get(DataPropertyNames.HEIGHT, 0.0)
                if not (isinstance(self.height, float)):
                    raise ValueError(
                        "height needs to be of type float, got {} instead.".format(
                            type(self.name)
                        )
                    )
            except Exception as e:
                raise type(e)(
                    "Node {} failed to initialise with: {}".format(self.data_type, e)
                )
        else:
            # set default values as past in only if there is no json
            self.name = name
            if not (isinstance(self.name, str)):
                raise ValueError(
                    "name needs to be of type str, got {} instead.".format(type(self.name))
                )
            

            self.width = width
            if not (isinstance(self.width, float)):
                raise ValueError(
                    "width needs to be of type float, got {} instead.".format(
                        type(self.name)
                    )
                )
            self.height = height
            if not (isinstance(self.height, float)):
                raise ValueError(
                    "height needs to be of type float, got {} instead.".format(
                        type(self.name)
                    )
                )

    def is_matching_size(self, width, height):
        """
        Check if supplied values are within a 20mm band of the actual paper size

        Args:
            width (_type_): _description_
            height (_type_): _description_

        Returns:
            _type_: _description_
        """
        # check if the past in values are within 10mm band of the sheet size

        if (
            width
            <= self.width
            + 10  # supplied width can be a max of 10 mm larger than the paper format
            and width
            >= self.width
            - 10  # supplied width can be a max of 10 mm smaller than the paper format
            and height
            <= self.height
            + 10  # supplied height can be a max of 10 mm larger than the paper format
            and height
            >= self.height
            - 10  # supplied height can be a max of 10 mm smaller than the paper format
        ):
            return True
        else:
            return False

    def __eq__(self, other):
        if not isinstance(other, DataSheetSize):
            return NotImplemented

        return (
            self.name == other.name
            and self.width == other.width
            and self.height == other.height
        )

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.name, self.width, self.height))
