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

from duHast.Revit.Views.Utility.convert_data_to_filter_rule import convert_data_to_rule
from duHast.Revit.Views.Utility.convert_data_to_filter_logic_filter import get_logical_filter_class
from duHast.Revit.Views.filters import create_filter, get_all_filters, update_filter


from Autodesk.Revit.DB import (
    Category,
    ElementId,
    ElementFilter,
    ElementParameterFilter,
    FilterRule,
)

DEBUG = False

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


def import_nested_logic_container_from_data(doc, logic_filter_containers):

    # set up a status tracker
    return_value = Result()
    
    try:
        # container for nested container
        element_parameter_filters = List[ElementFilter]()

        for logic_filter_container in  logic_filter_containers:

            # container for nested container
            nested_element_parameter_filters = List[ElementFilter]()

            # get the logic container filter class
            logic_filter_class = get_logical_filter_class(logic_filter_container.logic_container_type)
            
            if not logic_filter_class:
                return_value.update_sep(False, "Failed to get logic filter class for type: {}.".format(logic_filter_container.logic_container_type))
                return return_value
            
            return_value.append_message("Using logic filter class: {} for logic container of type: {}".format(logic_filter_class.__name__, logic_filter_container.logic_container_type))
            
            if DEBUG:
                print("Using logic filter class: {} for logic container of type: {}".format(logic_filter_class.__name__, logic_filter_container.logic_container_type))

            # get the nested logic containers 
            nested_logic_containers = logic_filter_container.logic_containers
            
            # check if there are any nested containers
            if nested_logic_containers is None or len(nested_logic_containers) == 0:
                return_value.append_message("No logic container found. Skipping logic containers...")
            else:
                # recursive call
                import_nested_containers_result = import_nested_logic_container_from_data(doc, nested_logic_containers)

                if not import_nested_containers_result.status:
                    return_value.update_sep(False, "Failed to import nested logic container. Error: {}".format(import_nested_containers_result.message))
                    # check if any rules were imported
                    if len(import_nested_containers_result.result) > 0:
                        for entry in import_nested_containers_result.result[0]:
                            nested_element_parameter_filters.Add(entry)

                else:
                    return_value.append_message("Successfully imported {} rules for nested logic container.".format(len(import_nested_containers_result.result[0])))
                    # add the imported rules to the main container
                    for entry in import_nested_containers_result.result[0]:
                        nested_element_parameter_filters.Add(entry)

            # look at view filter rules at this level
            if len(logic_filter_container.view_filter_rules) == 0:
                return_value.append_message("No filter rules found. Skipping view filter rules...")
                
                if DEBUG:
                    print ("no rules\n")
            else:

                if DEBUG:
                    print ("got rules {}\n".format(len(logic_filter_container.view_filter_rules)))

                # import the rules
                import_rules_result = import_rules_from_data(doc, logic_filter_container)

                # user feedback
                if not import_rules_result.status:
                    return_value.update_sep(False, "Failed to import rules for view filter. Error: {}".format(import_rules_result.message))
                    if DEBUG:
                        print("Failed to import rules for view filter. Error: {}\n".format(import_rules_result.message))
                else:
                    return_value.append_message("Successfully imported {} rules for view filter".format(len(import_rules_result.result[0])))
                    if DEBUG:
                        print("Successfully imported {} rules for view filter\n".format(len(import_rules_result.result[0])))

                
                #element_parameter_filters = List[ElementFilter]()

                # transfer rules across
                for entry in import_rules_result.result[0]:
                    if DEBUG:
                        print("adding rule {}\n".format(entry))
                    nested_element_parameter_filters.Add(entry)
                
                # user feedback
                if DEBUG:
                    print("imported rules {}\n".format(nested_element_parameter_filters.Count))


            try:
                # create the logic container class instance
                logic_container_class_instance = logic_filter_class(nested_element_parameter_filters)
                element_parameter_filters.Add(logic_container_class_instance)
                return_value.append_message("Successfully created logic container of type: {}".format(logic_filter_container.logic_container_type))
                if DEBUG:
                    print("Successfully created logic container of type: {}\n".format(logic_filter_container.logic_container_type))
            except Exception as e:
                return_value.update_sep(False, "Failed to create logic container of type: {}. Error: {}".format(logic_filter_container.logic_container_type, e))
                if DEBUG:
                    print("Failed to create logic container of type: {}. Error: {}\n".format(logic_filter_container.logic_container_type, e))

        
        # add the overall list to the return value
        return_value.result.append(element_parameter_filters)
    except Exception as e:
        return_value.update_sep(False, "Failed to import nested logic container. Error: {}".format(e))

    return return_value
    


