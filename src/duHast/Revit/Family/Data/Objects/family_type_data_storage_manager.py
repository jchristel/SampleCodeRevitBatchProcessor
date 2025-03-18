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

        # set up fields for family name and category
        self._family_name = None
        self._family_category = None

    @property
    def family_type_data_storage(self):
        return self._family_type_data_storage

    @property
    def family_name(self):
        return self._family_name

    @family_name.setter
    def family_name(self, family_name):
        # only allow to set the family name if its current value is None
        if self._family_name is not None:
            raise ValueError("family_name can only be set once")
        self._family_name = family_name

    @property
    def family_category(self):
        return self._family_category

    @family_category.setter
    def family_category(self, family_category):
        # only allow to set the family category if its current value is None
        if self._family_category is not None:
            raise ValueError("family_category can only be set once")
        self._family_category = family_category

    @property
    def family_has_types(self):
        """
        Check if the family has types
        (might have not types if all types where purge from a model and just the family was left)

        :return: True if the family has types, False otherwise
        :rtype: bool
        """

        return len(self.family_type_data_storage) > 0


    def add_family_type_data_storage(self, family_type_data_storage):
        """
        add family type data storage to the manager.

        This will also set the family name and category of this storage manager instance if they are not set yet.

        :param family_type_data_storage: family type data storage instance
        :type family_type_data_storage: FamilyTypeDataStorage
        """

        if not isinstance(family_type_data_storage, FamilyTypeDataStorage):
            raise ValueError(
                "family_type_data_storage must be an instance of FamilyTypeDataStorage"
            )

        # check if the family name and category are set
        if self.family_name is None:
            self.family_name = family_type_data_storage.family_name
        if self.family_category is None:
            self.family_category = family_type_data_storage.root_category_path

        # check if the family name and category match the family type data storage instance
        if self.family_name != family_type_data_storage.family_name:
            raise ValueError(
                "family_name does not match the family type data storage instance"
            )
        if self.family_category != family_type_data_storage.root_category_path:
            raise ValueError(
                "family_category does not match the family type data storage instance"
            )

        self._family_type_data_storage.append(family_type_data_storage)


    def remove_family_type(self, family_type_name):
        """
        Remove a family type from the family type data storage manager

        :param family_type_name: the name of the family type to remove
        :type family_type_name: str
        """

        filtered_list = []
        removed_type= False
        for family_type_data_storage in self.family_type_data_storage:
            if family_type_data_storage.family_type_name !=  family_type_name:
                filtered_list.append(family_type_data_storage)
            else:
                # remove the family type data storage instance
                removed_type = True
                pass

        # replace the old list with the filtered list
        self._family_type_data_storage = filtered_list
        return removed_type


    def get_catalogue_file_data(self, parameter_names=None):
        """
        Get the catalogue file data for the family type data storage manager

        :param parameter_names: list of parameter names to include in the catalogue file data and the order in which they should be included.
        If None, all parameters will be included in the order they are stored in the family type data storage instances.
        :type parameter_names: [str]
        :return: the catalogue file data for the family type data storage manager
        :rtype: [[str]]
        """

        catalogue_file_data = []

        # loop over type data storage instances and get the catalogue file data
        for family_type_data_storage in self.family_type_data_storage:
            catalogue_file_data.append(
                family_type_data_storage.get_catalogue_file_data(parameter_names)
            )


        return catalogue_file_data


    def get_catalogue_file_header_row(self, parameter_names=None):
        """
        Get the header row for the catalogue file

        :param parameter_names: list of parameter names to include in the catalogue file data and the order in which they should be included.
        If None, all parameters will be included in the order they are stored in the family type data storage instances.
        :type parameter_names: [str]
        :return: the header row for the catalogue file
        :rtype: [str]
        """

        header_row = []

        # loop over type data storage instances and get the header row based on the first instance
        for family_type_data_storage in self.family_type_data_storage:
            header_row = family_type_data_storage.get_catalogue_file_header_row(parameter_names)
            break

        return header_row


    def get_report_data(self, project_name=None):
        """
        Get the report data for the family type data storage manager

        :return: the report data for the family type data storage manager
        :rtype: [[str]]
        """

        report_data = []

        for family_type_data_storage in self.family_type_data_storage:
            type_data = family_type_data_storage.get_report_data()
            for fam in type_data:
                report_data.append(fam)
            # report_data.append(family_type_data_storage.get_report_data())

        return report_data


    def get_difference(self, other):
        """
        Get the difference between two family type data storage managers

        Return format is a list of lists, where each list contains the following:
        - Family name
        - Family category
        - family exists in library
        - Family type name
        - Family type exists in Library
        - Parameter name
        - Parameter exists in library
        - Parameter difference

        An entry in the list is only returned if there is a difference between the two family type data storage managers

        :param other: the other family type data storage manager
        :type other: FamilyTypeDataStorageManager

        :return: the difference between the two family type data storage managers
        :rtype: [[str]]
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
                if family_type_data_storage.is_match_by_names_and_category(
                    other_family_type_data_storage
                ):
                    # set a flag for match
                    type_data_storage_has_match = True
                    # get the differences between the two family type data storage instances
                    diff_entries = (
                        family_type_data_storage.get_comparison_report_parameter_values(
                            other_family_type_data_storage
                        )
                    )
                    # if there are differences, add them to the difference list
                    for entry in diff_entries:
                        difference.append(entry)
                    break
                else:
                    continue

            if not type_data_storage_has_match:
                difference.append(
                    [
                        family_type_data_storage.family_name,
                        family_type_data_storage.root_category_path,
                        "Found match in library",
                        family_type_data_storage.family_type_name,
                        "No match in library",
                    ]
                )

        return difference


    def get_differences_report_header_row(self):
        """
        get the header row for the differences report

        :return: the header row for the differences report
        :rtype: [str]
        """

        return [
            "Family name",
            "Family category",
            "Family exists in library",
            "Family type name",
            "Family type exists in Library",
            "Parameter name",
            "Parameter exists in library",
            "Parameter difference (Project -> Library)",
        ]


    def remove_ghost_types(self, type_names):
        """
        Remove ghost types from the family type data storage manager
        Ghost types are types that are not present in the family file but listed in the part atom export from a Family class instance

        Any type that is not in the type_names list is considered a ghost type

        :param type_names: list of type names which are present in the document (project file) for this family
        :type type_names: [str]
        """

        filtered_list = []
        for family_type_data_storage in self.family_type_data_storage:
            if family_type_data_storage.family_type_name in type_names:
                filtered_list.append(family_type_data_storage)
            else:
                # remove the family type data storage instance
                pass

        # replace the old list with the filtered list
        self._family_type_data_storage = filtered_list
