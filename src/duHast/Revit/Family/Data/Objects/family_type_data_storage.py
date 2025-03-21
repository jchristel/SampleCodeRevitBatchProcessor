"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Class for family type data storage class.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Used as storage class when retrieving family type data from a family file.

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

from duHast.Revit.Family.Data.Objects import ifamily_data_storage as IFamDataStorage


class FamilyTypeDataStorage(IFamDataStorage.IFamilyDataStorage):

    # data type for this class ( used in reports as first entry per row )
    data_type = "FamilyType"

    # number of properties in this class ( used in report reader function )
    number_of_properties = 8

    def __init__(
        self,
        root_name_path,  # root name path ( most often the same as the family name)
        root_category_path,  # family category
        family_name,  # family name
        family_file_path,  # family file path
        family_type_name,  # family type name
        parameters,  # parameters and there values for this type
        last_updated_date=None,  # last updated date (when was the data retrieved from the family type)
        last_updated_time=None,  # last updated time (when was the data retrieved from the family type)
        **kwargs
    ):
        """
        constructor

        :param root_name_path: root name path ( most often the same as the family name)
        :param root_category_path: family category
        :param family_name: family name
        :param family_file_path: family file path
        :param family_type_name: family type name
        :param parameters: parameters and there values for this type
        :param last_updated_date: last updated date (when was the data retrieved from the family type)
        :param last_updated_time: last updated time (when was the data retrieved from the family type)
        """

        # store args in base class
        super(FamilyTypeDataStorage, self).__init__(
            # data_type=FamilyTypeDataStorage.data_type,
            data_type=FamilyTypeDataStorage.data_type,
            root_name_path=root_name_path,
            root_category_path=root_category_path,
            family_name=family_name,
            family_file_path=family_file_path,
        )

        self._family_type_name = family_type_name
        self._parameters = parameters
        self._last_updated_date = last_updated_date  # last updated date (when was the data retrieved from the family type)
        self._last_updated_time = last_updated_time  # last updated time (when was the data retrieved from the family type)

    @property
    def family_type_name(self):
        return self._family_type_name

    @property
    def parameters(self):
        return self._parameters

    @property
    def last_updated_date(self):
        return self._last_updated_date

    @property
    def last_updated_time(self):
        return self._last_updated_time

    def get_parameter_by_name(self, parameter_name):
        """
        Returns the parameter by its name.

        :param parameter_name: The name of the parameter to retrieve.
        :return: The parameter if found, otherwise None.
        """
        for parameter in self._parameters:
            if parameter.name == parameter_name:
                return parameter
        return None

    def __eq__(self, other):
        """
        equal compare (ignores last updated date and time)

        :param other: object to compare with
        :return: True if equal, False if not
        """

        if not isinstance(other, FamilyTypeDataStorage):
            return NotImplemented
        return (
            self.data_type == other.data_type,
            self.root_name_path == other.root_name_path,
            self.root_category_path == other.root_category_path,
            self.family_name == other.family_name,
            self.family_file_path == other.family_file_path,
            self.family_type_name == other.family_type_name,
            self.parameters == other.parameters,
        )

    def __ne__(self, other):
        """
        not equal compare (ignores last updated date and time)

        :param other: object to compare with
        :return: True if not equal, False if equal
        """
        return not self.__eq__(other)

    def __hash__(self):
        """
        hash function for this class (ignores last updated date and time)

        :return: hash value
        """

        return hash(
            (
                self.data_type,
                self.root_name_path,
                self.root_category_path,
                self.family_name,
                self.family_file_path,
                self.family_type_name,
                self.parameters,
            )
        )

    def is_match_by_names_and_category(self, other):
        """
        check if this object is a match with another object by family name and category
        ignores:

        - last updated date and time
        - parameters
        - family file path

        :param other: object to compare with
        :return: True if match, False if not
        """

        if not isinstance(other, FamilyTypeDataStorage):
            return False

        return (
            self.root_name_path == other.root_name_path
            and self.root_category_path == other.root_category_path
            and self.family_name == other.family_name
            and self.family_type_name == other.family_type_name
        )

    def get_comparison_report_parameter_values(self, other, ignore_property_names=[]):
        """
        get the difference between this object and another family type data storage object in terms of parameter values only
        Assumes that the objects are equal in terms of family name, family type name, root name path and root category path

        :param other: object to compare with
        :return: list of properties that are different
        """

        if not isinstance(other, FamilyTypeDataStorage):
            return NotImplemented

        return_list = []

        # repeats per parameter difference
        diff_base = [
            self.family_name,
            self.root_category_path,
            "Found match in library",
            self.family_type_name,
            "Found match in library",
        ]

        for param in self.parameters:
            param_other = other.get_parameter_by_name(param.name)
            if param_other is None:
                # parameter not found in other object
                diff_parameter = [param.name, "No match in library"]
                return_list.append(diff_base + diff_parameter)
            else:
                if param != param_other and param.name not in ignore_property_names:
                    para_diff = param.get_difference(param_other)
                    for single_difference in para_diff:
                        # write each difference as a separate entry
                        parameter_diff_entry = [
                            param.name,
                            "Found match in library",
                            single_difference,
                        ]
                        return_list.append(diff_base + parameter_diff_entry)

        return return_list

    def get_difference(self, other, ignore_property_names=[]):
        """
        get the difference between this object and another family type data storage object

        :param other: object to compare with
        :return: list of properties that are different
        """

        if not isinstance(other, FamilyTypeDataStorage):
            return NotImplemented

        # holds all the differences per para
        diff = []

        # should return a list with an entry for each difference
        # if no differences are found the list should be empty

        if (
            self.data_type != other.data_type
            and "data_type" not in ignore_property_names
        ):
            diff.append("data_type: {} != {}".format(self.data_type, other.data_type))

        if (
            self.root_name_path != other.root_name_path
            and "root_name_path" not in ignore_property_names
        ):
            diff.append(
                "root_name_path: {} != {}".format(
                    self.root_name_path, other.root_name_path
                )
            )

        if (
            self.root_category_path != other.root_category_path
            and "root_category_path" not in ignore_property_names
        ):
            diff.append(
                "root_category_path: {} != {}".format(
                    self.root_category_path, other.root_category_path
                )
            )

        if (
            self.family_name != other.family_name
            and "family_name" not in ignore_property_names
        ):
            diff.append(
                "family_name: {} != {}".format(self.family_name, other.family_name)
            )

        if (
            self.family_file_path != other.family_file_path
            and "family_file_path" not in ignore_property_names
        ):
            diff.append(
                "family_file_path: {} != {}".format(
                    self.family_file_path, other.family_file_path
                )
            )

        if (
            self.family_type_name != other.family_type_name
            and "family_type_name" not in ignore_property_names
        ):
            diff.append(
                "family_type_name: {} != {}".format(
                    self.family_type_name, other.family_type_name
                )
            )

        # compare parameters by their names
        # if a match is found compare the values

        for param in self.parameters:
            param_other = other.get_parameter_by_name(param.name)
            if param_other is None:
                diff.append("parameter {} not found in other object".format(param.name))
            else:
                if param != param_other and param.name not in ignore_property_names:
                    para_diff = param.get_difference(param_other)
                    for single_difference in para_diff:
                        diff.append(
                            "parameter {} is different: {}".format(
                                param.name, single_difference
                            )
                        )
                else:
                    pass
                    # diff.append("parameter {} is equal. {}".format(param.name, para_diff))

        return diff


    def get_report_data(self, file_name=None):
        """
        get the data for the report

        :param file_name: name of the file the data was retrieved from
        :type file_name: str
        :return: list of data for the report
        """

        data = []
        
        for param in self.parameters:
            # get the report data for the parameter
            para_report_data = param.get_report_data()
            
            # add the file name if available
            if file_name is None:
                file_name = "N/A"
            
            # build the default type information repeated for each parameter
            def_report_data = [
                file_name,
                self.family_name,
                self.root_category_path,
                self.family_type_name,
                self.last_updated_date,
                self.last_updated_time,
            ]

            index = len(def_report_data)
            # add the parameter report data to the default type information
            def_report_data[index:index] = para_report_data

            # append the data to the list
            data.append(def_report_data)
        return data
    

    def get_catalogue_file_data(self, parameter_names=None):
        """
        Get the data for the catalogue file

        :param parameter_names: list of parameter names to include in the catalogue file and their order
        :type parameter_names: [str]
        :return: list of data for the catalogue file
        """

        data = []
        
        if parameter_names is None:
            for param in self.parameters:
                # get the report data for the parameter
                para_report_data = param.get_catalogue_file_data()
                # append the data to the list
                data.append(para_report_data)
        else:
            for parameter_name in parameter_names:
                param = self.get_parameter_by_name(parameter_name)
                if param is not None:
                    # get the report data for the parameter
                    para_report_data = param.get_catalogue_file_data()
                    # append the data to the list
                    data.append(para_report_data)
                else:
                    # add no data for the parameter
                    pass
                
        # add the type name to the front
        data.insert(0, self.family_type_name)

        return data
    
    def get_catalogue_file_header_row(self, parameter_names):
        """
        Get the header row for the catalogue file

        :param parameter_names: list of parameter names to include in the catalogue file and their order
        :type parameter_names: [str]
        :return: list of data for the catalogue file header row
        """

        # set up a header row with empty entry for the first column
        header_row = [""]

        # add the header row based on the parameter names
        if parameter_names is not None:
            for parameter_name in parameter_names:

                para_storage = self.get_parameter_by_name(parameter_name)
                if para_storage is not None:
                    # get the header row for the parameter
                    para_header_row = para_storage.get_catalogue_file_header_row()
                    # append the data to the list
                    header_row.append(para_header_row)
                else:
                    # add no data for the parameter
                    pass
        else:
            for param in self.parameters:
                # get the header row for the parameter
                para_header_row = param.get_catalogue_file_header_row()
                # append the data to the list
                header_row.append(para_header_row)

        return header_row