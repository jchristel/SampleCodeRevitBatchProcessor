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

class FamilyDataFamily(base.Base):

    def __init__(self, family_name=None, family_category=None, family_file_path=None):
        """
        Family data class.

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
        
        # default value for data containers
        self.data_containers = []

        # default value for nesting by name path
        self.nesting_by_name_path = {}

        self.nesting_by_level = {}

    def _build_nesting_by_name(self):
        """
        Build the nesting name for the family data.

        """
        self.nesting_by_name_path = {
        }

        for data_container in self.data_containers:
           self.nesting_by_name_path[data_container.family_nesting_path]

    def _build_nesting_by_level(self):

        self.nesting_by_level = {}
        # start at 1 because for nesting level ( 1 based rather then 0 based )
        for data_container in self.data_containers:
            nesting_chunks = data_container.family_nesting_path.split(" :: ")
           
            if len(nesting_chunks) - 1 in self.nesting_by_level:
                self.nesting_by_level[len(nesting_chunks) - 1].append(data_container)
            else:
                self.nesting_by_level[len(nesting_chunks) - 1] = [data_container]

    def _get_longest_unique_nesting_path(self):
        pass

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

        
        self.data_containers.append(data_container)

    def has_circular_nesting(self):
        """
        Check if the family data has circular nesting.

        Circular nesting is defined as a situation where a nesting path property of a container contains the same family more than once.
        """

        # build the nesting by level
        self._build_nesting_by_level(self)

        longest_unique_nesting_path = self._get_longest_unique_nesting_path()

        # loop over these path and check for multiple occurrence
        

        return False
