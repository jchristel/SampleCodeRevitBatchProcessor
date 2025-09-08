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

import clr
clr.AddReference('System')
from System.Collections.Generic import List

from duHast.Data.Utils.data_to_file import build_json_for_file
from duHast.Utilities.files_io import get_file_name_without_ext
from duHast.Utilities.Objects.result import Result
from duHast.Utilities.files_json import write_json_to_file


from duHast.Revit.Views.filters import get_all_filters
from duHast.Revit.Views.Objects.Data.view_filter import ViewFilter
from duHast.Revit.Views.Objects.Data.view_filter_rule import ViewFilterRule
from duHast.Revit.Views.Objects.Data.view_filter_logic_container import ViewFilterLogicContainer

from Autodesk.Revit.DB import Element, LogicalAndFilter, LogicalOrFilter, ElementFilter, ElementParameterFilter,  FilterNumericValueRule, FilterInverseRule, FilterStringRule


DEBUG = False


# Note:
# Inverse rules are essentially wrappers around standard rules inversing that outcome


def analyze_rule(doc, rule,  is_inversed, nesting_level,):
    

    view_filter_rule = ViewFilterRule()

    # can be numeric or a string rule
    # get the parameter to be checked
    if DEBUG:
        print ("{} rule parameter id: {}".format("..." * nesting_level, rule.GetRuleParameter().IntegerValue))
    view_filter_rule.parameter_id = rule.GetRuleParameter().IntegerValue

    # get the evaluation type (ends with, starts with, equals, greater than, etc)
    if DEBUG:
        print ("{} rule evaluator: {}".format("..." * nesting_level, type(rule.GetEvaluator())))
    view_filter_rule.evaluation_type = rule.GetEvaluator().GetType().Name

    # get the rule value
    if isinstance(rule, FilterNumericValueRule):
        if DEBUG:
            print ("{} rule value: {}".format("..." * nesting_level, rule.RuleValue))
        view_filter_rule.rule_value=rule.RuleValue
    elif isinstance(rule, FilterStringRule):
        if DEBUG:
            print ("{} rule value: {}".format("..." * nesting_level, rule.RuleString))
        view_filter_rule.rule_value=rule.RuleString
    
    # is the rule inversed
    if DEBUG:
        print ("{} is inversed: {}".format("..." * nesting_level, is_inversed))
    
    view_filter_rule.is_inversed = is_inversed

    if DEBUG:
        print ("{} rule complete: {}".format("..." * nesting_level, view_filter_rule))
    return view_filter_rule

    



def analyze_element_parameter_filter(doc, element_parameter_filter, nesting_level):

    rules = element_parameter_filter.GetRules()
    if DEBUG:
        print ("{} rules: {}".format("..." * nesting_level, rules.Count))
    
    # set up a list to hold the rules
    rules_analysed = []

    # go over all rules
    for rule in rules:
        if DEBUG:
            print ("{} rule type: {}".format("..." * nesting_level, type(rule)))
       
        # check if the rule is an inverse rule
        if isinstance(rule, FilterInverseRule):
            if DEBUG:
                print ("{} is inverse rule...unwrap".format("..." * nesting_level))
            rule_nested = rule.GetInnerRule()
            rule_analysed = analyze_rule(doc, rule_nested, True, nesting_level+1)
            
            # add generated rule to list
            rules_analysed.append(rule_analysed)
        else:
            rule_analysed = analyze_rule(doc, rule, False, nesting_level+1)
            
            # add generated rule to list
            rules_analysed.append(rule_analysed)
    
    return rules_analysed
       


def analyze_logical_filter(doc, logical_filter, nesting_level=0):
    
    logical_container = ViewFilterLogicContainer()

    # get the filters in the logical filter
    # should always be a list of element parameter filters or nested logical filters
    filters = logical_filter.GetFilters()

    if DEBUG:
        print ("{} Logical filter contains the following filters:".format("..." * nesting_level))
        print ("{} {} ".format("..." * nesting_level, type(filters)))

    # set up a comparing type
    filter_list_type = List[ElementFilter]

    # should always be a list of element parameter filters or nested logical filters
    if isinstance(filters, filter_list_type):
        for filter in filters:
            # check the type of filter
            if isinstance(filter, ElementParameterFilter):
                if DEBUG:
                    print ( "{} is element parameter filter".format("..." * nesting_level))
                rules = analyze_element_parameter_filter(doc, filter, nesting_level + 1)
                
                # check what came back
                if len(rules) > 0:
                    if DEBUG:
                        print("{} adding {} rules to logical container".format("..." * nesting_level, len(rules)))
                    # add rules to the logical container
                    logical_container.view_filter_rules = logical_container.view_filter_rules + rules

            elif isinstance(filter, LogicalAndFilter) or isinstance(filter_elements, LogicalOrFilter):
                if DEBUG:
                    print ( "{} is logical and filter...recursive call".format("..." * nesting_level))
                nested_container = analyze_logical_filter(doc,filter, nesting_level + 1)
                
                # check what came back
                if  nested_container:
                    # add nested container to the logical container
                    logical_container.logic_containers.append(nested_container)
                    
                
    else:
        if DEBUG:
            # not sure what this...
            print("{} Currently not supported: {}".format("..." * nesting_level, type(filters)))
        return none
    
    if DEBUG:
        print ("{} logical filter complete: {}".format("..." * nesting_level, logical_container))
    return logical_container




def analyze_filters(doc, filters, forms):


    analysed_filters = []

    max_value = len(filters.ToElements())
    counter = 1

    # set up a pyrevit progress bar
    with forms.ProgressBar(
        title="Exporting view filters: {value} of {max_value}", cancellable=True
    ) as pb:

        # loop over view filters in the model
        for filter in filters:
            
            # update progress bar
            pb.update_progress(counter, max_value)

            view_filter = ViewFilter()
            
            if DEBUG:
                # get the filter name
                print("filter name: {}".format(Element.Name.GetValue(filter)))
            view_filter.name = Element.Name.GetValue(filter)

            # getting the revit category ids the filter is applied to
            filter_revit_category_ids = filter.GetCategories()
            for id in filter_revit_category_ids:
                if DEBUG:
                    print("...Filter Id [{}]".format(id.IntegerValue))
                view_filter.category_ids.append(id.IntegerValue)
            
            # getting the filter elements
            filter_elements = filter.GetElementFilter()

            # check the type of filter, should be a logical element filter (top level)
            if isinstance(filter_elements, LogicalAndFilter) or isinstance(filter_elements, LogicalOrFilter):
                if DEBUG:
                    print ( "...is logical filter")
                container_host = analyze_logical_filter(doc, filter_elements,1)
                if container_host:
                    view_filter.logic_container = container_host
                    if DEBUG:
                        print("...updated container host to view filter")
                    analysed_filters.append(view_filter)
            else:
                if DEBUG:
                    # not sure what this...
                    print("    Currently not supported: {}".format(type(filter_elements)))

            if pb.cancelled:
                return None
            
            # update progress
            counter = counter + 1

    return analysed_filters
