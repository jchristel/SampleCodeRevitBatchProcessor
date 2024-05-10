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
            value = value.encode("utf-8").decode("utf-8")
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
            # encode all values to utf-8
            # System.Byte to string, ElementId to int
            value_updated = self._fix_data_types(value)
            # convert to string if not already and not a list
            if(isinstance(value_updated, str) == False and isinstance(value_updated, list) == False):
                value_updated = str(value_updated)
            elif(isinstance(value_updated, list)):
                # check if I need to do anything to a list of values...
                # ie. the used by property is a list
                # convert individual values to string
                list_string = [str(item) for item in value_updated]
                value_updated = "[{}]".format(",".join(list_string))
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
