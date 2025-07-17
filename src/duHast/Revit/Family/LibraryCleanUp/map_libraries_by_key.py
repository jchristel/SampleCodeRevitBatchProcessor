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
import os

from duHast.Utilities.Objects.result import Result
from duHast.Utilities.files_xml import get_all_xml_files_from_directories
from duHast.Revit.Family.family_types_get_data_from_xml import get_family_type_data_from_library
from duHast.Revit.Family.Data.Objects.family_directive_swap_instances_of_type import FamilyDirectiveSwap

def get_family_data_from_file(libraryPath):
    """
    Extracts family type data from XML files in the specified library path.

    :return:
        Result class instance.

        - result.status: XML conversion status will be returned in result.status. False if an exception occurred, otherwise True.
        - result.message will contain which xml file was read and converted into family type data.
        - result.result will be [:class:`FamilyTypeDataStorageManager`]

        On exception

        - Reload.status (bool) will be False
        - Reload.message will contain the exception message
        - Reload.result will be an empty list

    :rtype: :class:`.Result`
    """
    xml_files =  get_all_xml_files_from_directories([libraryPath])

    if len(xml_files) == 0:
        return None
    
    family_data_result = get_family_type_data_from_library(xml_files)
    
    return family_data_result.result


def find_matches_by_key (family_target_data, family_source_data, library_target_key_parameter_name, library_source_key_parameter_name,output):

    return_value = Result()

    key_to_families_mapper = {}

    # loop over source library data and check if key parameter exists in source family 
    for family_source in family_source_data:

        # check if  FamilyTypeDataStorageManager has the key parameter
        for fam_source_type in family_source.family_type_data_storage:

            match_found = False

            key_source_parameter = fam_source_type.get_parameter_by_name( library_source_key_parameter_name)
            if key_source_parameter is None:
                output("Key parameter '{}' not found in source family '{}' type: {}.".format(library_source_key_parameter_name, family_source.family_name, fam_source_type.family_type_name))
                continue

            # get the key value from the source family type
            source_key_value =  key_source_parameter.value
        
            # loop over target library data and check if key parameter exists in target family
            for family_target in family_target_data:
                # check if  FamilyTypeDataStorageManager has the key parameter
                for fam_target_type in family_target.family_type_data_storage:
                    key_target_parameter = fam_target_type.get_parameter_by_name(library_target_key_parameter_name)

                    if key_target_parameter is None:
                        output("Key parameter '{}' not found in target family '{}' type: {}.".format(library_target_key_parameter_name, family_target.family_name, fam_target_type.family_type_name))
                        continue
                
                    # get the key value from the source family type
                    target_key_value =  key_target_parameter.value
                
                    # if the key values match add to result
                    if source_key_value == target_key_value:
                        key_to_families_mapper[source_key_value] = (fam_source_type, fam_target_type)
                        match_found = True
                        break  # break to avoid multiple matches for the same source key value
                
                # get out of this loop too
                if match_found:
                    break

    
    return_value.update_sep(True, "Found {} matches by key.".format(len(key_to_families_mapper)))
    return_value.result.append(key_to_families_mapper)
    return return_value


def map_libraries_by_keys(library_target_report_path, library_source_report_path, library_target_key_parameter_name, library_source_key_parameter_name,output):

    """
    Maps libraries by keys from the target and source report paths.

    :param library_target_report_path: Path to the target library report.
    :param library_source_report_path: Path to the source library report.
    :return: A dictionary mapping keys to their corresponding libraries.
    """
    
    return_value = Result()

    if not os.path.exists(library_target_report_path):
        return_value.update_sep(False, "Target report path does not exist: {library_target_report_path}".format(library_target_report_path=library_target_report_path))
        return return_value

    if not os.path.exists(library_source_report_path):
        return_value.update_sep(False, "Source report path does not exist: {library_source_report_path}".format(library_source_report_path=library_source_report_path))
        return return_value

    # Initialize a dictionary to hold the mapping
    

    family_data_target = get_family_data_from_file(library_target_report_path)
    if (family_data_target is None):
        return_value.update_sep(False, "No family data found in the specified library path.")
        output("No family data found in the specified library path: {}".format(library_target_report_path))
        return return_value

    family_data_source = get_family_data_from_file(library_source_report_path)
    if (family_data_source is None):
        return_value.update_sep(False, "No family data found in the specified library path.")
        output("No family data found in the specified library path: {}".format(library_source_report_path))
        return return_value
    

    library_map_result = find_matches_by_key(family_data_target, family_data_source, library_target_key_parameter_name, library_source_key_parameter_name, output)
    if (library_map_result.status is False):
        return_value.update_sep(False, "Error finding matches by key: {}".format(library_map_result.message))
        return return_value
    
    # get the result dictionary from the library_map_result
    library_map = library_map_result.result[0]

    if len(library_map) == 0:
        return_value.update_sep(False, "No matches found between the libraries.")
        output("No matches found between the libraries.")
        return return_value

    output("Found {} matches between the libraries.".format(len(library_map)))

    return_value.result.append(library_map)
    return_value.update_sep(True, "Libraries mapped successfully.")
    return return_value


def convert_mapping_to_swap_directives(mapping):
    """
    Converts the mapping of libraries to swap directives.

    :param mapping: The mapping of libraries.
    :return: A list of swap directives.
    """
    swap_directives = []
    
    for key, (source_family, target_family) in mapping.items():
        swappy = FamilyDirectiveSwap(
            name=source_family.family_name,
            category=source_family.root_category_path,
            source_type_name=source_family.family_type_name,
            target_family_name=target_family.family_name,
            target_family_type_name=target_family.family_type_name
        )
        swap_directives.append(swappy)
    
    if len(swap_directives) == 0:
        raise Exception("No swap directives created from the mapping.")
    

    
    return swap_directives