"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to Revit view filters to storage conversion. 
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
from System import Enum

from duHast.Utilities.Objects.result import Result

from duHast.Revit.Views.Objects.Data.view_filter import ViewFilter
from duHast.Revit.Views.Objects.Data.view_filter_rule import ViewFilterRule
from duHast.Revit.Views.Objects.Data.view_filter_logic_container import ViewFilterLogicContainer
from duHast.Revit.SharedParameters.shared_parameters import get_all_shared_parameters
from duHast.Revit.Common.parameter_project import get_project_parameter_definitions

from Autodesk.Revit.DB import (
    BuiltInParameter,
    ElementId,
    Element, 
    LogicalAndFilter, 
    ElementFilter, 
    ElementParameterFilter,
    FilteredElementCollector,
    FilterElementIdRule, 
    FilterNumericValueRule, 
    FilterInverseRule, 
    FilterStringRule,
    LogicalOrFilter,  
    ParameterValueProvider,
)


DEBUG = False


# Note:
# Inverse rules are essentially wrappers around standard rules inversing that outcome

def get_project_parameters(doc):
    """
    Get all project parameters in the document.

    :param doc: Current Revit document
    :type doc: Autodesk.Revit.DB.Document
    :return: Dictionary where key is the id of the parameter and values are a list of [name, guid]
    :rtype: dict
    """

    # get project parameter definitions
    definitions = get_project_parameter_definitions(doc)

    # get all shared parameters
    shared_parameters = get_all_shared_parameters(doc)


    # build dictionary where key is the id of the parameter and values are a list of [name, guid]
    # guid will be None for non-shared parameters
    project_parameters = {}

    # loop over definitions and find any shared parameters
    for d in definitions:

        # set default flag to not shared
        is_shared = False

        # loop over shared parameters to see if we have a match
        for sp in shared_parameters:
            if d.Id.IntegerValue == sp.Id.IntegerValue:
                # this is a shared parameter
                is_shared = True
                project_parameters[d.Id.IntegerValue] = [d.Name, str(sp.GuidValue)]
                break
        
        # this is not a shared parameter
        if not is_shared:
            project_parameters[d.Id.IntegerValue] = [d.Name, None]
    
    return project_parameters


