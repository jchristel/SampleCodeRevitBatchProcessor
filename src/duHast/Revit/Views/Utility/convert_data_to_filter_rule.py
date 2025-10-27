"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
data to revit api FilterValueRule conversion helper functions.
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
from System import Enum

from duHast.Revit.Views.Objects.Data.view_filter_rule import ViewFilterRule
from duHast.Revit.Common.parameter_project import get_project_parameter_definition_by_name
from duHast.Revit.SharedParameters.shared_parameters import get_shared_parameter_by_guid
from duHast.Revit.Views.Utility.convert_data_to_filter_value_provider import get_value_provider_class
from duHast.Revit.Views.Utility.convert_data_to_filter_evaluator import get_evaluator_class


from duHast.Utilities.Objects.result import Result


from Autodesk.Revit.DB import  (
    BuiltInParameter,
    ElementId, 
    FilterDoubleRule,
    FilterIntegerRule,
    FilterInverseRule,
    FilterElementIdRule,
    FilterStringRule,
    FilterGlobalParameterAssociationRule
)

# dictionary containing varies rule mappings

# numeric rules (all of these inherit from: Autodesk.Revit.DB.FilterNumericValueRule)
# string rules (just one : Autodesk.Revit.DB.FilterStringRule)

class_mapping = {
    "FilterDoubleRule": FilterDoubleRule,
    "FilterElementIdRule":  FilterElementIdRule,
    "FilterIntegerRule": FilterIntegerRule,
    "FilterStringRule":  FilterStringRule,
    "FilterGlobalParameterAssociationRule": FilterGlobalParameterAssociationRule,

}

# notes: rules require 
# - a rule type (see class_mapping above)
# - a parameter
# - a value provider (ParameterValueProvider Class) 
# - a rule value


def create_filter_double_rule(evaluator, value_provider, rule_data_instance):
    """
    Creates a FilterDoubleRule.
    
    :param evaluator: The evaluator for the rule.
    :type evaluator: Autodesk.Revit.DB.FilterDoubleEvaluator
    :param value_provider: The value provider for the rule.
    :type value_provider: Autodesk.Revit.DB.ParameterValueProvider
    :param rule_data_instance: The rule data instance containing the rule value and epsilon.

    :return: The created FilterDoubleRule or None if creation failed.
    """

    try:
        rule = FilterDoubleRule( value_provider, evaluator, float(rule_data_instance.rule_value), float(rule_data_instance.epsilon))
        return rule
    except Exception:
        pass
    return None


def create_filter_integer_rule(evaluator, value_provider, rule_data_instance):
    """
    Creates a FilterIntegerRule.

    :param evaluator: The evaluator for the rule.
    :type evaluator: Autodesk.Revit.DB.FilterIntegerEvaluator
    :param value_provider: The value provider for the rule.
    :type value_provider: Autodesk.Revit.DB.ParameterValueProvider
    :param rule_data_instance: The rule data instance containing the rule value.

    :return: The created FilterIntegerRule or None if creation failed.
    """

    try:
        rule = FilterIntegerRule( value_provider, evaluator, int(rule_data_instance.rule_value))
        return rule
    except Exception:
        pass
    return None


def create_filter_element_id_rule(evaluator, value_provider, rule_data_instance):
    """
    Creates a FilterElementIdRule.

    :param evaluator: The evaluator for the rule.
    :type evaluator: Autodesk.Revit.DB.FilterIntegerEvaluator
    :param value_provider: The value provider for the rule.
    :type value_provider: Autodesk.Revit.DB.ParameterValueProvider
    :param rule_data_instance: The rule data instance containing the rule value.

    :return: The created FilterElementIdRule or None if creation failed.
    """

    try:
        rule = FilterElementIdRule( value_provider, evaluator, ElementId(int(rule_data_instance.rule_value)))
        return rule
    except Exception:
        pass
    return None


def create_filter_string_rule(evaluator, value_provider, rule_data_instance):
    """
    Creates a FilterStringRule.

    :param evaluator: The evaluator for the rule.
    :type evaluator: Autodesk.Revit.DB.FilterStringEvaluator
    :param value_provider: The value provider for the rule.
    :type value_provider: Autodesk.Revit.DB.ParameterValueProvider
    :param rule_data_instance: The rule data instance containing the rule value.

    :return: The created FilterStringRule or None if creation failed.
    """

    rule = None
    try:
        rule = FilterStringRule( value_provider, evaluator, rule_data_instance.rule_value)
    except Exception:
        pass
    return rule


