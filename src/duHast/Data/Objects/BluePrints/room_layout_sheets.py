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
        
        # check if any data was past in with constructor!
        if j is not None:
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
                self.set_name = j.get(DataPropertyNames.SET_NAME.value, self.set_name)
                if not isinstance(self.set_name, str):
                    raise TypeError(
                        "Expected 'set_name' to be a string, got {}".format(
                            type(self.set_name)
                        )
                    )

                self.option_name = j.get(
                    DataPropertyNames.OPTION_NAME.value, self.option_name
                )
                if not isinstance(self.option_name, str):
                    raise TypeError(
                        "Expected 'option_name' to be a string, got {}".format(
                            type(self.option_name)
                        )
                    )

                self.is_primary = j.get(
                    DataPropertyNames.IS_PRIMARY.value, self.is_primary
                )
                if not isinstance(self.is_primary, bool):
                    raise TypeError(
                        "Expected 'is_primary' to be a boolean, got {}".format(
                            type(self.is_primary)
                        )
                    )

            except Exception as e:
                raise type(e)(
                    "Node {} failed to initialise with: {}".format(self.data_type, e)
                )

    def __eq__(self, other):
        if not isinstance(other, DataDesignSetOption):
            return NotImplemented
        return (
            self.set_name == other.set_name
            and self.option_name == other.option_name
            and self.is_primary == other.is_primary
        )

    def __ne__(self, other):
        return not self.__eq__(other)
        
        