def import_root_logic_container_from_data(doc, view_filter_json):

    # set up a status tracker
    return_value = Result()
    
    try:
        return_value.append_message("Importing root logic container for view filter: {}".format(view_filter_json.name))
        
        # get the logic containers at the top of the tree
        logic_filter_container = view_filter_json.logic_containers
        if logic_filter_container is None or len(logic_filter_container) == 0:
            return_value.append_message("No logic container found. Skipping view filter: {}".format(view_filter_json.name))
            if DEBUG:
                print("No logic container found. Skipping view filter: {}\n".format(view_filter_json.name))
            return return_value

        return_value.append_message("Found {} root logic container(s) for view filter: {}".format(len(logic_filter_container), view_filter_json.name))
        # there is no need to check for rules here as this is done in the nested logic container function ( root container has no rules at the same level)
        if DEBUG:
            print("Found {} root logic container(s) for view filter: {}\n".format(len(logic_filter_container), view_filter_json.name))

        # get the root container json object (there is always only just one root container)
        logic_filter_root_container = logic_filter_container[0]

        # get the logic filter class
        logic_container_class = get_logical_filter_class(logic_filter_root_container.logic_container_type)
        if not logic_container_class:
            return_value.update_sep(False, "Failed to get logic filter class for type: {}. Skipping view filter: {}".format(logic_filter_root_container.logic_container_type, view_filter_json.name))
            return return_value
    
        return_value.append_message("Using logic container class: {} for view filter: {}".format(logic_container_class.__name__, view_filter_json.name))
        if DEBUG:
            print("Using logic container class: {} for view filter: {}\n".format(logic_container_class.__name__, view_filter_json.name))

        # container for nested container(s)
        element_parameter_filters = List[ElementFilter]()

        # check if there are any nested containers to import
        if len(logic_filter_root_container.logic_containers)> 0:
            # got nested containers
            if DEBUG:
                print("Importing root logic containers: {} of type: {}".format(len( logic_filter_root_container.logic_containers), logic_filter_root_container.logic_container_type))

            # import the nested logic containers (there might be none if all we have are rules within the root logic container)
            import_nested_logic_result = import_nested_logic_container_from_data(doc, logic_filter_root_container.logic_containers)

            if DEBUG:
                print("here {}\n".format(view_filter_json.name),import_nested_logic_result.result)

            # check what we got...
            if not import_nested_logic_result.status:
                # only rules within the root container
                return_value.append_message("No nested logic containers found for {}".format(view_filter_json.name))
                # check if any rules were imported ( .net list!!)
                if import_nested_logic_result.result[0].Count>0:
                    return_value.append_message("Successfully imported {} rules for root logic container for view filter: {}".format(import_nested_logic_result.result[0].Count, view_filter_json.name))
                    for entry in import_nested_logic_result.result[0]:
                        element_parameter_filters.Add(entry)
                else:
                    return_value.append_message("No rules found for root container for view filter: {}".format(view_filter_json.name))
            else:
                # nested containers and/or rules found
                return_value.append_message("Successfully imported {} rules for nested logic container for view filter: {}".format(len(import_nested_logic_result.result[0]), view_filter_json.name))
                # add the imported rules to the main container
                for entry in import_nested_logic_result.result[0]:
                    element_parameter_filters.Add(entry)
        else:
            # no nested containers...need to check for rules at this level
            if DEBUG:
                print("No nested logic containers found for {}\n".format(view_filter_json.name))
            return_value.append_message("No nested logic containers found for {}".format(view_filter_json.name))

            if DEBUG:
                print("Checking for rules at root level for view filter: {}\n".format(view_filter_json.name))
                print("Number of rules at root level: {}\n".format(len(logic_filter_root_container.view_filter_rules)))

            if len(logic_filter_root_container.view_filter_rules) == 0:
                return_value.append_message("No filter rules found. Skipping view filter rules for view filter: {}".format(view_filter_json.name))
                if DEBUG:
                    print ("no rules\n")
                return return_value
            
            try:
                rules_result = import_rules_from_data(doc, logic_filter_root_container)

                if DEBUG:
                    print("here2 {}\n".format(view_filter_json.name),rules_result.result)

                # add filters to main container
                for entry in rules_result.result[0]:
                    element_parameter_filters.Add(entry)

            except Exception as e:
                return_value.update_sep(False, "Failed to import rules at root level for view filter: {}. Error: {}".format(view_filter_json.name, e))
                if DEBUG:
                    print("Failed to import rules at root level for view filter: {}. Error: {}\n".format(view_filter_json.name, e))
                return return_value
        
        
        # add the imported rules to the return value
        logic_container_class_instance = logic_container_class(element_parameter_filters)

        return_value.result.append(logic_container_class_instance)
    except Exception as e:
        return_value.update_sep(False, "Failed to import root logic container for view filter: {}. Error: {}".format(view_filter_json.name, e))
    
    return return_value


