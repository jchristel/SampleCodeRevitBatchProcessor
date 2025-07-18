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
#

"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The class representing a Revit family.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

from duHast.Utilities.Objects.base import Base
from RevitFamilyId import FamilyID


class RevitFamily(Base):

    def __init__(self, id, family_name, family_category, is_shared, match_status):
        """
        A class representing a Revit family.

        :param id: the id of the family
        :type id: :class:`.FamilyID`
        :param family_name: the name of the family
        :type family_name: str
        :param family_category: the category of the family
        :type family_category: str
        :param is_shared: True if the family is shared, otherwise False
        :type is_shared: bool
        :param match_status: the match status of the family
        :type match_status: str
        """

        super(RevitFamily, self).__init__()

        # set the id
        self.id = id

        # check type
        if isinstance(family_name, str) == False:
            raise TypeError(
                "family_name needs to be of type string, got {} instead".format(
                    type(family_name)
                )
            )
        self.family_name = family_name

        if isinstance(family_category, str) == False:
            raise TypeError(
                "family_category needs to be of type string. Got {} instead".format(id)
            )
        self.family_category = family_category

        if isinstance(is_shared, bool) == False:
            raise TypeError(
                "is_shared needs to be of type bool. Got {} instead".format(id)
            )
        self.is_shared = is_shared

        if isinstance(match_status, str) == False:
            raise TypeError(
                "match_status needs to be of type string. Got {} instead".format(id)
            )
        self.match_status = match_status

        # filed to store the file path to reload famiy from in
        self.family_file_path = None

    def Conflicts(self, revit_family):
        """
        Check if the current family conflicts with another family based on the id.

        :param revit_family: the family to compare with
        :type revit_family: :class:`.RevitFamily`
        :return: True if the families conflict, otherwise False
        :rtype: bool
        """

        # check type
        if isinstance(revit_family, RevitFamily) == False:
            raise TypeError(
                "revit_family needs to be of type RevitFamily, got {} instead".format(
                    type(revit_family)
                )
            )

        # check the  id
        if revit_family.id != self.id:
            return False
        else:
            return True

    @property
    def id(self):
        return self._id.id

    @id.setter
    def id(self, value):
        # ini values
        if isinstance(value, FamilyID) == False:
            raise TypeError(
                "id needs to be of type RoomID. Got {} instead".format(value)
            )
        self._id = value
