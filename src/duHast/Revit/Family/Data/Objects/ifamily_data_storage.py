"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Interface for family data storage class.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


Notes:

- any revit specific data types i.e. ElementId need to be converted to int or string for JSON to work and in order for these classes to be used outside the Revit API!
- any string values need to be encoded to utf-8 and decoded back to utf-8 to avoid encoding issues


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
from duHast.Utilities.utility import encode_utf8
from duHast.Revit.Family.Data.Objects.ifamily_data_storage_used_by import (
    IFamilyDataStorageUsedBy,
)
import System
import json


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

    def __eq__(self, other):
        """
        Custom compare is equal override.

        :param other: Another instance of IFamilyDataStorage base class
        :type other: :class:`.IFamilyDataStorage`
        :return: True if all properties of compared class instances are equal, otherwise False.
        :rtype: Bool
        """

        return isinstance(other, IFamilyDataStorage) and (
            self.data_type,
            self.root_name_path,
            self.root_category_path,
            self.family_name,
            self.family_file_path,
        ) == (
            other.data_type,
            other.root_name_path,
            other.root_category_path,
            other.family_name,
            other.family_file_path,
        )

    # python 2.7 needs custom implementation of not equal
    def __ne__(self, other):
        return not self.__eq__(other=other)

    def update_usage(self, other_storage):
        """
        Update the usage of this storage object with the usage of another storage object by:

        - adding the use counter of the other storage object to this storage object's use counter
        - appending the root name path of the other storage object to this storage object's used_by list

        """

        if isinstance(other_storage, IFamilyDataStorage):
            self.use_counter = self.use_counter + other_storage.use_counter
            # just append the used by storage class
            for dummy in other_storage.used_by:
                self.used_by.append(dummy)
        else:
            raise ValueError(
                "other_storage is not of type IFamilyDataStorage but of type: {}".format(
                    type(other_storage)
                )
            )

    def _fix_data_types(self, value):
        """
        Replace any ElementId and Byte values with int or string respectively to have JSON working ok.
        Encodes any string in utf-8 and decodes it back to utf-8 to avoid encoding issues.
        Will do the same for list items!

        Any other type of values are not changed.

        :param flattened_dic: Dictionary of which values are to be converted.
        :type flattened_dic: {}
        :return: Dictionary with converted values.
        :rtype: {}
        """

        if isinstance(value, str):
            value = encode_utf8(value)
        elif isinstance(value, System.Byte):
            value = str(value)
        elif isinstance(value, list):
            value = [self._fix_data_types(item) for item in value]

        return value

    def get_data(self):
        """
        Get the data from the object als dictionary.

        Note data type fixing is applied to:

        - ElementIds
        - System.Byte values
        """

        dict = {}
        for key, value in self.__dict__.items():
            dict[key] = self._fix_data_types(value)
        return dict

    def get_data_values_as_list_of_strings(self):
        data_list = []
        for key, value in self.__dict__.items():

            value_updated = "None"
            if isinstance(value, list):
                # check if a value is a list of IFamilyDataStorageUsedBy objects
                # if so convert them to list of json dictionaries
                if len(value) > 0:
                    # check if list of used by instances
                    if isinstance(value[0], IFamilyDataStorageUsedBy):
                        # list of used by instances
                        list_string = [item.to_json() for item in value]
                        value_updated = "[{}]".format(",".join(list_string))
                    else:
                        # list of standard values
                        # encode all values to utf-8
                        # System.Byte to string, ElementId to int
                        value_updated = self._fix_data_types(value)
                        # convert individual values to string
                        list_string = [str(item) for item in value_updated]
                        value_updated = "[{}]".format(",".join(list_string))
            else:
                # encode all values to utf-8
                # System.Byte to string, ElementId to int
                value_updated = self._fix_data_types(value)
                if (
                    isinstance(value_updated, str) == False
                    and isinstance(value_updated, list) == False
                ):
                    value_updated = str(value_updated)

            data_list.append(value_updated)
        return data_list

    def get_property_names(self):
        return self.__dict__.keys()

    def to_json(self):
        """
        Convert the instance of this class to json.

        :return: A Json object.
        :rtype: json
        """

        data_cleaned = self.get_data()
        json_object = json.dumps(
            dict(data_cleaned), indent=None, default=lambda o: o.__dict__
        )
        return json_object
