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
import json

from duHast.Revit.Family.Data.Objects import ifamily_data_storage as IFamDataStorage
from duHast.Revit.SharedParameters.Data.Objects.shared_parameter_storage_used_by import (
    FamilySharedParameterDataStorageUsedBy,
)


class FamilySharedParameterDataStorage(IFamDataStorage.IFamilyDataStorage):

    # data type for this class ( used in reports as first entry per row )
    data_type = "SharedParameter"

    # number of properties in this class ( used in report reader function )
    number_of_properties = 10

    def __init__(
        self,
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
            data_type=FamilySharedParameterDataStorage.data_type,
            root_name_path=root_name_path,
            root_category_path=root_category_path,
            family_name=family_name,
            family_file_path=family_file_path,
        )

        # check whether used by is a json list as a string
        if used_by is not None and used_by != "None":
            # check type of data that came in:
            # check if string was passed in
            if isinstance(used_by, str):
                # a string
                used_by_json = json.loads(used_by)
                # if used by was converted into a json object successfully it should now be a list of dictionaries!
                converted_used_by = []
                if isinstance(used_by_json, list):
                    for i in range(len(used_by_json)):
                        try:
                            # convert to FamilySharedParameterDataStorageUsedBy object
                            dummy = FamilySharedParameterDataStorageUsedBy(
                                j=used_by_json[i]
                            )
                            converted_used_by.append(dummy)
                        except Exception as e:
                            raise ValueError(
                                "Failed to convert string {} to FamilySharedParameterDataStorageUsedBy object: {}".format(
                                    used_by_json[i], e
                                )
                            )
                    # override string with converted data
                    used_by = converted_used_by
            # check if a list of family category data storage used by objects was passed in
            elif isinstance(used_by, list):
                # check if every list item is of type FamilySharedParameterDataStorageUsedBy
                for i in range(len(used_by)):
                    if not isinstance(
                        used_by[i], FamilySharedParameterDataStorageUsedBy
                    ):
                        raise ValueError(
                            "used_by list must contain only FamilySharedParameterDataStorageUsedBy objects"
                        )
            elif isinstance(used_by, FamilySharedParameterDataStorageUsedBy):
                # convert to a list
                used_by = [used_by]
            else:
                raise ValueError(
                    "used_by argument supplied must be of type string or type FamilySharedParameterDataStorageUsedBy or a list of FamilySharedParameterDataStorageUsedBy"
                )
        else:
            # default is an empty list
            used_by = []

        self.parameter_guid = parameter_guid
        self.parameter_name = parameter_name
        self.parameter_id = parameter_id
        self.use_counter = use_counter
        self.used_by = used_by

    def __eq__(self, other):
        """
        Custom compare is equal override.

        :param other: Another instance of FamilySharedParameterDataStorage base class
        :type other: :class:`.FamilySharedParameterDataStorage`
        :return: True if all properties of compared class instances are equal, otherwise False.
        :rtype: Bool
        """

        return isinstance(other, FamilySharedParameterDataStorage) and (
            self.data_type,
            self.root_name_path,
            self.root_category_path,
            self.family_name,
            self.family_file_path,
            self.parameter_guid,
            self.parameter_name,
            self.parameter_id,
            self.use_counter,
            self.used_by,
        ) == (
            other.data_type,
            other.root_name_path,
            other.root_category_path,
            other.family_name,
            other.family_file_path,
            other.parameter_guid,
            other.parameter_name,
            other.parameter_id,
            other.use_counter,
            other.used_by,
        )

    # python 2.7 needs custom implementation of not equal
    def __ne__(self, other):
        return not self.__eq__(other=other)
