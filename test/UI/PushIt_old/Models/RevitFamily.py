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

"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A class to store revit family information in.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

from duHast.Utilities.Objects.base import Base


class RFamily(Base):

    def __init__(
        self,
        room_id,
        area_designed,
        area_briefed,
        properties,
        design_set,
        design_option,
        design_option_is_primary,
        revit_element_id,
    ):
        """
        Initializes a new instance of the Family class.
        """

        super(RFamily, self).__init__()

        # the unique id identifying a room
        self._room_id = room_id

        # the area designed
        self._area_designed = area_designed

        # the area briefed
        self._area_briefed = area_briefed

        # any other properties
        self._properties = properties

        # the design set in Revit the family instance is placed in
        self._design_set = design_set

        # the design option in Revit the family is placed in
        self._design_option = design_option

        # True, design option in Revit is the primary design option for a set
        self._design_option_is_primary = design_option_is_primary

        # the revit element id
        self._revit_element_id = revit_element_id

    @property
    def room_id(self):
        return self._room_id

    @property
    def area_designed(self):
        return self._area_designed

    @property
    def area_briefed(self):
        return self._area_briefed

    @property
    def properties(self):
        return self._properties

    @property
    def design_set(self):
        return self._design_set

    @property
    def design_option(self):
        return self._design_option

    @property
    def design_option_is_primary(self):
        return self._design_option_is_primary

    @property
    def revit_element_id(self):
        return self._revit_element_id

    def __eq__(self, other):
        """
        Custom compare is equal override

        :param other: Another instance of this class
        :type other: :class:`.RFamily`
        :return: True if properties of other equal properties of this instance, otherwise False.
        :rtype: Bool
        """

        if not isinstance(other, self.__class__):
            return False

        return (
            self.room_id == other.room_id
            and self.area_designed == other.area_designed
            and self.area_briefed == other.area_briefed
            and self.properties == other.properties
            and self.design_set == other.design_set
            and self.design_option == other.design_option
            and self.design_option_is_primary == other.design_option_is_primary
            and self.revit_element_id == other.revit_element_id
        )

    # python 2.7 needs custom implementation of not equal
    def __ne__(self, other):
        return not self.__eq__(other=other)

    def __hash__(self):
        """
        Custom hash override

        Required due to custom __eq__ override present in this class
        """

        return hash(
            (
                self.room_id,
                self.area_designed,
                self.area_briefed,
                self.properties,
                self.design_set,
                self.design_option,
                self.design_option_is_primary,
                self.revit_element_id,
            )
        )
