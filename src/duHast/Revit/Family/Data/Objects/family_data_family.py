"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Family data class.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- contains:

    - an entire family nesting tree structure represented as other  FamilyDataFamily instances
    - all FamilyDataContainer instances belonging to this family only ( identified by unique combination on family name nesting path and family category nesting path )

"""

#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2024, Jan Christel
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

from duHast.Utilities.Objects import base
from duHast.Revit.Family.Data.Objects.family_data_container import FamilyDataContainer
from duHast.Revit.Family.Data.Objects.family_base_data_processor_defaults import (
    NESTING_SEPARATOR,
)


class FamilyDataFamily(base.Base):
    def __init__(
        self,
        family_name=None,
        family_category=None,
        family_file_path=None,
        family_nesting_path=None,
        family_category_nesting_path=None,
        is_root_family=False,
        nested_families=None,
    ):
        """
        Family data class.

        - contains an entire family nesting tree structure represented as family data container instances

        :param family_name: The name of the family.
        :type family_name: str
        :param family_category: The Revit category of the family.
        :type family_category: str
        :param family_file_path: The file path of the family.
        :type family_file_path: str

        """

        # forwards all unused arguments
        # ini super class to allow multi inheritance in children!
        super(FamilyDataFamily, self).__init__()

        # set some base properties to their default values
        if isinstance(family_name, str) or family_name == None:
            self.family_name = family_name
        else:
            raise TypeError(
                "family_name must either be a string or None. Got: {}".format(
                    type(family_name)
                )
            )

        if isinstance(family_category, str) or family_category == None:
            self.family_category = family_category
        else:
            raise TypeError(
                "family_category must either be a string or None. Got: {}".format(
                    type(family_category)
                )
            )

        if isinstance(family_file_path, str) or family_file_path == None:
            self.family_file_path = family_file_path
        else:
            raise TypeError(
                "family_file_path must either be a string or None. Got {}".format(
                    type(family_file_path)
                )
            )

        if isinstance(family_nesting_path, str) or family_nesting_path == None:
            self.family_nesting_path = family_nesting_path
        else:
            raise TypeError(
                "family_nesting_path must either be a string or None. Got {}".format(
                    type(family_nesting_path)
                )
            )

        if (
            isinstance(family_category_nesting_path, str)
            or family_category_nesting_path == None
        ):
            self.family_category_nesting_path = family_category_nesting_path
        else:
            raise TypeError(
                "family_category_nesting_path must either be a string or None. Got {}".format(
                    type(family_category_nesting_path)
                )
            )

        if isinstance(is_root_family, bool):
            self.is_root_family = is_root_family
        else:
            raise TypeError(
                "is_root_family must be a boolean. Got {}".format(type(is_root_family))
            )

        # nested family tree
        self.nested_families_unsorted = []
        if nested_families is not None:
            for nested in nested_families:
                if not isinstance(nested, FamilyDataFamily):
                    raise ValueError(
                        "nested_families must be a list of FamilyDataFamily instances. Got: {}".format(
                            type(nested)
                        )
                    )
                self.nested_families_unsorted.append(nested)

        # default value for data containers
        self.data_containers_unsorted = []

        # default value for nesting by name path
        self.nesting_by_name_path = {}

        # default value for nesting by level
        self.nesting_by_level = {}

        # flag indicating whether nodes have been processed
        self.is_processed = False

    def __repr__(self):
        return "{}<{}>".format(self.family_name, self.family_category)

    def __eq__(self, other):
        """
        Compares family_name, family_category, family_nesting_path and family_category_nesting_path properties only

        :param other: Another FamilyDataFamily instance
        :type other: :class:`.FamilyDataFamily`
        :return: True if family_name and family_category are equal otherwise false
        :rtype: bool
        """

        return isinstance(other, FamilyDataFamily) and (
            self.family_name,
            self.family_category,
            self.family_nesting_path,
            self.family_category_nesting_path,
        ) == (
            other.family_name,
            other.family_category,
            other.family_nesting_path,
            other.family_category_nesting_path,
        )

    # python 2.7 needs custom implementation of not equal
    def __ne__(self, other):
        return not self.__eq__(other=other)

    def _build_nesting_by_name(self):
        """
        Build the nesting name for the family data.

        """
        self.nesting_by_name_path = {}

        for family_instance_data in self.nested_families_unsorted:
            self.nesting_by_name_path[
                family_instance_data.family_nesting_path
            ] = family_instance_data

    def _build_nesting_by_level(self):
        """
        Build the nesting by level for the family data.

        """

        self.nesting_by_level = {}
        # start at 1 because nesting level 0 is this family (root)
        # ( 1 based rather then 0 based )
        for family_instance_data in self.nested_families_unsorted:
            if family_instance_data.family_nesting_path == None:
                raise ValueError(
                    "Family nesting path is None. Cannot build nesting by level."
                )
            elif family_instance_data.family_nesting_path == "":
                raise ValueError(
                    "Family nesting path is empty. Cannot build nesting by level."
                )
            else:
                nesting_chunks = family_instance_data.family_nesting_path.split(
                    NESTING_SEPARATOR
                )

                if len(nesting_chunks) - 1 in self.nesting_by_level:
                    self.nesting_by_level[len(nesting_chunks) - 1].append(
                        family_instance_data
                    )
                else:
                    self.nesting_by_level[len(nesting_chunks) - 1] = [
                        family_instance_data
                    ]

    def get_longest_unique_nesting_path(self):
        """
        Get the longest unique family name nesting path(s) and family category nesting path(s) of the family data.

        :return: The longest unique nesting path as a list of tuples, or None if family is not processed.
        :rtype: list[(family_name_nesting, family_category_nesting)] or None
        """

        unique_nesting_paths = []
        if self.is_processed == False:
            return

        # loop over nesting by level property and get the longest unique family name nesting path (multiple)
        # anf category nesting path as a tuple where 0 index is the name path, and 1 index the category nesting path
        # nesting by level has the nesting depth as key and the data containers as value
        # start from the highest nesting level and check whether the next level down overlaps with the current level
        # all path in the highest (deepest) level of nesting are unique
        # if the next level down overlaps with the current level, the path in the next level down is not unique
        # if the next level down does not overlap with the current level, the path in the next level down is unique
        # as soon as there is a nested family, the root path of a family (no nesting) is not unique anymore.

        # get the highest nesting level
        if len(self.nesting_by_level) == 0:
            # if no nesting levels found return the root family only (?)
            unique_nesting_paths.append(
                (self.family_nesting_path, self.family_category_nesting_path)
            )
        else:
            highest_nesting_level = max(self.nesting_by_level.keys())

            # get the data containers at the highest nesting level
            family_data_instances = self.nesting_by_level[highest_nesting_level]
            if family_data_instances == None:
                raise ValueError("No data containers found at highest nesting level.")

            # add their nesting path to the unique nesting paths
            for family_data_instance in family_data_instances:
                # add tuple made up off family name nesting path at 0 and family category nesting path at 1
                unique_nesting_paths.append(
                    (
                        family_data_instance.family_nesting_path,
                        family_data_instance.family_category_nesting_path,
                    )
                )

            # loop over the nesting levels from the highest to the lowest
            for nesting_level in range(highest_nesting_level - 1, 0, -1):
                # get the data containers at the current nesting level
                family_data_instances = self.nesting_by_level[nesting_level]
                if family_data_instances == None:
                    raise ValueError(
                        "No data containers found at nesting level: {}".format(
                            nesting_level
                        )
                    )
                # loop over the data containers at the current nesting level
                for family_data_instance in family_data_instances:
                    # get the nesting path of the current data container
                    nesting_path_family_name_current_level = (
                        family_data_instance.family_nesting_path
                    )
                    nesting_path_category_current_level = (
                        family_data_instance.family_category_nesting_path
                    )
                    # check for match of both path
                    for unique_nesting_path in unique_nesting_paths:
                        found_match = False
                        # check if the current nesting path overlaps with the unique nesting path
                        if (
                            nesting_path_family_name_current_level
                            in unique_nesting_path[0]
                            and nesting_path_category_current_level
                            in unique_nesting_path[1]
                        ):
                            # if it overlaps, remove it from the unique nesting paths
                            found_match = True
                            break
                    if not found_match:
                        unique_nesting_paths.append(
                            (
                                nesting_path_family_name_current_level,
                                nesting_path_category_current_level,
                            )
                        )
        # return the unique nesting paths
        return unique_nesting_paths

    def process(self):
        """
        Process the family data.

        - build the nesting by name path
        - build the nesting by level

        """

        # check if processed
        if self.is_processed:
            return

        # build internal data structures
        self._build_nesting_by_name()
        self._build_nesting_by_level()

        # set processed flag
        self.is_processed = True

    def add_data_container(self, data_container):
        """
        Add a data container to the family data.

        """

        if not isinstance(data_container, FamilyDataContainer):
            raise TypeError(
                "data_container must be an instance of FamilyDataContainer. Got: {}".format(
                    type(data_container)
                )
            )

        self.data_containers_unsorted.append(data_container)

        # set flag indicating that the family data has changed and needs to be processed again
        self.is_processed = False

    def add_nested_family_instance(self, nested_family_instance):
        """
        Add a nested family instance.

        :param nested_family_instance: The family instance to be added
        :type nested_family_instance: :class:`.FamilyDataFamily`
        :raises TypeError: If nested_family_instance is not an instance of FamilyDataFamily a type error will be raised.
        """

        # check correct type
        if not isinstance(nested_family_instance, FamilyDataFamily):
            raise TypeError(
                "nested_family_instance must be an instance of FamilyDataFamily. Got: {}".format(
                    type(nested_family_instance)
                )
            )

        # check if nested family instance already exists...if so raise an exception
        if nested_family_instance in self.nested_families_unsorted:
            raise ValueError(
                "family instance {} {}  already exists in family".format(
                    nested_family_instance.family_name,
                    nested_family_instance.family_category,
                )
            )

        # add the instance
        self.nested_families_unsorted.append(nested_family_instance)

        # set flag indicating that the family data has changed and needs to be processed again
        self.is_processed = False

    def get_all_storage_data_as_strings(self):
        """
        Returns the data storage within each storage container within this family as well as within the nested families as a a list of string.

        :return: A dictionary where key is the data storage type, and value is a nested list of lists containing the data storage string value
        :rtype: {key:[[str]]}
        """

        # set up the return value
        data_storage_as_string = {}

        # loop over each container belonging directly to this family and get its dictionary representing the storage type and its values as a list o string
        for container in self.data_containers_unsorted:
            container_data_storage_dic = container.get_data_string_list()
            for key, value in container_data_storage_dic.items():
                # check if that storage key is already in the return dictionary
                if key in data_storage_as_string:
                    # if extend its value list by the new containers values list
                    data_storage_as_string[key].extend(value)
                else:
                    # set up a new key and value list
                    data_storage_as_string[key] = value

        # loop over nested families and get their storage values too
        for nested_family in self.nested_families_unsorted:
            family_data_storage_dic = nested_family.get_all_storage_data_as_strings()
            for key, value in family_data_storage_dic.items():
                # check if that storage key is already in the return dictionary
                if key in data_storage_as_string:
                    # if extend its value list by the new containers values list
                    data_storage_as_string[key].extend(value)
                else:
                    # set up a new key and value list
                    data_storage_as_string[key] = value

        return data_storage_as_string

    def get_all_storage_headers_as_strings(self):
        """
        Returns all property names used in storage instances in containers within this family and any nested families.

        :return: A dictionary where key is the data storage type, and value is a list containing the data storage properties as string values
        :rtype: {key:[[str]]}
        """

        # set up the return value
        data_storage_as_string = {}
        # loop over each container belonging directly to this family and get its dictionary representing the storage type and its header values as a list o string
        for container in self.data_containers_unsorted:
            container_data_storage_dic = container.get_data_headers_list()
            for key, value in container_data_storage_dic.items():
                # check if that storage key is already in the return dictionary
                if key not in data_storage_as_string:
                    # if not add its value list by the new containers values list
                    data_storage_as_string[key] = value

        # loop over nested families and get their storage header values too
        for nested_family in self.nested_families_unsorted:
            family_data_storage_dic = nested_family.get_all_storage_headers_as_strings()
            for key, value in family_data_storage_dic.items():
                # check if that storage key is already in the return dictionary
                if key not in data_storage_as_string:
                    # if extend its value list by the new containers values list
                    data_storage_as_string[key] = value
        return data_storage_as_string

    def has_circular_nesting(self):
        """
        Check if the family data has circular nesting.

        Circular nesting is defined as a situation where a nesting path property of a container contains the same family more than once.

        returns a list of tuples in format:

            - 0 index the nesting level at which the circular nesting occurs
            - 1 index a string in format: family name :: family category
            - 2 the entire family name nesting path this circular reference appeared on

        """

        # check if processed and if not process the family data
        if not self.is_processed:
            self.process()

        # get the longest unique nesting path ( can be multiple )
        longest_unique_nesting_path = self.get_longest_unique_nesting_path()

        # keep record of duplicated family names
        duplicated_family_names = []
        # loop over these path and check for multiple occurrence of a family name
        for nesting_path in longest_unique_nesting_path:

            # split path at nesting separator ( should have the same length )
            nesting_chunks_family_names = nesting_path[0].split(NESTING_SEPARATOR)
            nesting_chunks_category = nesting_path[1].split(NESTING_SEPARATOR)

            # double check path length are equal!
            if len(nesting_chunks_family_names) != len(nesting_chunks_category):
                raise ValueError(
                    "Length of nesting name path: {} is not the same as length of nesting category path: {}".format(
                        len(nesting_chunks_family_names), len(nesting_chunks_category)
                    )
                )

            # check if a chunk is already in the list, indicating a circular nesting
            node_names = []
            for i in range(len(nesting_chunks_family_names)):

                # build a test value made from family name and category name
                test_value = (
                    nesting_chunks_family_names[i]
                    + NESTING_SEPARATOR
                    + nesting_chunks_category[i]
                )

                # check if test value is already in list...indicating a circular nesting reference
                if test_value in node_names:
                    # add family name and category to duplicated list including the nesting level
                    duplicated_family_names.append((i, test_value, nesting_path[0]))
                else:
                    # add test value to nodes list
                    node_names.append(test_value)

        return duplicated_family_names
