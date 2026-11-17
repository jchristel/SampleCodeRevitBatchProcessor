"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Class for a family nesting path: the family names and the matching family categories from the root family down to a nested family.
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
from duHast.Revit.Family.Data.Objects.family_base_data_processor_defaults import (
    NESTING_SEPARATOR,
)


class FamilyNestingPath(Base):
    def __init__(self, name_path, category_path):
        """
        A family nesting path.

        :param name_path: The family name nesting path, e.g. Table :: Leg :: Bolt
        :type name_path: str
        :param category_path: The matching family category nesting path, e.g. Furniture :: Furniture :: Generic Models
        :type category_path: str
        """

        super(FamilyNestingPath, self).__init__()
        self.name_path = name_path
        self.category_path = category_path

    def get_name_chunks(self):
        """
        :return: The family names, from the root family down.
        :rtype: [str]
        """
        return self.name_path.split(NESTING_SEPARATOR)

    def get_category_chunks(self):
        """
        :return: The family categories, from the root family down.
        :rtype: [str]
        """
        return self.category_path.split(NESTING_SEPARATOR)

    def get_chunks(self):
        """
        The family names and their categories, from the root family down.

        :raises ValueError: If the name path and the category path have a different number of entries.
        :return: The family names and the family categories.
        :rtype: [str], [str]
        """
        name_chunks = self.get_name_chunks()
        category_chunks = self.get_category_chunks()
        if len(name_chunks) != len(category_chunks):
            raise ValueError(
                "Length of nesting name path: {} is not the same as length of nesting category path: {}".format(
                    len(name_chunks), len(category_chunks)
                )
            )
        return name_chunks, category_chunks

    def is_part_of(self, other):
        """
        Checks whether this nesting path is the start of another nesting path (or the same path): its family names and
        categories are the first entries of the other's.

        Whole entries are compared: Table :: Leg is part of Table :: Leg :: Bolt, but not of Table :: Legacy :: Bolt.

        :param other: Another nesting path.
        :type other: :class:`.FamilyNestingPath`
        :return: True if this path is the start of the other path, otherwise False.
        :rtype: bool
        """
        names, categories = self.get_chunks()
        other_names, other_categories = other.get_chunks()
        number_of_entries = len(names)
        return (
            number_of_entries <= len(other_names)
            and names == other_names[:number_of_entries]
            and categories == other_categories[:number_of_entries]
        )

    def __repr__(self):
        return "{}<{}>".format(self.name_path, self.category_path)

    def __eq__(self, other):
        return isinstance(other, FamilyNestingPath) and (
            self.name_path,
            self.category_path,
        ) == (
            other.name_path,
            other.category_path,
        )

    # python 2.7 needs custom implementation of not equal
    def __ne__(self, other):
        return not self.__eq__(other=other)

    def __hash__(self):
        return hash((self.name_path, self.category_path))
