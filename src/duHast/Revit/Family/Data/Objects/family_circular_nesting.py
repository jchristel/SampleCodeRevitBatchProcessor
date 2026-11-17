"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Class for a circular nesting found in a family: a family nested into itself somewhere down its nesting tree.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""


#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2026, Jan Christel
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


class FamilyCircularNesting(Base):
    def __init__(
        self, family, nesting_level, family_name, family_category, nesting_path
    ):
        """
        A circular nesting found in a family.

        :param family: The family in whose nesting tree the circular nesting was found.
        :type family: :class:`.FamilyDataFamily`
        :param nesting_level: The nesting level at which the family appears again (0 is the family itself).
        :type nesting_level: int
        :param family_name: The name of the family appearing more than once in the nesting path.
        :type family_name: str
        :param family_category: The Revit category of the family appearing more than once in the nesting path.
        :type family_category: str
        :param nesting_path: The family name nesting path the circular nesting appeared on.
        :type nesting_path: str
        """

        super(FamilyCircularNesting, self).__init__()
        self.family = family
        self.nesting_level = nesting_level
        self.family_name = family_name
        self.family_category = family_category
        self.nesting_path = nesting_path

    def __eq__(self, other):
        return isinstance(other, FamilyCircularNesting) and (
            self.family,
            self.nesting_level,
            self.family_name,
            self.family_category,
            self.nesting_path,
        ) == (
            other.family,
            other.nesting_level,
            other.family_name,
            other.family_category,
            other.nesting_path,
        )

    # python 2.7 needs custom implementation of not equal
    def __ne__(self, other):
        return not self.__eq__(other=other)

    def __hash__(self):
        return hash(
            (
                self.family,
                self.nesting_level,
                self.family_name,
                self.family_category,
                self.nesting_path,
            )
        )
