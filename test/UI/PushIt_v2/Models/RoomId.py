# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2025, Jan Christel
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

from duHast.Utilities.Objects.base import Base


class RoomID(Base):

    def __init__(
        self,
        id,
        parameter_guid,
    ):
        """
        Initializes a new instance of the RoomID class.

        :param id: The id of the room
        :type id: RoomId
        :param parameter_guid: The parameter guid in which the id is to be stored.
        :type parameter_guid: str
        """

        super(RoomID, self).__init__()

        if isinstance(id, str) == False:
            raise TypeError(
                "id needs to be of type str, got {} instead.".format(type(id))
            )
        # The id of the room
        self.id = id

        if isinstance(parameter_guid, str) == False:
            raise TypeError(
                "parameter_guid needs to be of type str. Got {} instead.".format(id)
            )
        # The parameter guid in which the id is to be stored
        self.parameter_guid = parameter_guid

    def __eq__(self, other):
        """
        Custom compare is equal override

        :param other: Another instance of  ID class
        :type other: :class:`.FamilyId`

        :return: True if name value of other colour class instance equal the name values of this instance, otherwise False.
        :rtype: Bool
        """

        if isinstance(other, RoomID) == False:
            return False

        if other.id == self.id and other.parameter_guid == self.parameter_guid:
            return True
        else:
            return False

    # python 2.7 needs custom implementation of not equal
    def __ne__(self, other):
        return not self.__eq__(other=other)

    def __hash__(self):
        """
        Custom hash override

        Required due to custom __eq__ override present in this class
        """
        try:
            return hash(self.__class__)
        except Exception as e:
            raise ValueError("Exception {} occurred.".format(e))
