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
from duHast.Utilities.Objects.result import Result

from Autodesk.Revit.DB import  BuiltInParameter, ElementId, FilterValueRule,ParameterValueProvider


from Autodesk.Revit.DB import  (
    FilterDoubleRule,
    FilterIntegerRule,
    FilterElementIdRule,
    FilterStringRule,
)

# dictionary containing varies rule mappings

# numeric rules (all of these inherit from: Autodesk.Revit.DB.FilterNumericValueRule)
# string rules (just one : Autodesk.Revit.DB.FilterStringRule)

class_mapping = {
    "FilterDoubleRule": FilterDoubleRule,
    "FilterElementIdRule":  FilterElementIdRule,
    "FilterIntegerRule": FilterIntegerRule,
    "FilterStringRule":  FilterStringRule,

}

# notes: rules require 
# - a rule type (see class_mapping above)
# - a parameter
# - a value provider (ParameterValueProvider Class) 
# - a rule value

def get_rule_parameter(doc, rule_data_instance):
    
    return_value = Result()
   
    # get the parameter
    # if the id is negative it is a built in parameter id, easiest since no further checking is required
    # if the id is positive but no guid is provided it is a project parameter, try to match by name only
    # if the id is positive and a guid is provided it is a shared parameter, try to match by guid only

    if rule_data_instance.parameter_id < 0:
        # built in parameter
        try:
            builtin_param = Enum.Parse(BuiltInParameter, rule_data_instance.parameter_name)
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
    
    return return_value



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

    
    # if the id is negative it is a built in parameter id, easiest since no further checking is required
    # if the id is positive but no guid is provided it is a project parameter, try to match by name only
    # if the id is positive and a guid is provided it is a shared parameter, try to match by guid only


    return return_value