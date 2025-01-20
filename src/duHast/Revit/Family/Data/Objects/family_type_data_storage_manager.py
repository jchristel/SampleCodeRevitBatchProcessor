"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Class for family type data storage class.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Used as accumulate all family type storage class instances when retrieving family type data from a family file.

"""

#
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


from duHast.Utilities.Objects.base import Base
from duHast.Revit.Family.Data.Objects.family_type_data_storage import (
    FamilyTypeDataStorage,
)


class FamilyTypeDataStorageManager(Base):

    def __init__(self):

        super(FamilyTypeDataStorageManager, self).__init__()

        # storage for family type data
        self._family_type_data_storage = []

    @property
    def family_type_data_storage(self):
        return self._family_type_data_storage

    def add_family_type_data_storage(self, family_type_data_storage):
        """
        add family type data storage to the manager

        :param family_type_data_storage: family type data storage instance
        :type family_type_data_storage: FamilyTypeDataStorage
        """

        if not isinstance(family_type_data_storage, FamilyTypeDataStorage):
            raise ValueError(
                "family_type_data_storage must be an instance of FamilyTypeDataStorage"
            )

        self._family_type_data_storage.append(family_type_data_storage)
    
    def get_difference(self, other):
        """
        get the difference between two family type data storage managers

        :param other: the other family type data storage manager
        :type other: FamilyTypeDataStorageManager

        :return: the difference between the two family type data storage managers
        :rtype: FamilyTypeDataStorageManager
        """

        if not isinstance(other, FamilyTypeDataStorageManager):
            raise ValueError(
                "other must be an instance of FamilyTypeDataStorageManager"
            )

        difference = []

        
        for family_type_data_storage in self.family_type_data_storage:

            # flag to check whether type (by name only exists in other)
            type_data_storage_has_match = False
            # loop over storage types from library to find a match
            for other_family_type_data_storage in other.family_type_data_storage:
                if family_type_data_storage.is_match_by_names_and_catgory(other_family_type_data_storage):
                    # set a falg for match
                    type_data_storage_has_match = True
                    # get the differences between the two family type data storage instances
                    diff_entries = family_type_data_storage.get_comparison_report_parameter_values(other_family_type_data_storage)
                    # if there are differences, add them to the difference list
                    for entry in diff_entries:
                        difference.append(entry)
                    break
                else:
                    continue

            if not type_data_storage_has_match:
                difference.append([family_type_data_storage.family_name, family_type_data_storage.root_category_path, family_type_data_storage.family_type_name, "Not found in library"])
            
        return difference

    def get_differences_report_header_row(self):
        """
        get the header row for the differences report

        :return: the header row for the differences report
        :rtype: [str]
        """

        return ["Family name", "Family category", "Family type name", "Family type exists in Library", "Parameter name", "Parameter exists in library", "Parameter difference"]
    

    def remove_ghost_types(self, type_names):
        """
        Remove ghost types from the family type data storage manager
        Ghost types are types that are not present in the family file but listed in the part atom export from a Family class instance

        Any type that is not in the type_names list is considered a ghost type
        
        :param type_names: list of type names which are present in the document (project file) for this family
        :type type_names: [str]
        """

        for family_type_data_storage in self.family_type_data_storage:
            if family_type_data_storage.family_type_name not in type_names:
                self.family_type_data_storage.remove(family_type_data_storage)