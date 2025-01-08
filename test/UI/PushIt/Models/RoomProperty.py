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


class RoomProperty(Base):

    def __init__(self, name, value, parameter_guid, unit_converter=None):
        """
        Initializes a new instance of the RoomProperty class.

        :param name: The name of the property
        :type name: str
        :param value: The value of the property
        :type value: str
        :param parameter_guid: The parameter guid in which the property is to be stored.
        :type parameter_guid: str
        :param unit_converter: The unit converter to be used when pushing data to revit.
        :type unit_converter: func, optional
        """

        super(RoomProperty, self).__init__()

        if isinstance(name, str) == False:
            raise TypeError(
                "name needs to be of type str, got {} instead.".format(type(id))
            )

        self.name = name

        if isinstance(value, str) == False:
            raise TypeError("value needs to be of type str. Got {} instead.".format(id))
        self.value = value

        if isinstance(parameter_guid, str) == False:
            raise TypeError(
                "parameter_guid needs to be of type str. Got {} instead.".format(id)
            )
        self.parameter_guid = parameter_guid

        # unit converter used when pushing data to revit (some data is read as string but needs to be float in revit)
        self.unit_converter = unit_converter

    def __eq__(self, other):
        """
        Custom compare is equal override

        :param other: Another instance of  RoomProperty class
        :type other: :class:`.RoomProperty`
        
        :return: True if name value of other colour class instance equal the name values of this instance, otherwise False.
        :rtype: Bool
        """

        if isinstance(other, RoomProperty) == False:
            return False

        if (
            other.name == self.name
            and other.value == self.value
            and other.parameter_guid == self.parameter_guid
        ):
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