def analyze_rule(doc, rule,  is_inversed, project_parameters, nesting_level, debug = False):
    """
    
    Analyze a single rule and return a view filter rule object.
    
    :param doc: The Revit document.
    :type doc: Document
    :param rule: The rule to analyze.
    :type rule: FilterRule
    :param is_inversed: Whether the rule is inversed.
    :type is_inversed: bool
    :param nesting_level: The nesting level of the rule.
    :type nesting_level: int
    :param debug: Whether to print debug information.
    :type debug: bool

    :return: A result object containing the view filter rule. If an error occurs, the result object will indicate failure and contain an error message.
    :rtype: :class:`.Result`
    """

    return_value = Result()
    try:

        view_filter_rule = ViewFilterRule()

        # can be numeric or a string rule
        # get the parameter to be checked
        if debug:
            return_value.append_message ("{} rule parameter id: {}".format("..." * nesting_level, rule.GetRuleParameter().IntegerValue))
        
        # parameter id
        view_filter_rule.parameter_id = rule.GetRuleParameter().IntegerValue

        # save the rule type
        view_filter_rule.rule_type = type(rule).__name__

        # depending on the rule type there might be an epsilon value ( in the moment only for double values)
        if hasattr(rule, "Epsilon"):
            view_filter_rule.epsilon = rule.Epsilon
            if debug:
                return_value.append_message ("{} rule epsilon: {}".format("..." * nesting_level, view_filter_rule.epsilon))


        # in the moment there is only one value provider type
        view_filter_rule.value_provider = ParameterValueProvider.__name__

        # if the id is negative means its a built in parameter and we dont have to get its name and or guid
        # check if parameter id indicates a custom parameter by checking if id value is greater than 0
        # and whether we have any project parameters to check against
        if view_filter_rule.parameter_id > 0 and len(project_parameters) > 0:
            
            if view_filter_rule.parameter_id in project_parameters:
               
                # assign the parameter name
                view_filter_rule.parameter_name = project_parameters[view_filter_rule.parameter_id][0]
                
                if debug:
                    return_value.append_message ("{} rule parameter name: {}".format("..." * nesting_level, view_filter_rule.parameter_name))
                
                if project_parameters[view_filter_rule.parameter_id][1] is not None:
                    # assign the parameter guid
                    view_filter_rule.parameter_guid = project_parameters[view_filter_rule.parameter_id][1]
                    
                    if debug:
                        return_value.append_message ("{} rule parameter guid: {}".format("..." * nesting_level, view_filter_rule.parameter_guid))
                else:
                    # guid is None, leave the default value
                    if debug:
                        return_value.append_message ("{} rule parameter guid: None".format("..." * nesting_level))
                    
        elif view_filter_rule.parameter_id < 0:
                # built in parameter, leave the default name and guid values
                if debug:
                    return_value.append_message ("{} rule parameter is built in parameter".format("..." * nesting_level))
                
                # get the built in parameter name
                param = Enum.ToObject(BuiltInParameter, view_filter_rule.parameter_id)
                view_filter_rule.parameter_name = str(param)
        else:
            pass
            # should never get here but just in case

        # get the evaluation type (ends with, starts with, equals, greater than, etc)
        if debug:
            return_value.append_message ("{} rule evaluator: {}".format("..." * nesting_level, rule.GetEvaluator().GetType().Name))
        
        view_filter_rule.evaluation_type = rule.GetEvaluator().GetType().Name

        # get the rule value
        if isinstance(rule, FilterElementIdRule):
            # check for element id rule
            if debug:
                return_value.append_message ("{} rule value: {}".format("..." * nesting_level, rule.RuleValue.IntegerValue))
            view_filter_rule.rule_value=rule.RuleValue.IntegerValue
        
        elif isinstance(rule, FilterNumericValueRule):
            # check for numeric rule
            if debug:
                return_value.append_message ("{} rule value: {}".format("..." * nesting_level, rule.RuleValue))
            
            # check if the rule value is an element id ( if a global parameter provides the value, the rule value is the global parameter id)
            if isinstance(rule.RuleValue, ElementId):
                view_filter_rule.rule_value=rule.RuleValue.IntegerValue
            else:
                view_filter_rule.rule_value=rule.RuleValue
        
        elif isinstance(rule, FilterStringRule):
            # check for string rule
            if debug:
                return_value.append_message ("{} rule value: {}".format("..." * nesting_level, rule.RuleString))
            view_filter_rule.rule_value=rule.RuleString
        
        # is the rule inversed
        if debug:
            return_value.append_message ("{} is inversed: {}".format("..." * nesting_level, is_inversed))
        
        view_filter_rule.is_inversed = is_inversed

        if debug:
            return_value.append_message ("{} rule complete: {}".format("..." * nesting_level, view_filter_rule))
        
        return_value.result.append(view_filter_rule)
        return return_value
    except Exception as e:
        return_value.update_sep(False, "Failed to analyze rule. Error: {}".format(e))
        return return_value

    

