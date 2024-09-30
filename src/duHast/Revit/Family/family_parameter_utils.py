"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Revit families parameter helper functions.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2023, Jan Christel
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
import System

# import common library
# utility functions for most commonly used Revit API tasks
from duHast.Revit.Common import transaction as rTran

# class used for stats reporting
from duHast.Utilities.Objects import result as res

# import Autodesk Revit DataBase namespace
from Autodesk.Revit.DB import (
    BuiltInParameterGroup,
    ParameterType,
    StorageType,
    Transaction,
)


def set_family_parameter_value_by_storage_type(param_w, manager, value):
    """
    Set parameter value based on the storage type of the parameter.

    :param param_w: The parameter to set the value for.
    :type param_w: Parameter
    :param manager: The family manager.
    :type manager: FamilyManager
    :param value: The value to set the parameter to.
    :type value: str

    :return: The result of the operation.
    :rtype: res.Result
    """
    return_value = res.Result()
    try:
        if param_w.StorageType == StorageType.Double:
            # THIS IS THE KEY:  Use SetValueString instead of Set.  Set requires your data to be in
            # whatever internal units of measure Revit uses. SetValueString expects your value to
            # be in whatever the current DisplayUnitType (units of measure) the document is set to
            # for the UnitType associated with the parameter.
            #
            # So SetValueString is basically how the Revit GUI works.
            manager.SetValueString(param_w, value)
            return_value.update_sep(
                True, "Updated {} to value: {}".format(param_w.Definition.Name, value)
            )
        elif param_w.StorageType == StorageType.ElementId:
            manager.Set(param_w, value)
            return_value.update_sep(
                True, "Updated {} to value: {}".format(param_w.Definition.Name, value)
            )
        elif param_w.StorageType == StorageType.Integer:
            manager.Set(param_w, value)
            return_value.update_sep(
                True, "Updated {} to value: {}".format(param_w.Definition.Name, value)
            )
        elif param_w.StorageType == StorageType.String:
            manager.Set(param_w, value)
            return_value.update_sep(
                True, "Updated {} to value: {}".format(param_w.Definition.Name, value)
            )
        else:
            return_value.update_sep(False, "Parameter storage type is not supported!")

    except Exception as e:
        return_value.update_sep(
            False, "failed to set parameter value with exception: {}".format(e)
        )
    return return_value


def set_family_parameter_value(doc, manager, fam_para, value):
    """
    Set parameter value.

    :param doc: The Revit document.
    :type doc: rdb.Document
    :param manager: The family manager.
    :type manager: FamilyManager
    :param fam_para: The parameter to set the value for.
    :type fam_para: Parameter
    :param value: The value to set the parameter to.
    :type value: str

    :return: The result of the operation.
    :rtype: res.Result
    """

    # get the parameter
    param_w = manager.get_Parameter(fam_para.Definition.Name)

    # set-up action to be executed in transaction
    def action():
        action_return_value = res.Result()
        try:
            # attempt to change parameter value
            action_return_value = set_family_parameter_value_by_storage_type(
                param_w, manager, value
            )
        except Exception as e:
            action_return_value.status = False
            action_return_value.message = (
                "{} : Failed to set parameter value: with exception: {}".format(
                    fam_para.Definition.Name, e
                )
            )
        return action_return_value

    transaction = Transaction(doc, "Setting parameter value")
    return_value = rTran.in_transaction(transaction, action)
    return return_value


def set_parameter_formula(doc, manager, fam_para, formula):
    """
    Set parameter value as a formula.

    :param doc: The Revit document.
    :type doc: rdb.Document
    :param manager: The family manager.
    :type manager: FamilyManager
    :param fam_para: The parameter to set the formula for.
    :type fam_para: rdb.Parameter
    :param formula: The formula to set.
    :type formula: str

    :return: The result of the operation.
    :rtype: res.Result
    """

    def action():
        action_return_value = res.Result()
        try:
            # set parameter formula
            manager.SetFormula(fam_para, formula)
            action_return_value.message = (
                "{} : parameter formulas successfully set.".format(
                    fam_para.Definition.Name
                )
            )
            action_return_value.result.append(fam_para)
        except Exception as e:
            action_return_value.update_sep(
                False,
                "{} : Failed to set parameter formula: {} with exception: {}".format(
                    fam_para.Definition.Name, formula, e
                ),
            )
        return action_return_value

    transaction = Transaction(doc, "Setting parameter formula")
    return_value = rTran.in_transaction(transaction, action)
    return return_value


