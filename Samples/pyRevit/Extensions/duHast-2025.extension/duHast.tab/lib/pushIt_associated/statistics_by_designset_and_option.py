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


from duHast.Utilities.Objects.result import Result

from families.util.print_table import print_result_table
from pushIt_associated.utils.utilities import (
    get_unique_id_parameter_from_data_file, 
    get_data_path_and_supported_categories, 
    get_family_instances_of_supported_categories,
    sort_families_by_parameter_value,
    sort_families_by_design_set
)

def build_table_data(problematic_keys):
    """
    Build table data to be printed
    :param problematic_keys: dictionary with keys as unique id and values as design set and family instance ids
    :return: list of lists with table data
    """
    
    # build table data to be printed
    table_data = []
    # table to have per row the unique id, design set and family instance id
    for key, value in problematic_keys.items():
        # build new row by unique id, design set and family instances id
        row_data = []

        # add the unique id to the row data
        row_data.append(key)

        # get all design sets for the key
        for design_set, family_instances in value.items():
            row_data.append(design_set)

            # get all family instances for the design set
            fam_instance_ids = []
            for fam_instance in family_instances:
                fam_instance_ids.append(str(fam_instance.Id.IntegerValue))

            # add the family instance ids to the row data as strings so they form one column
            row_data.append(",".join(fam_instance_ids))

            # add the row data to the table data
            table_data.append(row_data)

            # start a new row for the next design set with the same unique id
            row_data = [key]

    return table_data

def push_it_design_set_options_by_id(doc,  uiapp, output, forms):

    # set up a status tracker
    return_value = Result()

    data_path, supported_category_names = get_data_path_and_supported_categories()
    if data_path is None or supported_category_names is None:
        return_value.update_sep(False, "Invalid data path or supported categories")
        return return_value
   
    print("Data path: {}".format(data_path))
    print("Supported categories: {}".format(supported_category_names))
   
    # read the data file and get the first column since it will contain the unique id parameter info by which to sort
    # push it rooms and design options by
    parameter_name, parameter_guid = get_unique_id_parameter_from_data_file(data_path)
    if parameter_name is None or parameter_guid is None:
        return_value.update_sep(False, "Invalid parameter name or guid")
        return return_value
    
    print("Unique ID Parameter name: {}".format(parameter_name))
    print("Unique ID Parameter guid: {}".format(parameter_guid))

    # get supported revit categories
    get_family_instances_result =  get_family_instances_of_supported_categories(doc, supported_category_names)

    # check if we got any family instances
    if not(get_family_instances_result.status):
        return_value.update_sep(False, "No family instances found: {}".format(get_family_instances_result.message))
        print(return_value.message)
        return return_value
    
    # get the family instances
    family_instances = get_family_instances_result.result

    print("Number of family instances: {}".format(len(family_instances)))

    # sort instances by parameter value (unique id)
    sorted_instances = sort_families_by_parameter_value(doc, family_instances,parameter_guid)

    # get he number of keys in sorted instances (this is the number of unique id values)
    keys = sorted_instances.keys()
    print("Number of unique keys in sorted instances: {}".format(len(keys)))

    if len(keys) == 0:
        return_value.update_sep(False, "No sorted instances found")
        print(return_value.message)
        return return_value

    # check if we got any sorted instances are in different design set which may lead to double counting
    problematic_keys =  sort_families_by_design_set(doc, sorted_instances)

    if len(problematic_keys) == 0:
        return_value.update_sep(True, "No problematic keys found.")
        print(return_value.message)
        return return_value
    
    # build table data to be printed
    table_data = build_table_data(problematic_keys)

    # print the table
    print_result_table (output=output, data=table_data,  header=["Unique Id", "Design Set", "Family Instance ID"], table_title="Problematic keys")

    return return_value
