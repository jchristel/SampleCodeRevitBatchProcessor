"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Class for family parameter data storage class.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Used to store values of family parameters by family type.

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


from duHast.Utilities.Objects.base import Base
from duHast.Revit.Family.Data.Objects import ifamily_data_storage as IFamDataStorage

class FamilyTypeParameterDataStorage(IFamDataStorage.IFamilyDataStorage):

    # data type for this class ( used in reports as first entry per row )
    data_type = "FamilyTypeParameter"

    unit_type_compare_values_as_floats = [
        "Length",
        "Area",
        "Angle",
        "Currency",
        "Flow",
    ]

    # number of properties in this class ( used in report reader function )
    number_of_properties = 10

    def __init__(self, 
            root_name_path,
            root_category_path,
            family_name,
            family_file_path,
            family_type_name,
            name, 
            type, 
            type_of_parameter, 
            units, 
            value
        ):
        """
        constructor

        :param root_name_path: root name path (i.e. rootFamilyName :: nestedFamilyNameOne :: nestedFamilyTwo)
        :type root_name_path: str
        :param root_category_path: root category path (i.e. rootCategoryName :: nestedCategoryNameOne :: nestedCategoryTwo)
        :type root_category_path: str
        :param family_name: name of the family
        :type family_name: str
        :param family_file_path: file path of the family
        :type family_file_path: str
        :param name: name of the family parameter
        :param type: type of the parameter ( i.e. shared, system, custom)
        :param type_of_parameter: unit type of the parameter ( i.e. length, area, volume, string, etc.)
        :param units: units of the parameter, i.e. mm ( there are parameter type which do not have units i.e. string)
        :param value: value of the parameter
        """

        super(FamilyTypeParameterDataStorage, self).__init__(
            data_type=FamilyTypeParameterDataStorage.data_type,
            root_name_path=root_name_path,
            root_category_path=root_category_path,
            family_name=family_name,
            family_file_path=family_file_path,
        )

        self.family_type_name = family_type_name  # name of the family type
        self.name = name  # name of the family type
        self.type = type  # type of the parameter ( i.e. shared, system, custom)
        self.type_of_parameter = type_of_parameter  # unit type of the parameter ( i.e. length, area, volume, string, etc.)
        self.units = units  # units of the parameter ( there are parameter type which do not have units i.e. string)
        self.value = value  # value of the parameter
        self.value_as_float = None

        # attempt to convert value to float if possible
        if self.type_of_parameter in self.unit_type_compare_values_as_floats:
            try:
                self.value_as_float = float(self.value)
            except Exception:
                self.value_as_float = None
          

    def __eq__(self, other):
        """
        equal compare

        :param other: object to compare with
        :return: True if equal, False if not
        """

        if not isinstance(other, FamilyTypeParameterDataStorage):
            raise ValueError("other must be an instance of FamilyTypeParameterDataStorage")
        
        # compare values as floats if the type of parameter is in the list of unit types
        # that should be compared as floats and the value as float is not None
        if self.type_of_parameter in self.unit_type_compare_values_as_floats and self.value_as_float is not None:
            return (
                self.data_type == other.data_type and
                self.name == other.name and
                self.type == other.type and
                self.type_of_parameter == other.type_of_parameter and
                self.units == other.units and
                self.value_as_float == other.value_as_float
            )
        else:
            # compare values as strings
            return (
                self.data_type == other.data_type and
                self.name == other.name and
                self.type == other.type and
                self.type_of_parameter == other.type_of_parameter and
                self.units == other.units and
                self.value == other.value
            )

    def __ne__(self, other):
        """
        not equal compare

        :param other: object to compare with
        :return: True if not equal, False if equal
        """
        return not self.__eq__(other)

    def __hash__(self):
        """
        hash function for this class

        :return: hash value
        """

        return hash(
            (
                self.data_type,
                self.name,
                self.type,
                self.type_of_parameter,
                self.units,
                self.value,
                self.value_as_float,
            )
        )

    def get_difference(self, other):
        """
        get the difference between this object and another object

        :param other: object to compare with
        :return: a list of differences
        :rtype: [str]
        """

        if not isinstance(other, FamilyTypeParameterDataStorage):
            return NotImplemented

        differences = []

        if self.name != other.name:
            differences.append("name: {} != {}".format(self.name, other.name))
        if self.type != other.type:
            differences.append("type: {} != {}".format(self.type, other.type))
        if self.type_of_parameter != other.type_of_parameter:
            differences.append(
                "type_of_parameter: {} != {}".format(
                    self.type_of_parameter, other.type_of_parameter
                )
            )
        if self.units != other.units:
            differences.append("units: {} != {}".format(self.units, other.units))
        
        # check if values need to be compared as floats
        if self.type_of_parameter in self.unit_type_compare_values_as_floats and self.value_as_float is not None and other.value_as_float is not None:
            # compare values as floats
            if self.value_as_float != other.value_as_float:
                differences.append("value: {} != {}".format(self.value_as_float, other.value_as_float))
        else:
            # compare values as strings
            if self.value != other.value:
                differences.append("value: {} != {}".format(self.value, other.value))

        return differences

    def get_report_data(self):
        """
        get the report data for this object

        :return: the report data
        :rtype: [str]
        """

        return [
            self.name,
            self.type,
            self.type_of_parameter,
            self.units,
            self.value,
        ]
    
    def get_catalogue_file_data(self):
        """
        Get the catalogue file data for this parameter ( the value of the parameter)

        :return: the catalogue file data
        :rtype: [str]
        """

        return self.value
    
    def get_catalogue_file_header_row(self):
        """
        Get the catalogue file header row for this object sample ParameterName##LENGTH##MILLIMETERS

        :return: the catalogue file header row entry for this parameter
        :rtype: str
        """

        type_name_revised_for_file = self.type_of_parameter.upper()

        # some type names change to more generic names for the catalogue file
        if self.type_of_parameter == "Text" or self.type_of_parameter == "Yes/No" or self.type_of_parameter == "Material" or self.type_of_parameter == "Image" or self.type_of_parameter == "FamilyType":
            type_name_revised_for_file = "OTHER"

        # some unit names change to more generic names for the catalogue file
        unit_names_for_catalogue_file = self.units.upper()
        if self.units == "unitless":
            unit_names_for_catalogue_file =""
        elif self.units == "mm":
            unit_names_for_catalogue_file = "MILLIMETERS"
        elif self.units == "m":
            unit_names_for_catalogue_file = "METERS"


        return "{}##{}##{}".format(self.name, type_name_revised_for_file, unit_names_for_catalogue_file)