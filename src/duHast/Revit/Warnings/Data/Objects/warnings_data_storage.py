"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Class for family shared parameter data storage class.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2023, Jan Christel
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

from duHast.Revit.Family.Data.Objects import ifamily_data_storage as IFamDataStorage


class FamilyWarningsDataStorage(IFamDataStorage.IFamilyDataStorage):

    # data type for this class ( used in reports as first entry per row )
    data_type = "Warnings"

    # number of properties in this class ( used in report reader function )
    number_of_properties = 9

    def __init__(
        self,
        root_name_path,
        root_category_path,
        family_name,
        family_file_path,
        warning_text,
        warning_guid,
        warning_related_ids,
        warning_other_ids,
        **kwargs
    ):

        # store args in base class
        super(FamilyWarningsDataStorage, self).__init__(
            data_type=FamilyWarningsDataStorage.data_type,
            root_name_path=root_name_path,
            root_category_path=root_category_path,
            family_name=family_name,
            family_file_path=family_file_path,
        )

        self.warning_text = warning_text
        self.warning_guid = warning_guid
        self.warning_related_ids = warning_related_ids
        self.warning_other_ids = warning_other_ids

    def __eq__(self, other):
        """
        Custom compare is equal override.

        :param other: Another instance of FamilyWarningsDataStorage base class
        :type other: :class:`.FamilyWarningsDataStorage`
        :return: True if all properties of compared class instances are equal, otherwise False.
        :rtype: Bool
        """

        return isinstance(other, FamilyWarningsDataStorage) and (
            self.data_type,
            self.root_name_path,
            self.root_category_path,
            self.family_name,
            self.family_file_path,
            self.warning_text,
            self.warning_guid,
            self.warning_related_ids,
            self.warning_other_ids,
        ) == (
            other.data_type,
            other.root_name_path,
            other.root_category_path,
            other.family_name,
            other.family_file_path,
            other.warning_text,
            other.warning_guid,
            other.warning_related_ids,
            other.warning_other_ids,
        )

    # python 2.7 needs custom implementation of not equal
    def __ne__(self, other):
        return not self.__eq__(other=other)
