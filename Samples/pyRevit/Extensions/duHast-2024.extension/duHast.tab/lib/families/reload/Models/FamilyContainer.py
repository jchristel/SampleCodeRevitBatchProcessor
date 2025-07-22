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
The class representing a all families within a revit model.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Used by RevitFamiliesModel to store all the families in the model.

"""

from families.reload.Models.RevitFamily import RevitFamily
from families.reload.Exceptions.FamilyConflictException import FamiliesConflictException

from duHast.Utilities.Objects.base import Base


class FamiliesContainer(Base):

    def __init__(self):
        """
        A class representing a all families within a revit model.
        """
        super(FamiliesContainer, self).__init__()

        # ini list
        self._revit_families = []

    def get_all_families(self):
        """
        Get all the families in the model.

        :return: all the families in the model
        :rtype: list of :class:`.RevitFamily`
        """

        return self._revit_families

    def add_family(self, revit_family):
        """
        Add a family to the model.

        :param revit_family: the family to add
        :type revit_family: :class:`.RevitFamily`
        """

        # type checking
        if isinstance(revit_family, RevitFamily) == False:
            raise TypeError(
                "revit_family needs to be of type RevitFamily, got {} instead".format(
                    type(revit_family)
                )
            )

        # check if any reservations conflicts with the new one
        for existing_revit_family in self._revit_families:
            if existing_revit_family.Conflicts(revit_family):
                raise FamiliesConflictException(
                    message="New revit family conflicts existing family",
                    existing_family=existing_revit_family,
                    new_family=revit_family,
                )

        self._revit_families.append(revit_family)
