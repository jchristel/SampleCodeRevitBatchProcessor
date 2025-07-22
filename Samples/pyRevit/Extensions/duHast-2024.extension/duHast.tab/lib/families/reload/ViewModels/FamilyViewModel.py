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
RevitFamily view model class.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Used to display family properties in a list view.

"""

from duHast.UI.Objects.WPF.ViewModels.ViewModelBase import ViewModelBase
from families.reload.Objects.match_status_names import MatchStatusNames
from families.reload.Models.RevitFamily import RevitFamily


class FamilyViewModel(ViewModelBase):

    def __init__(self, family):
        """
        A view model for a Revit family.

        :param family: a Revit family object
        :type family: :class:`.RevitFamily`
        """

        super(FamilyViewModel, self).__init__()

        if not (isinstance(family, RevitFamily)):
            raise ValueError(
                "family needs to be of type RevitFamily, got {} instead.".format(
                    type(family)
                )
            )

        self._family = family

        self._match_status = MatchStatusNames.NO_MATCH.value
        self._is_selected = False
        self._family_file_path = None

    @property
    def IsSelected(self):
        return self._is_selected

    @IsSelected.setter
    def IsSelected(self, value):
        self._is_selected = value

    @property
    def FamilyName(self):
        return self._family.family_name

    @property
    def FamilyCategory(self):
        return self._family.family_category

    @property
    def FamilyIsShared(self):
        return self._family.is_shared

    @property
    def MatchStatus(self):
        return self._match_status

    @MatchStatus.setter
    def MatchStatus(self, value):
        self._match_status = value

    @property
    def FamilyFilePath(self):
        return self._family_file_path

    @FamilyFilePath.setter
    def FamilyFilePath(self, value):
        self._family_file_path = value
