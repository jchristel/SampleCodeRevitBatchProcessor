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

        super(FamilyTypeDataStorageManager).__init__()

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
