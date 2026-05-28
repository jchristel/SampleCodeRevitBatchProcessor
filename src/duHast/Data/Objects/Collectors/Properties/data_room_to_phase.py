"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Data storage class associating a room element id with the phase it was observed in.
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

from duHast.Data.Objects.Collectors import data_base
from duHast.Data.Objects.Collectors.Properties.data_property_names import (
    DataPropertyNames,
)


class DataRoomToPhase(data_base.DataBase):

    data_type = "room_to_phase"

    def __init__(self, j=None):
        """
        Class constructor.

        Stores a single room-to-phase pairing: the element id of a room and the
        element id of the phase in which that room assignment was observed.

        :param j: A json formatted dictionary of this class, defaults to None
        :type j: dict, optional
        """

        super(DataRoomToPhase, self).__init__(DataRoomToPhase.data_type)

        # set default values  (-1 == not set)
        self.phase_id = -1
        self.room_id = -1

        json_var = None
        if j is not None:
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

            try:
                self.phase_id = json_var.get(DataPropertyNames.PHASE_ID, self.phase_id)
                if not isinstance(self.phase_id, int):
                    raise TypeError(
                        "phase_id needs to be of type int, got {} instead.".format(
                            type(self.phase_id)
                        )
                    )

                self.room_id = json_var.get(DataPropertyNames.ROOM_ID, self.room_id)
                if not isinstance(self.room_id, int):
                    raise TypeError(
                        "room_id needs to be of type int, got {} instead.".format(
                            type(self.room_id)
                        )
                    )

            except Exception as e:
                raise type(e)(
                    "Node {} failed to initialise with: {}".format(self.data_type, e)
                )

    def __eq__(self, other):
        if not isinstance(other, DataRoomToPhase):
            raise ValueError(
                "other needs to be of type DataRoomToPhase, got {} instead.".format(
                    type(other)
                )
            )
        return self.phase_id == other.phase_id and self.room_id == other.room_id

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.phase_id, self.room_id))
