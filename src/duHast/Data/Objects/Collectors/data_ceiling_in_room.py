"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Data storage class pairing a ceiling with its intersection area inside a room.
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

from duHast.Data.Objects.Collectors.data_ceiling import DataCeiling
from duHast.Data.Objects.Collectors.Properties.data_property_names import (
    DataPropertyNames,
)
from duHast.Utilities.Objects.base import Base


class DataCeilingInRoom(Base):
    """
    Pairs a :class:`.DataCeiling` instance with the area (mm²) of the polygon
    intersection between that ceiling and a specific room.

    One instance is created per ceiling-room intersection and stored in
    :attr:`.DataRoom.ceilings`.

    :param area: Intersection area in mm².
    :type area: float
    :param ceiling: The ceiling data object.
    :type ceiling: :class:`.DataCeiling`
    """

    data_type = "ceiling_in_room"

    def __init__(self, j=None):
        """
        Class constructor.

        :param j: A json formatted string or dictionary of this class, defaults to None
        :type j: str or dict, optional

        :raises TypeError: If j is neither a string nor a dictionary.
        """

        super(DataCeilingInRoom, self).__init__()

        # set default values
        #: Intersection area between the ceiling and the room polygon, in mm².
        self.area = 0.0
        #: The :class:`.DataCeiling` instance associated with this entry.
        self.ceiling = None

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
                area = json_var.get(DataPropertyNames.AREA, self.area)
                if not isinstance(area, (float, int)):
                    raise TypeError(
                        "Expected 'area' to be a number, got {}".format(type(area))
                    )
                # json holds a whole number as an int, and this is always a float
                self.area = float(area)

                # the ceiling is optional: an entry can be stored with the area alone
                ceiling = json_var.get(DataPropertyNames.CEILING, None)
                if ceiling is not None:
                    self.ceiling = DataCeiling(j=ceiling)

            except Exception as e:
                raise type(e)(
                    "Node {} failed to initialise with: {}".format(self.data_type, e)
                )
