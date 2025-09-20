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
from Autodesk.Revit.DB import Element, WorksharingUtils

from pushIt_associated.utils.utilities import (
    get_unique_id_parameter_from_data_file, 
    get_data_path_and_supported_categories, 
    get_family_instances_of_supported_categories,
    sort_families_by_parameter_value,
)

from families.util.print_table import print_result_table

def get_families_user_data_stats(doc, sorted_instances):
    """
    This function will get the user data for the families in the document.
    :param doc: the document
    :param sorted_instances: the sorted instances
    :return: a dictionary with the family name as key and the list of family instance ids as value
    """

    stats = {}
    stats_creators = {}
    stats_owners = {}

    for key, family_instances in sorted_instances.items():
        for c in family_instances:
            fam_name = Element.Name.GetValue(c.Symbol.Family)
            if not fam_name in stats:
                stats[fam_name] = []
            stats[fam_name].append(c.Id.Value)


            # get the user name
            info = WorksharingUtils.GetWorksharingTooltipInfo(doc, c.Id)

            creator =  info.Creator
            owner = info.Owner

            if creator not in stats_creators:
                stats_creators[creator] = 0
            
            stats_creators[creator] += 1

            if owner not in stats_owners:
                stats_owners[owner] = 0
            
            stats_owners[owner] += 1
    
    return stats, stats_creators, stats_owners



def basic_stats_entry(doc,  uiapp, output, forms):
    """
    This function will give you a basic statistics of the elements in the document.
    """

    # set up a status tracker
    return_value = Result()

    data_path, supported_category_names = get_data_path_and_supported_categories()
    if data_path is None or supported_category_names is None:
        return_value.update_sep(False, "Invalid data path or supported categories")
        return return_value
    
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

    # sort families by user data
    stats, stats_creators, stats_owners = get_families_user_data_stats(doc, sorted_instances)

    # check if there are any elements in the document
    if len(stats) == 0:
        print("No PushIt elements found in the document.")
        return_value.update_sep(True,"No PushIt elements found in the document.")
        return return_value
    
    # reformat data for printing
    
    # by family name
    data = []
    # get the list of keys sorted by family name
    keys = sorted(stats.keys())
    # iterate over the keys and get the data
    for key in keys:
        data.append([key, len(stats[key])])
    # print the data
    print_result_table(output=output, data=data, header= ["Family Name", "Count"], table_title= "Basic Statistics of PushIt Elements",  max_row_number = 1000)

    # by user data - creators
    data_users = []
    # get the list of keys sorted by family name
    keys = sorted(stats_creators.keys())
    # iterate over the keys and get the data
    for key in keys:
        data_users.append([key, str(stats_creators[key])])
    # print the data
    print_result_table(output=output, data=data_users, header= ["Creator", "Count"], table_title= "Creators of PushIt Elements")

    # by user data - owners
    data_owners = []
    # get the list of keys sorted by family name
    keys = sorted(stats_owners.keys())
    # iterate over the keys and get the data
    for key in keys:
        data_owners.append([key, str(stats_owners[key])])
    # print the data
    print_result_table(output=output, data=data_owners, header= ["Owner", "Count"], table_title= "Owners of PushIt Elements")

    # set the return value
    return_value.update_sep(True,"Successfully processed the elements in the document.")

    return return_value

