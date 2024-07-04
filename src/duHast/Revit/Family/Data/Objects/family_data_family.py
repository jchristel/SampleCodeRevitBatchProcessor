"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Family data class.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- contains an entire family nesting tree structure represented as family data container instances

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
from duHast.Revit.Family.Data.Objects.family_base_data_processor_defaults import NESTING_SEPARATOR

class FamilyDataFamily(base.Base):

    def __init__(self, family_name=None, family_category=None, family_file_path=None, nested_families=None):
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
        
        # nested family tree
        self.nested_families = []
        if nested_families is not None:
            for nested in nested_families:
                if(not isinstance(nested, FamilyDataFamily)):
                    raise ValueError("nested_families must be a list of FamilyDataFamily instances. Got: {}".format(type(nested)))
                self.nested_families.append(nested)

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
    
    def _build_nesting_by_name(self):
        """
        Build the nesting name for the family data.

        """
        self.nesting_by_name_path = {}

        for data_container in self.data_containers_unsorted:
            self.nesting_by_name_path[data_container.family_nesting_path] = data_container

    def _build_nesting_by_level(self):
        """
        Build the nesting by level for the family data.

        """

        self.nesting_by_level = {}
        # start at 1 because for nesting level ( 1 based rather then 0 based )
        for data_container in self.data_containers_unsorted:
            if data_container.family_nesting_path == None:
                raise ValueError("Family nesting path is None. Cannot build nesting by level.")
            elif data_container.family_nesting_path == "":
                raise ValueError("Family nesting path is empty. Cannot build nesting by level.")
            else:
                nesting_chunks = data_container.family_nesting_path.split(NESTING_SEPARATOR)

                if len(nesting_chunks) - 1 in self.nesting_by_level:
                    self.nesting_by_level[len(nesting_chunks) - 1].append(data_container)
                else:
                    self.nesting_by_level[len(nesting_chunks) - 1] = [data_container]

    def _get_longest_unique_nesting_path(self):
        """
        Get the longest unique nesting path(s) of the family data.

        :return: The longest unique nesting path as a list. or None if family is not processed.
        :rtype: list or None
        """

        unique_nesting_paths = []
        if self.is_processed == False:
            return

        # loop over nesting by level property and get the longest unique nesting path (multiple)
        # nesting by level has the nesting depth as key and the data containers as value
        # start from the highest nesting level and check whether the next level down overlaps with the current level
        # all path in the highest (deepest) level of nesting are unique
        # if the next level down overlaps with the current level, the path in the next level down is not unique
        # if the next level down does not overlap with the current level, the path in the next level down is unique
        # as soon as there is a nested family, the root path of a family (no nesting) is not unique anymore.

        # get the highest nesting level
        highest_nesting_level = max(self.nesting_by_level.keys())

        # get the data containers at the highest nesting level
        data_containers = self.nesting_by_level[highest_nesting_level]
        if data_containers == None:
            raise ValueError("No data containers found at highest nesting level.")
        
        # add their nesting path to the unique nesting paths
        for data_container in data_containers:
            unique_nesting_paths.append(data_container.family_nesting_path)

        # loop over the nesting levels from the highest to the lowest
        for nesting_level in range(highest_nesting_level - 1, 0, -1):
            # get the data containers at the current nesting level
            data_containers = self.nesting_by_level[nesting_level]
            if data_containers == None:
                raise ValueError("No data containers found at nesting level: {}".format(nesting_level))
            # loop over the data containers at the current nesting level
            for data_container in data_containers:
                # get the nesting path of the current data container
                nesting_path_current_level = data_container.family_nesting_path
                for unique_nesting_path in unique_nesting_paths:
                    found_match = False
                    # check if the current nesting path overlaps with the unique nesting path
                    if nesting_path_current_level in unique_nesting_path:
                        # if it overlaps, remove it from the unique nesting paths
                        found_match = True
                        break
                if not found_match:
                    unique_nesting_paths.append(nesting_path_current_level)
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

    def has_circular_nesting(self):
        """
        Check if the family data has circular nesting.

        Circular nesting is defined as a situation where a nesting path property of a container contains the same family more than once.
        """

        # check if processed and if not process the family data
        self.process(self)

        # get the longest unique nesting path ( can be multiple )
        longest_unique_nesting_path = self._get_longest_unique_nesting_path()

        # keep record of duplicated family names
        duplicated_family_names = []
        # loop over these path and check for multiple occurrence of a family name
        for nesting_path in longest_unique_nesting_path:
            # split path at nesting separator
            nesting_chunks = nesting_path.split(NESTING_SEPARATOR)
            # check if a chunk is already in the list, indicating a circular nesting
            node_names = []
            for nesting_chunk in nesting_chunks:
                if nesting_chunk in node_names:
                    duplicated_family_names.append(nesting_chunk)
                else:
                    node_names.append(nesting_chunk)

        return duplicated_family_names