def analyze_element_parameter_filter(doc, element_parameter_filter, project_parameters, nesting_level, debug = False):
    """
    Analyze an element parameter filter and return a list of view filter rules.

    :param doc: The Revit document.
    :type doc: Document
    :param element_parameter_filter: The element parameter filter to analyze.
    :type element_parameter_filter: ElementParameterFilter
    :param nesting_level: The nesting level of the filter.
    :type nesting_level: int
    :param debug: Whether to print debug information.
    :type debug: bool

    :return: A result object containing a list of view filter rules. If an error occurs, the result object will indicate failure and contain an error message.
    :rtype: :class:`.Result`
    """

    return_value = Result()

    try:
        rules = element_parameter_filter.GetRules()
        if debug:
            return_value.append_message ("{} rules: {}".format("..." * nesting_level, rules.Count))
        
        # set up a list to hold the rules
        rules_analysed = []

        # go over all rules
        for rule in rules:
            if debug:
                return_value.append_message ("{} rule type: {}".format("..." * nesting_level, type(rule)))
        
            # check if the rule is an inverse rule
            if isinstance(rule, FilterInverseRule):
                if debug:
                    return_value.append_message ("{} is inverse rule...unwrap".format("..." * nesting_level))
                
                # get the nested rule
                rule_nested = rule.GetInnerRule()

                # analyze the inverse rule
                rule_analysed_result = analyze_rule(doc, rule_nested, True, project_parameters, nesting_level+1, debug)

                # check if successful
                if not rule_analysed_result.status:
                    return_value.update_sep(False, "Failed to analyze element parameter filter inverse rule. Error: {}".format(rule_analysed_result.message))
                    continue
                
                # add generated rule to list
                rules_analysed.append(rule_analysed_result.result[0])
            else:
                # analyze the rule
                rule_analysed_result = analyze_rule(doc, rule, False, project_parameters,nesting_level+1, debug)

                # check if successful
                if not rule_analysed_result.status:
                    return_value.update_sep(False, "Failed to analyze element parameter filter rule. Error: {}".format(rule_analysed_result.message))
                    continue
                
                # add generated rule to list
                rules_analysed.append(rule_analysed_result.result[0])
        

        # return the rules
        return_value.result.append(rules_analysed)
        return return_value

    except Exception as e:
        return_value.update_sep(False, "Failed to analyze element parameter filter. Error: {}".format(e))
        return return_value
       


def analyze_logical_filter(doc, logical_filter, project_parameters, nesting_level=0, debug = False):
    """
    Analyze a logical filter and return a view filter logic container.

    :param doc: The Revit document.
    :type doc: Document
    :param logical_filter: The logical filter to analyze.
    :type logical_filter: LogicalAndFilter or LogicalOrFilter
    :param nesting_level: The nesting level of the filter.
    :type nesting_level: int
    :param debug: Whether to print debug information.
    :type debug: bool

    :return: A result object containing a view filter logic container. If an error occurs, the result object will indicate failure and contain an error message.
    :rtype: :class:`.Result`
    """

    return_value = Result()

    try:
        # setup a logical container
        logical_container = ViewFilterLogicContainer()

        # store the type of logical container
        logical_container.logic_container_type = type(logical_filter).__name__

        # get the filters in the logical filter
        # should always be a list of element parameter filters or nested logical filters
        filters = logical_filter.GetFilters()

        if debug:
            return_value.append_message ("{} Logical filter contains the following filters:".format("..." * nesting_level))
            return_value.append_message ("{} {} ".format("..." * nesting_level, type(filters)))

        # set up a comparing type to make sure we get a list
        filter_list_type = List[ElementFilter]

        # should always be a list of element parameter filters or nested logical filters
        if isinstance(filters, filter_list_type):

            # loop over list contents
            for filter in filters:
                # check the type of filter
                if isinstance(filter, ElementParameterFilter):
                    if debug:
                        return_value.append_message ( "{} is element parameter filter".format("..." * nesting_level))
                    
                    # analyze the element parameter filter
                    rules_result = analyze_element_parameter_filter(doc, filter, project_parameters, nesting_level + 1, debug)
                    
                    # check what came back
                    if rules_result.status and len(rules_result.result) > 0:
                        if debug:
                            return_value.append_message ("{} adding {} rules to logical container".format("..." * nesting_level, len(rules_result.result)))
                        
                        # add rules to the logical container
                        logical_container.view_filter_rules = logical_container.view_filter_rules + rules_result.result[0]
                    else:
                        # something went wrong
                        return_value.update_sep(False, "Failed to analyze element parameter filter. Error: {}".format(rules_result.message))

                elif isinstance(filter, LogicalAndFilter) or isinstance(filter, LogicalOrFilter):
                    if debug:
                        return_value.append_message ( "{} is logical and filter...recursive call".format("..." * nesting_level))
                    
                    # analyse another logical conditions
                    nested_container_result = analyze_logical_filter(doc,filter, project_parameters, nesting_level + 1, debug)
                    
                    # check what came back
                    if  nested_container_result.status and len(nested_container_result.result) > 0:
                        # add nested container to the logical container
                        logical_container.logic_containers.append(nested_container_result.result[0])
                        
        else:
            # not sure what this...
            return_value.update_sep(False, "{} Currently not supported: {}".format("..." * nesting_level, type(filters)))
            return return_value
        
        if debug:
            return_value.append_message ("{} logical filter complete: {}".format("..." * nesting_level, logical_container))
        
        # add the container
        return_value.result.append(logical_container)

        # return to caller
        return return_value

    except Exception as e:
        return_value.update_sep(False, "Failed to analyze logical filter. Error: {}".format(e))
        return return_value



