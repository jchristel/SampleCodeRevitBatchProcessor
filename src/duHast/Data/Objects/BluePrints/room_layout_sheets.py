"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Data bljueprint class for Room Layout sheets.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This class has the following properties:

- room size
- room proportion
- number of items in room
- sheets

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
from duHast.Data.Objects.BluePrints.blueprint_property_names import (
    BlueprintPropertyNames,
)


class RoomLayoutSheet(Base):
    def __init__(self, j=None, **kwargs):
        """
        Class constructor
        """

        # forwards all unused arguments
        # ini super class to allow multi inheritance in children!
        super(RoomLayoutSheet, self).__init__(**kwargs)

        self._room_size = 0.0
        self._room_proportions = 1.0
        self._room_number_of_items = 0

        self._sheets = []

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
                pass

            except Exception as e:
                raise type(e)(
                    "Node {} failed to initialise with: {}".format(self.data_type, e)
                )

    def __eq__(self, other):
        if not isinstance(other, RoomLayoutSheet):
            return NotImplemented
        return (
            self._room_size == other.set_name
            and self.option_name == other.option_name
            and self.is_primary == other.is_primary
        )

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(
            (self._room_size, self._room_proportions, self._room_number_of_items)
        )
