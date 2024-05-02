"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Interface for family data storage class.
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

from duHast.Utilities.Objects import base


class IFamilyDataStorage(base.Base):
    def __init__(
        self,
        data_type,
        root_name_path,
        root_category_path,
        family_name,
        family_file_path,
        **kwargs
    ):

        # forwards all unused arguments
        # ini super class to allow multi inheritance in children!
        super(IFamilyDataStorage, self).__init__(**kwargs)

        if isinstance(data_type, str):
            self.data_type = data_type
        else:
            raise ValueError("data_type must be a string")

        if isinstance(root_name_path, str):
            self.root_name_path = root_name_path
        else:
            raise ValueError("root_name_path must be a string")

        if isinstance(root_category_path, str):
            self.root_category_path = root_category_path
        else:
            raise ValueError("root_category_path must be a string")

        if isinstance(family_name, str):
            self.family_name = family_name
        else:
            raise ValueError("family_name must be a string")

        if isinstance(family_file_path, str):
            self.family_file_path = family_file_path
        else:
            raise ValueError("family_file_path must be a string")

    def get_data(self):
        """
        Get the data from the object als dictionary.
        """

        return {key: value for key, value in self.__dict__.items()}

    def get_property_names(self):
        return  self.__dict__.keys()
