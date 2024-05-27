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
from duHast.Revit.SharedParameters.Data.Objects.shared_parameter_storage_used_by import FamilySharedParameterDataStorageUsedBy


class FamilySharedParameterDataStorage(IFamDataStorage.IFamilyDataStorage):

    def __init__(
        self,
        data_type,
        root_name_path,
        root_category_path,
        family_name,
        family_file_path,
        parameter_guid,
        parameter_name,
        parameter_id,
        use_counter,
        used_by,
        **kwargs
    ):

        # store args in base class
        super(FamilySharedParameterDataStorage, self).__init__(
            data_type=data_type,
            root_name_path=root_name_path,
            root_category_path=root_category_path,
            family_name=family_name,
            family_file_path=family_file_path,
        )

        self.parameter_guid = parameter_guid
        self.parameter_name = parameter_name
        self.parameter_id = parameter_id
        self.use_counter = use_counter
        self.used_by = used_by


    def _used_by_contains(self, guid):
        if isinstance(self.used_by, list) == False:
            raise ValueError(
                "used by must be an instance of list but is type: {}".format(
                    type(self.used_by)
                )
            )
        # might either be a dictionary or a family name
        for entry in self.used_by:
            if isinstance(entry, FamilySharedParameterDataStorageUsedBy) == False:
                raise ValueError(
                    "used by item must be an instance of FamilySharedParameterDataStorageUsedBy but is type: {}".format(
                        type(entry)
                    )
                )
            else:
                pass