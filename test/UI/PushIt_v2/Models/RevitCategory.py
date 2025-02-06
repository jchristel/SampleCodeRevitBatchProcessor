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
A class to store revit category information in.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

from duHast.Utilities.Objects.base import Base


class RCategory(Base):

    def __init__(
        self,
        category_name
    ):
        """
        Initializes a new instance of the Family class.
        """

        super(RCategory, self).__init__()

        # the unique id identifying a room
        self._category_name = category_name

       
    @property
    def category_name(self):
        return self._category_name

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
            self.category_name == other.category_name
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
                self.category_name,
            )
        )