def analyze_filters(doc, filters,  progress_callback, debug = False):
    """
    Analyze all view filters in the document and return a list of view filter objects.

    :param doc: The Revit document.
    :type doc: Document
    :param filters: The view filters to analyze.
    :type filters: FilterElementCollector
    :param forms: The pyrevit forms module.
    :type forms: module
    :param debug: Whether to print debug information.
    :type debug: bool

    :return: A result object containing a list of view filter objects. If an error occurs, the result object will indicate failure and contain an error message.
    :rtype: :class:`.Result`
    """

    return_value = Result()

    try:

        analysed_filters = []

        # get all project parameters in order to be able to identify any shared parameters properly when re-importing the filters
        project_parameters = get_project_parameters(doc)

        # prepare progress bar
        max_value = 0

        # check if we got a FilteredElementCollector or a list
        if isinstance(filters,FilteredElementCollector):
            max_value = len(filters.ToElements())
        else:
            max_value = len(filters)
        
        counter = 1

        # loop over view filters in the model
        for filter in filters:
            
            view_filter = ViewFilter()

            # store the filter name
            view_filter.name = Element.Name.GetValue(filter)

            if debug:
                # get the filter name
                return_value.append_message ("filter name: {}".format(Element.Name.GetValue(filter)))

            # update progress bar
            if progress_callback:
                progress_callback.update(counter, max_value, view_filter.name)
           
            # getting the revit category ids the filter is applied to
            filter_revit_category_ids = filter.GetCategories()
            
            # add category ids to the view filter
            for id in filter_revit_category_ids:
                if debug:
                    return_value.append_message ("...Filter Id [{}]".format(id.IntegerValue))
                
                view_filter.category_ids.append(id.IntegerValue)
            
            # getting the filter elements
            filter_elements = filter.GetElementFilter()

            # check the type of filter, should be a logical element filter (top level)
            if isinstance(filter_elements, LogicalAndFilter) or isinstance(filter_elements, LogicalOrFilter):
                if debug:
                    return_value.append_message ( "...is logical filter")
                
                # analyze the logical filter
                container_host_result = analyze_logical_filter(doc, filter_elements,  project_parameters,   1, debug)
                
                # check what came back
                if container_host_result.status and len(container_host_result.result) > 0:

                    # store the container host in the view filter
                    view_filter.logic_containers.append(container_host_result.result[0])
                    
                    if debug:
                        return_value.append_message ("...updated container host to view filter")
                    
                    # add the view filter to the list to be returned
                    analysed_filters.append(view_filter)
            else:

                # not sure what this...
                return_value.append_message ("    Currently not supported: {}".format(type(filter_elements)))

            # update progress
            counter = counter + 1

            # check for user cancel
            if progress_callback != None:
                if progress_callback.is_cancelled():
                    return_value.append_message("User cancelled!")
                    break
        
        return_value.result.append(analysed_filters)
        return return_value

    except Exception as e:
        return_value.update_sep(False, "Failed to analyze filters. Error: {}".format(e))
        return return_value
