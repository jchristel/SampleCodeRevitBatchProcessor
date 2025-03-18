"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A module with helper function around family types catalogue files.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Family types can be filtered ( removed from the export ) by providing a list of filters.
For available filters see the documentation in the module duHast.Utilities.compare alternatively inline filters can be provided as lambda functions.

 filters = [[lambda x, y: x.startswith(y), "A"], [lambda x, y: x.endswith(y), "B"]]

The filters are applied to the family type names ( x in the above examples ). If the type name passes all filters it will be added to the catalogue file.


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


import os
import csv

from duHast.Revit.Family.family_types_get_data_from_xml import get_type_data_via_XML_from_family_file
from duHast.Revit.Family.family_parameter_utils import  get_family_type_parameters,  filter_parameters_by_formula_driven
from duHast.Revit.Family.Data.Objects.family_type_data_storage_manager import FamilyTypeDataStorageManager

from duHast.Utilities.Objects.result import Result
from duHast.Utilities.files_io import get_file_name_without_ext, get_directory_path_from_file_path,file_exist
from duHast.Utilities.files_csv import write_report_data_as_csv
from duHast.Utilities.Objects.file_encoding_bom import BOMValue


def type_name_passes_filters(fam_type, filters):

    """
    Check if the family type name passes the filters.

    :param fam_type: The family type to check.
    :type fam_type: FamilyTypeDataStorage
    :param filters: The filters to apply to the types to be added to the catalogue file. If None, no filters will be applied and all types will be added. If more then one filter is provided, the types must pass all filters
    :type filters: list(list(function(value1,value2), test_value))

    :return: True if the type name passes all filters, False otherwise.
    :rtype: bool
    """

    # check if filters are None
    if filters is None:
        return True
    
    # go over filters and check if the type passes all filters by type name
    passes_filter = True

    for filter_instance in filters:

        # do some sanity checks
        if not isinstance(filter_instance, list):
            return False

        if len(filter_instance) != 2:
            return False

        # get the filter function
        filter_func = filter_instance[0]
        filter_value = filter_instance[1]

        # check if the filter function is callable
        if not callable(filter_func):
            return False

        # check if the type name passes the filter
        passes_filter = passes_filter and filter_func(fam_type.family_type_name, filter_value)

    return passes_filter

   
def pass_fam_types_through_filters(fam_type_manager, filters):
    """
    Pass family types through filters.

    :param fam_type_manager: The family type manager to pass through the filters.
    :type fam_type_manager: FamilyTypeDataStorageManager
    :param filters: The filters to apply to the types to be added to the catalogue file. If None, no filters will be applied and all types will be added. If more then one filter is provided, the types must pass all filters
    :type filters: list(list(function(value1,value2), test_value))
    
    :return: The updated family type manager.
    :rtype: FamilyTypeDataStorageManager
    """

    return_value = Result()

    try:
        # loop over filters
        for filter_instance in filters:

            # do some sanity checks
            if not isinstance(filter_instance, list):
                return_value.update_sep(False, "Filter is not a list: {}".format(filter_instance))
                continue

            if len(filter_instance) != 2:
                return_value.update_sep(False, "Filter does not contain two elements: {}".format(filter_instance))
                continue

            # get the filter function
            filter_func = filter_instance[0]

            # check if the filter function is callable
            if not callable(filter_func):
                return_value.update_sep(False, "Filter function is not callable: {}".format(filter_func))
                continue
        
            # loop over family types and remove types not passing filters
            for fam_type_storage in fam_type_manager.family_type_data_storage:
                if (not type_name_passes_filters( fam_type_storage, filters)):
                    removed_type_flag = fam_type_manager.remove_family_type( fam_type_storage.family_type_name)
                    return_value.update_sep( removed_type_flag, "Removed family type: {} with status: {}".format(fam_type_storage.family_type_name, removed_type_flag))
                else:
                    return_value.append_message(True, "Family type: {} passed filters.".format(fam_type_storage.family_type_name))

            
            # return the updated family type manager
            return_value.result.append(fam_type_manager)

    except Exception as e:
        return_value.update_sep(False, "Failed to pass family types through filters: {}".format(str(e)))

    return return_value