def create_filter_from_json(doc, view_filter_json, element_filters):

    return_value = Result()
    try:
        # set up a .net list of Element Ids
        category_ids = List[ElementId]()

        # loop over category ids and add as element id
        for category_id in view_filter_json.category_ids:
            category_ids.Add(ElementId(category_id))
            
        # check we got a least one category
        if category_ids.Count == 0:
            return_value.update_sep(False, "No valid categories found for filter: {}.".format(view_filter_json.name))
            return return_value

        # create the filter
        filter_element = create_filter(
            doc, 
            view_filter_json.name,
            category_ids,
            element_filters,
        )

        # check result
        if not filter_element:
            return_value.update_sep(False, "Failed to create filter: {}.".format(view_filter_json.name))
            return return_value

        # add success message
        return_value.append_message("Successfully created filter: {}".format(view_filter_json.name))

        # return created filter
        return_value.result.append(filter_element)
    except Exception as e:
        
        return_value.update_sep(False, "Failed to create filter: {}. Error: {}".format(view_filter_json.name, e))
    return return_value


def update_filter_from_json(doc, existing_filter, view_filter_json, element_filters):

    return_value = Result()
    try:
        # set up a .net list of Element Ids
        category_ids = List[ElementId]()

        # loop over category ids and add as element id
        for category_id in view_filter_json.category_ids:
            category_ids.Add(ElementId(category_id))
            
        # check we got a least one category
        if category_ids.Count == 0:
            return_value.update_sep(False, "No valid categories found for filter: {}.".format(view_filter_json.name))
            return return_value

        # update the filter
        updated_filter_element = create_filter(
            doc, 
            view_filter_json.name,
            category_ids,
            element_filters,
            existing_filter,
        )

        # check result
        if not updated_filter_element:
            return_value.update_sep(False, "Failed to update filter: {}.".format(view_filter_json.name))
            return return_value

        # add success message
        return_value.append_message("Successfully updated filter: {}".format(view_filter_json.name))

        # return created filter
        return_value.result.append(updated_filter_element)
    except Exception as e:
        
        return_value.update_sep(False, "Failed to update filter: {}. Error: {}".format(view_filter_json.name, e))
    return return_value


def get_filters_in_model_by_name(doc):
    """
    Get all view filters in the model by name.

    :param doc: Revit Document
    :return: Dictionary of view filters by name
    """
    filters_in_model = get_all_filters(doc)
    filters_by_name = {f.Name: f for f in filters_in_model}
    return filters_by_name


def import_view_filters_from_data(doc, json_object, progress_callback=None, overwrite_existing=False):

    # set up a status tracker
    return_value = Result()

    counter = 0
    max_value = len(json_object)

    # get all filter in the model to check if we need to overwrite any
    existing_filters_by_name = get_filters_in_model_by_name(doc)

    # loop over json objects and create view filters
    for view_filter_json in json_object:

        # check if we have any existing filters
        is_existing_filter = view_filter_json.name in existing_filters_by_name

        #TODO: check if filter already exists and handle overwrite_existing flag
        if not overwrite_existing and is_existing_filter:
            return_value.append_message("Skipping existing view filter: {}".format(view_filter_json.name))
            if DEBUG:
                print("Skipping existing view filter: {}\n".format(view_filter_json.name))
            # update progress
            counter = counter + 1
            if progress_callback:
                progress_callback.update(counter, max_value, view_filter_json.name)
            continue

        if progress_callback:
            progress_callback.update(counter, max_value, view_filter_json.name)

        return_value.append_message("Importing view filter: {}".format(view_filter_json.name))

        if DEBUG:
            print("\nImporting view filter: {}\n".format(view_filter_json.name))
        
        try:
            # get the container and all its nested items
            container_result = import_root_logic_container_from_data(doc, view_filter_json)

            if not container_result.status:
                return_value.update_sep(False, "Failed to import logic container for view filter: {}. Error: {}".format(view_filter_json.name, container_result.message))
                continue

            # keep track of the container
            return_value.append_message("Successfully imported logic container for view filter: {}".format(view_filter_json.name))

            # set up a Revit view filter depending on whether this is a new filter or an update of an existing one
            if is_existing_filter:
                return_value.append_message("Updating existing filter: {}".format(view_filter_json.name))
                if DEBUG:
                    print("Updating existing filter: {}\n".format(view_filter_json.name))
                create_filter_result = update_filter_from_json(doc, existing_filters_by_name[view_filter_json.name], view_filter_json, container_result.result[0])
            else:
                return_value.append_message("Creating new filter: {}".format(view_filter_json.name))
                if DEBUG:
                    print("Creating new filter: {}\n".format(view_filter_json.name))
                create_filter_result = create_filter_from_json(doc, view_filter_json, container_result.result[0])

            # check result
            if not create_filter_result.status:
                return_value.update_sep(False, "Failed to create filter for view filter: {}. Error: {}".format(view_filter_json.name, create_filter_result.message))
                continue

            # create success message
            return_value.append_message("Successfully created filter for view filter: {}".format(view_filter_json.name))

            # return created filter
            return_value.result.append(create_filter_result.result[0])

        except Exception as e:
            return_value.update_sep(False, "Failed to import view filter: {}. Error: {}".format(view_filter_json.name, e))
            continue


        # update progress
        counter = counter + 1

        # check for user cancel
        if progress_callback != None:
            if progress_callback.is_cancelled():
                return_value.append_message("User cancelled!")
                break
    
    return return_value
                   