def create_filter_global_parameter_association_rule(evaluator, value_provider, rule_data_instance):
    """
    Creates a FilterGlobalParameterAssociationRule.

    :param evaluator: The evaluator for the rule.
    :type evaluator: Autodesk.Revit.DB.FilterGlobalParameterAssociationEvaluator
    :param value_provider: The value provider for the rule.
    :type value_provider: Autodesk.Revit.DB.ParameterValueProvider
    :param rule_data_instance: The rule data instance containing the rule value.

    :return: The created FilterGlobalParameterAssociationRule or None if creation failed.
    """

    rule = None
    try:
        rule = FilterGlobalParameterAssociationRule( value_provider, evaluator, ElementId(int(rule_data_instance.rule_value)))
    except Exception:
        pass
    return rule


def get_rule_parameter(doc, rule_data_instance):
    """
    Gets the parameter for the given rule data instance.

    :param doc: The Revit document.
    :type doc: Autodesk.Revit.DB.Document
    :param rule_data_instance: The rule data instance containing the parameter information.
    :type rule_data_instance: ViewFilterRule
    :return: A Result object containing the parameter or an error message.
    """

    return_value = Result()
   
    # get the parameter
    # if the id is negative it is a built in parameter id, easiest since no further checking is required
    # if the id is positive but no guid is provided it is a project parameter, try to match by name only
    # if the id is positive and a guid is provided it is a shared parameter, try to match by guid only

    if rule_data_instance.parameter_id < 0:
        # built in parameter
        try:
            built_in_param = Enum.Parse(BuiltInParameter, rule_data_instance.parameter_name)
            return_value.result.append(built_in_param)
            return_value.append_message( "Successfully got built in parameter: {}".format(rule_data_instance.parameter_name))

        except Exception as e:
            return_value.update_sep(False, "Failed to get built in parameter: {} with exception: {}".format( rule_data_instance.parameter_name, e))
        return return_value
    
    elif rule_data_instance.parameter_id > 0 and rule_data_instance.parameter_guid == "":
        # project parameter, try to match by name only
        try:
            parameter_definition = get_project_parameter_definition_by_name(doc, rule_data_instance.parameter_name)
            if parameter_definition:
                return_value.result.append(parameter_definition)
                return_value.append_message( "Successfully got project parameter: {}".format(rule_data_instance.parameter_name))
            else:
                return_value.update_sep(False, "Failed to get project parameter: {}. No matching parameter found by name.".format( rule_data_instance.parameter_name))
        except Exception as e:
            return_value.update_sep(False, "Failed to get project parameter: {} with exception: {}".format( rule_data_instance.parameter_name, e))
        return return_value
    elif rule_data_instance.parameter_id > 0 and rule_data_instance.parameter_guid != "":
        # shared parameter, try to match by guid only
        try:
            parameter_definition = get_shared_parameter_by_guid(doc, rule_data_instance.parameter_guid)
            if parameter_definition:
                return_value.result.append(parameter_definition)
                return_value.append_message( "Successfully got shared parameter: {}[{}]".format(rule_data_instance.parameter_name, rule_data_instance.parameter_guid))
            else:
                return_value.update_sep(False, "Failed to get shared parameter: {}. No matching parameter found by guid: {}".format( rule_data_instance.parameter_name, rule_data_instance.parameter_guid))
        except Exception as e:
            return_value.update_sep(False, "Failed to get shared parameter: {} with exception: {}".format( rule_data_instance.parameter_name, e))
        return return_value
    else:
        # no valid id provided, shouldnt get here but just in case
        return_value.update_sep(False, "Failed to get parameter: {}. No valid parameter id or guid provided.".format( rule_data_instance.parameter_name))
        return return_value


def get_rule_parameter_id(doc, rule_data_instance, parameter ):
    
    # decide on which parameter id to use
    parameter_id = ElementId.InvalidElementId

    if rule_data_instance.parameter_id < 0:
        # built in parameter, use what has been stored in the rule
        parameter_id = ElementId(rule_data_instance.parameter_id)
    elif rule_data_instance.parameter_id > 0:
        # use the past in parameter
        parameter_id = parameter.Id
    
    return parameter_id