def get_type_parameter_order(doc, parameter_order):
    """
    Get the type parameter order for the catalogue file.
    
    :param doc: The family document to extract the type data from.
    :type doc: rdb.Family
    
    :param parameter_order: The order of the parameters in the catalogue file. If None, the parameters will be ordered alphabetically.
    :type parameter_order: list(str)
    
    :return: The type parameter order for the catalogue file with the result class .result property
    :rtype: Result
    """

    return_value = Result()
    
    try:
        # get list of parameters to export ( remove any type driven parameters governed by a formula)
        # get type parameters
        type_parameters = get_family_type_parameters(doc)

        # check if the type parameters are valid
        if type_parameters is None or len(type_parameters) == 0:
            return_value.update_sep(False, "Failed to get the family type parameters.")
            return return_value
        
        # filter out formula driven parameters
        type_parameters_filtered = filter_parameters_by_formula_driven(type_parameters, False)

        # check if the filtered type parameters are valid
        if type_parameters_filtered is None or len(type_parameters_filtered) == 0:
            return_value.update_sep(False, "Filter formula driven parameters removed all parameters from the set.")
            return return_value
        
        # get the parameter order
        if parameter_order is None:
            return_value.result = sorted([param.Definition.Name for param in type_parameters_filtered])
        else:
            family_parameter_names_sorted =  sorted([param.Definition.Name for param in type_parameters_filtered])
            for para_name in parameter_order:
                if para_name not in family_parameter_names_sorted:
                    return_value.append_message("Parameter {} not found in type parameters.".format(para_name))
                else:
                    return_value.result.append(para_name)
                    # remove that parameter from the list
                    family_parameter_names_sorted.remove(para_name)
            # check if any parameters are left
            if len(family_parameter_names_sorted) > 0:
                # add the rest of the parameters
                return_value.result = return_value.result + family_parameter_names_sorted

    except Exception as e:
        return_value.update_sep(False, "Failed to setup parameter order: {}".format(str(e)))

    return return_value


def write_catalogue_file_to_csv(catalogue_file_data, family_file_path, header, override_existing = False):
    """
    Write the catalogue file to disk.

    :param catalogue_file_data: The catalogue file data to write to disk.
    :type catalogue_file_data: list(list(str))
    :param family_file_path: The path to the family file.
    :type family_file_path: str
    :param override_existing: If True, the existing catalogue file will be overwritten. If False, no catalogue file will be exported.
    :type override_existing: bool

    :return: The result of the write operation.
    :rtype: Result
    """

    return_value = Result()

    try:
        # build the catalogue file path
        catalogue_file_directory = get_directory_path_from_file_path( family_file_path)
        catalogue_file_path_name = "{}.txt".format(get_file_name_without_ext( family_file_path))
        catalogue_file_full_path = os.path.join(catalogue_file_directory, catalogue_file_path_name)

        # check if the file already exists
        if file_exist(catalogue_file_full_path) and not override_existing:
            return_value.update_sep(False, "Catalogue file already exists and override_existing is False.")
            return return_value
        
        # write the catalogue file to disk
        write_result = write_report_data_as_csv(
            file_name=catalogue_file_full_path,
            header=header, 
            data= catalogue_file_data,
            encoding="utf-16-le",
            bom=BOMValue.UTF_16_LITTLE_ENDIAN, 
            quoting=csv.QUOTE_MINIMAL
        )

        return_value.update(write_result)
        
    except Exception as e:
        return_value.update_sep(False, "An exception occurred when trying to write catalogue file to disk: {}".format(e))

    return return_value