def create_family_parameter(
    doc, parameter_name, parameter_group, parameter_type, is_instance
):
    """
    Changes a shared family parameter to a standard family parameter.

    Note: will need updating to support ForgeType fro Revit 2022 onwards

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param parameterName: The shared parameter name.
    :type parameterName: str
    :param prefix: Revit requires the new parameter to have a different name to the shard parameter, therefore a prefix to the name is applied, defaults to '_'
    :type prefix: str, optional

    :return:
        Result class instance.

        - Parameter change status returned in result.status. False if an exception occurred, otherwise True.
        - result.message will contain the name of the shared parameter and the new family parameter name.
        - result.status will contain the new family parameter.

        On exception (handled by optimizer itself!):

        - result.status (bool) will be False.
        - result.message will contain generic exception message.
        - result.status will be an empty list

    :rtype: :class:`.Result`
    """

    return_value = res.Result()

    # do some type checking
    if not isinstance(parameter_name, str):
        return_value.UpdateSep(
            False,
            "Parameter name must be a string. Got: {}".format(type(parameter_name)),
        )
        return return_value

    if not isinstance(parameter_group, BuiltInParameterGroup):
        return_value.UpdateSep(
            False,
            "Parameter group must be a BuiltInParameterGroup. Got: {}".format(
                type(parameter_group)
            ),
        )
        return return_value

    if not isinstance(parameter_type, ParameterType):
        return_value.UpdateSep(
            False,
            "Parameter type must be a ParameterType. Got: {}".format(
                type(parameter_type)
            ),
        )
        return return_value

    if not isinstance(is_instance, bool):
        return_value.UpdateSep(
            False, "Is instance must be a bool. Got: {}".format(type(is_instance))
        )
        return return_value

    # get the family manager
    manager = doc.FamilyManager
    # set up an action to be executed in a transaction
    def action():
        action_return_value = res.Result()
        try:

            parameter_new = manager.AddParameter(
                parameter_name, parameter_group, parameter_type, is_instance
            )

            action_return_value.UpdateSep(
                True, "Added parameter: {} to family.".format(parameter_name)
            )
            action_return_value.result.append(parameter_new)
        except Exception as e:
            action_return_value.UpdateSep(
                False,
                "Failed to add parameter: {} with exception: {}".format(
                    parameter_name, e
                ),
            )
        return action_return_value

    # set up a transaction and execute it
    transaction = Transaction(doc, "Add family parameter: {}".format(parameter_name))
    return_value = rTran.in_transaction(transaction, action)

    return return_value


def associate_parameter_with_other_parameter(
    doc, nested_family_instance, target_parameter_name, source_parameter_name
):
    """
    Associate a nested family instance parameter ( can be type or instance) with a host family parameter.

    :param doc: The Revit document.
    :type doc: Document
    :param nested_family_instance: The nested family instance.
    :type nested_family_instance: FamilyInstance
    :param target_parameter_name: The target parameter name.
    :type target_parameter_name: str
    :param source_parameter_name: The source parameter name.
    :type source_parameter_name: str

    :return: The result of the operation.
    :rtype: res.Result
    """

    return_value = res.Result()
    # get the family manager
    manager = doc.FamilyManager
    # get the nested family placed instance parameters
    nested_instance_parameters = nested_family_instance.GetOrderedParameters()
    # get the hot family parameters
    host_family_parameters = manager.GetParameters()

    # set up some flags to check if all went well
    found_source_parameter = False
    found_target_parameter = False

    # loop over the nested family instance parameters and check for matching parameter name
    for nested_instance_parameter in nested_instance_parameters:

        # check if match found for target parameter name
        if nested_instance_parameter.Definition.Name == target_parameter_name:
            target_parameter = nested_instance_parameter
            found_target_parameter = True

            # loop over the host family parameters and check for matching source parameter name
            for host_family_parameter in host_family_parameters:

                # check if match found for source parameter name
                if host_family_parameter.Definition.Name == source_parameter_name:
                    source_parameter = host_family_parameter
                    found_source_parameter = True

                    # set up an action to be executed in a transaction
                    def action():
                        action_return_value = res.Result()
                        try:
                            manager.AssociateElementParameterToFamilyParameter(
                                target_parameter, source_parameter
                            )
                            action_return_value.UpdateSep(
                                True,
                                "Associated parameter: {} with parameter: {}".format(
                                    target_parameter_name, source_parameter_name
                                ),
                            )
                        except Exception as e:
                            action_return_value.UpdateSep(
                                False,
                                "Failed to associate parameter: {} with parameter: {} with exception: {}".format(
                                    target_parameter_name, source_parameter_name, e
                                ),
                            )
                        return action_return_value

                    transaction = Transaction(
                        doc,
                        "Associate parameter: {} with {}".format(
                            target_parameter_name, source_parameter_name
                        ),
                    )
                    return_value = rTran.in_transaction(transaction, action)
                    break

            # break out of the loop if source parameter found
            if found_source_parameter:
                break
            else:
                # give user feedback if source parameter not found
                return_value.UpdateSep(
                    False,
                    "Failed to find source parameter: {}".format(source_parameter_name),
                )
                break

    # check if target parameter found
    if not found_target_parameter:
        return_value.UpdateSep(
            False, "Failed to find target parameter: {}".format(target_parameter_name)
        )

    return return_value
