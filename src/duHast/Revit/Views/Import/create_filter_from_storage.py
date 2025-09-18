"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to Revit view filters storage creation from json. 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

#
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


import clr
clr.AddReference('System')
from System.Collections.Generic import List


from duHast.Utilities.Objects.result import Result

from duHast.Revit.Views.Import.read_filter_storage import read_filter_storage_from_file
from duHast.Revit.Views.Utility.convert_data_to_filter_rule import convert_data_to_rule
from duHast.Revit.Views.Utility.convert_data_to_filter_logic_filter import get_logical_filter_class


from Autodesk.Revit.DB import (
    ElementFilter,
    ElementParameterFilter,
    FilterRule,
)


def import_rules_from_data(doc, data_rules):

    # set up a status tracker
    return_value = Result()

    # container for new rules
    element_parameter_filters = List[ElementFilter]()

    # loop over filters in logic container and convert to revit filter rules
    for filter in  data_rules.view_filter_rules:

        return_value.append_message("...Importing filter: {}".format(filter.parameter_name))

        conversion_result = convert_data_to_rule(doc, filter)
        
        if conversion_result.status:
            return_value.append_message("...Successfully converted filter: {}".format(filter.parameter_name))
            
            # rules need to be added to an ElementParameterFilter object which in turns get added to the logic container
            # convert python list to c# list
            rules_net =  List[FilterRule]()

            for rule in conversion_result.result:
                rules_net.Add(rule)
            
            # create the element parameter filter using rules provided
            element_parameter_filter = ElementParameterFilter(rules_net)

            # add to container
            element_parameter_filters.Add(element_parameter_filter)
            
        else:
            return_value.update_sep(False, "...Failed to convert filter: {}. Error: {}".format(filter.parameter_name, conversion_result.message))


    return_value.result.append(element_parameter_filters)
    return return_value


def import_logic_container_from_data(doc, data_object):

    # get the logic container at the top of the tree:
    logic_container = data_object.logic_container
    if logic_container is None:
        return_value.append_message("No logic container found. Skipping view filter: {}".format(data_object.name))
        continue

    if len(logic_container.view_filter_rules) == 0:
        return_value.append_message("No filter rules found. Skipping view filter: {}".format(data_object.name))
        continue
    
    # get the logic filter class
    logic_filter_class = get_logical_filter_class(logic_container.logic_container_type)
    if not logic_filter_class:
        return_value.update_sep(False, "Failed to get logic filter class for type: {}. Skipping view filter: {}".format(logic_container.logic_container_type, data_object.name))
        continue

    # import the rules
    import_rules_result = import_rules_from_data(doc, logic_container)

    # user feedback
    if not import_rules_result.status:
        return_value.update_sep(False, "Failed to import rules for view filter: {}. Error: {}".format(data_object.name, import_rules_result.message))
    else
        return_value.append_message("Successfully imported {} rules for view filter: {}".format(len(import_rules_result.result[0]), data_object.name))

    # import the rules
    import_rules_result = import_rules_from_data(doc, logic_container)

    # user feedback
    if not import_rules_result.status:
        return_value.update_sep(False, "Failed to import rules for view filter: {}. Error: {}".format(data_object.name, import_rules_result.message))
    else
        return_value.append_message("Successfully imported {} rules for view filter: {}".format(len(import_rules_result.result[0]), data_object.name))
    
    # container for new rules
    element_parameter_filters = List[ElementFilter]()

    # transfer rules across
    for entry in import_rules_result.result[0]:
        element_parameter_filters.Add(entry)

    # check for nested logic containers
    if len(logic_container.logic_containers) == 0:
        return_value.append_message("No nested logic containers found.")
    else:
        for entry in logic_container.logic_containers:
            return_value.append_message("Importing nested logic container of type: {}".format(entry.logic_container_type))
            # import the nested logic container
            import_nested_logic_result = import_logic_container_from_data(doc, entry)
            if not import_nested_logic_result.status:
                return_value.update_sep(False, "Failed to import nested logic container for view filter: {}. Error: {}".format(data_object.name, import_nested_logic_result.message))
                # check if any rules were imported
                if len(import_nested_logic_result.result) > 0:
                    for entry in import_nested_logic_result.result[0]:
                        element_parameter_filters.Add(entry)
            else:
                return_value.append_message("Successfully imported {} rules for nested logic container for view filter: {}".format(len(import_nested_logic_result.result[0]), data_object.name))
                # add the imported rules to the main container
                for entry in import_nested_logic_result.result[0]:
                        element_parameter_filters.Add(entry)
    
    return_value.result.append(element_parameter_filters)

    return return_value
    

def import_view_filters_from_data(doc, json_object)

    # set up a status tracker
    return_value = Result()

    # loop over json objects and create view filters
    for data_object in data_objects:
        return_value.append_message("Importing view filter: {}".format(data_object.name))
        
        # get the container and all its nested items
        container = import_logic_container_from_data(doc, data_object)

        # set up a view filter

    
    return return_value
                   