def convert_data_to_rule(doc, rule_data_instance):
    """
    Converts a ViewFilterRule data instance to a Revit FilterValueRule.

    Args:
        doc (Revit Document): The Revit document object.
        rule_data_instance (ViewFilterRule): An instance of the ViewFilterRule class containing the rule data.

    Returns:
        FilterValueRule or None: The created FilterValueRule object if successful, otherwise None.
    """
    return_value = return_value = Result()

    # check input
    if not isinstance(rule_data_instance, ViewFilterRule):
        return return_value
    
    # get the parameter
    parameter_result = get_rule_parameter(doc, rule_data_instance)

    # get out if something went wrong
    if not parameter_result.status:
        return_value.update_sep(False, "Failed to get parameter for rule: {}. Error: {}".format(rule_data_instance.parameter_name, parameter_result.message))
        return return_value

    # get the parameter ( or parameter definition)
    parameter = parameter_result.result[0]
    
    # decide on which parameter id to use
    parameter_id = get_rule_parameter_id(doc, rule_data_instance, parameter)
    #print(parameter_id)

    # get the value provider class
    value_provider_class = get_value_provider_class(rule_data_instance.value_provider)

    if not value_provider_class:
        return_value.update_sep(False, "Failed to get value provider class: {} for rule: {}".format(rule_data_instance.value_provider, rule_data_instance.parameter_name))
        return return_value

    # create the value provider
    value_provider = value_provider_class(parameter_id)
    #print(value_provider)

    # get the evaluator class
    evaluator_class = get_evaluator_class(rule_data_instance.evaluation_type)

    if not evaluator_class:
        return_value.update_sep(False, "Failed to get evaluator class: {} for rule: {}".format(rule_data_instance.evaluation_type, rule_data_instance.parameter_name))
        return return_value
    
    # convert the rule value to the correct type
    evaluator = evaluator_class()
    #print(evaluator)

    # init rule
    rule = None
    # create the rule
    if rule_data_instance.rule_type == FilterDoubleRule.__name__:
        # double rules need a double as rule value and an epsilon value

        rule = create_filter_double_rule( evaluator, value_provider, rule_data_instance)
        return_value.append_message("Created double rule: {} with epsilon: {}".format(rule_data_instance.rule_value, rule_data_instance.epsilon))
    elif rule_data_instance.rule_type == FilterIntegerRule.__name__:
        # integer rules need an integer as rule value

        rule = create_filter_integer_rule(evaluator, value_provider, rule_data_instance)
        return_value.append_message("Created integer rule: {}".format(rule_data_instance.rule_value))
    elif rule_data_instance.rule_type == FilterElementIdRule.__name__:
        # element id rules need an integer as rule value
        
        rule = create_filter_element_id_rule(evaluator, value_provider, rule_data_instance)
        return_value.append_message("Created element id rule: {}".format(rule_data_instance.rule_value))
    elif rule_data_instance.rule_type == FilterStringRule.__name__:
        # string rule
        
        rule = create_filter_string_rule(evaluator, value_provider, rule_data_instance)
        return_value.append_message("Created string rule: {}".format(rule_data_instance.rule_value))
    elif rule_data_instance.rule_type == FilterGlobalParameterAssociationRule.__name__:
        # global parameter association rule
        
        rule = create_filter_global_parameter_association_rule(evaluator, value_provider, rule_data_instance)
        return_value.append_message("Created global parameter association rule: {}".format(rule_data_instance.rule_value))
    else:
        # uh this is bad
        return_value.update_sep(False, "Failed to create rule. Unknown rule type: {} for rule: {}".format(rule_data_instance.rule_type, rule_data_instance.parameter_name))
        return return_value

    # check if rule was created
    if not rule:
        return_value.update_sep(False, "Failed to create rule of type: {} for rule: {}".format(rule_data_instance.rule_type, rule_data_instance.parameter_name))
        return return_value
    
    # check if inverted rule?
    if rule_data_instance.is_inversed:
        rule = FilterInverseRule(rule)
        return_value.append_message("Inverted rule as requested.")
    
    # return the rule
    return_value.result.append(rule)

    return return_value