def export_catalogue_file(doc, file_path = None, filters = None, parameter_order = None, override_existing = False):
    """
    Export the family types catalogue file.

    :param doc: The family document to extract the type data from.
    :type doc: rdb.Family
    :param file_path: The path to save the catalogue file. If None, the file will be saved in the same location as the family with the same name as the family.
    :type file_path: str
    :param filters: 
        
            The filters to apply to the types to be added to the catalogue file. If None, no filters will be applied and all types will be added. If more then one filter is provided, the types must pass all filters to be added.
            Filter format:

                [[func(family_type_name, filter value), "my check value"],...]
            
            Example:
                filters = [[lambda x, y: x.startswith(y), "A"], [lambda x, y: x.endswith(y), "B"]]

    :type filters: list(function(value1,value2))
    :param parameter_order: The order of the parameters in the catalogue file. If None, the parameters will be ordered alphabetically.
    :param override_existing: If True, the existing catalogue file will be overwritten. If False, no catalogue file will be exported.
    """

    return_value = Result()

    try:

        # check if a family document...
        if not doc.IsFamilyDocument:
            return_value.update_sep(False, "The document is not a family document.")
            return return_value

        # get the family name
        family_name = doc.Title

        # remove the file extension
        if family_name.lower().endswith(".rfa"):
            family_name = family_name[:-4]

        # get the family path
        family_path = doc.PathName

        # check if the file path is provided
        if file_path:
            file_path= family_path

        # get the family type data
        family_type_data_result = get_type_data_via_XML_from_family_file(doc.Application, family_name, family_path)

        # check if the family type data was successfully extracted
        if not family_type_data_result.status:
            return_value.update_sep(False, "Failed to get the family type data: {}".format(family_type_data_result.message))
            return return_value
        
        if family_type_data_result.result is None or len(family_type_data_result.result) == 0:
            return_value.update_sep(False, "No family type data was extracted.")
            return return_value
        
        # get the family type data
        fam_type_manager = family_type_data_result.result[0]

        if not isinstance(fam_type_manager, FamilyTypeDataStorageManager):
            return_value.update_sep(False, "Failed to get the family type manager. Got {} instead.".format(type(fam_type_manager)))
            return return_value
        
        # check if family has any types
        if not fam_type_manager.family_has_types:
            return_value.update_sep(False, "No family types found in family.")
            return return_value

        # go over filters and remove types that do not pass the filter
        if filters is not None:

            # attempt to pass family types through filters
            fam_type_manager_filter_result = pass_fam_types_through_filters(fam_type_manager, filters)

            # check if the family types passed through the filters
            if (not fam_type_manager_filter_result.status):
                # if not get out
                return_value.update_sep(False, "Failed to pass family types through filters: {}".format(fam_type_manager_filter_result.message))
                return return_value
        

        # get the parameter order for the catalogue file
        # this will also remove any type parameters that are formula driven
        type_parameter_order_result = get_type_parameter_order(doc, parameter_order)
    
        if not type_parameter_order_result.status:
            return_value.update_sep(False, "Failed to get the type parameter order: {}".format(type_parameter_order_result.message))
            return return_value
        
        # get the type parameter order
        type_parameter_order = type_parameter_order_result.result

        # export the catalogue file       
        catalogue_file_data = fam_type_manager.get_catalogue_file_data(type_parameter_order)

        # check if the catalogue file data is valid
        if catalogue_file_data is None or len(catalogue_file_data) == 0:
            return_value.update_sep(False, "Failed to get the catalogue file data.")
            return return_value

        # build the header
        catalogue_file_header = fam_type_manager.get_catalogue_file_header_row(type_parameter_order)

        # check if header is valid
        if catalogue_file_header is None or len(catalogue_file_header) == 0:
            return_value.update_sep(False, "Failed to get the catalogue file header.")
            return return_value

        print("Catalogue file data: {}".format(catalogue_file_data))
        print("Catalogue file header: {}".format(catalogue_file_header))
        print("Catalogue file path: {}".format(family_path))
        print("Override existing: {}".format(override_existing))

        # write the catalogue file to file
        write_catalogue_file_result = write_catalogue_file_to_csv(
            catalogue_file_data=catalogue_file_data, 
            header=catalogue_file_header,
            family_file_path= family_path, 
            override_existing=override_existing
        )

        # check if the write was successful
        if not write_catalogue_file_result.status:
            return_value.update_sep(False, "Failed to write the catalogue file to file: {}".format(write_catalogue_file_result.message))
            return return_value

        return_value.update_sep(True, "Catalogue file successfully exported to: {}".format(write_catalogue_file_result.message))

    except Exception as e:
        return_value.update_sep(False, str(e))

    return return_value
    