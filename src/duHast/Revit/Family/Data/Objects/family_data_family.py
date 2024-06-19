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
            self.family_name = None
        else:
            raise TypeError(
                "family_name must either be a string or None. Got: {}".format(
                    type(family_name)
                )
            )

        if isinstance(family_category, str) or family_category == None:
            self.family_category = None
        else:
            raise TypeError(
                "family_category must either be a string or None. Got: {}".format(
                    type(family_category)
                )
            )

        if isinstance(family_file_path, str) or family_file_path == None:
            self.family_file_path = None
        else:
            raise TypeError(
                "family_file_path must either be a string or None. Got {}".format(
                    type(family_file_path)
                )
            )
        
        # default value for data containers
        self.data_containers = []

    
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
