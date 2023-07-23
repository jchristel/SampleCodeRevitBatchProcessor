"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to changing Revit shared parameters to family parameters and vise versa.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright © 2023, Jan Christel
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


import Autodesk.Revit.DB as rdb

from duHast.Revit.Common import transaction as rTran
from duHast.Utilities.Objects import result as res
from duHast.Revit.SharedParameters.shared_parameters import get_family_parameters


def change_shared_parameter_to_family_parameter(doc, parameter_name, prefix="_"):
    """
    Changes a shared family parameter to a standard family parameter.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param parameter_name: The shared parameter name.
    :type parameter_name: str
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
    # get the family manager
    manager = doc.FamilyManager
    # get family parameters
    paras = get_family_parameters(doc)
    # flag
    changed_parameter = False
    # check whether any parameter in family requires changing
    for p in paras:
        if p.Definition.Name == parameter_name:
            para_old_name = p.Definition.Name

            def action():
                action_return_value = res.Result()
                try:

                    parameter_new = manager.ReplaceParameter(
                        p,
                        prefix + para_old_name,
                        p.Definition.ParameterGroup,
                        p.IsInstance,
                    )

                    action_return_value.update_sep(
                        True,
                        para_old_name
                        + ": Successfully changed shared parameter to family parameter: "
                        + prefix
                        + para_old_name,
                    )
                    action_return_value.result.append(parameter_new)
                except Exception as e:
                    action_return_value.update_sep(
                        False,
                        para_old_name
                        + ": Failed to change shared parameter to family parameter: "
                        + str(e),
                    )
                return action_return_value

            transaction = rdb.Transaction(doc, "change to family parameter")
            return_value = rTran.in_transaction(transaction, action)
            changed_parameter = return_value.status
    if changed_parameter == False:
        return_value.status = False
        return_value.message = (
            "No parameter matching: "
            + parameter_name
            + " was found. No shared parameter was changed."
        )
    return return_value


def change_family_parameter_to_shared_parameter(
    doc, parameter_name, parameter_data, parameter_def
):
    """
    Changes a family parameter to a shared parameter.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param parameter_name: The family parameter name.
    :type parameter_name: str
    :param parameter_data: A named tup[le containing the shared parameter information
    :type parameter_data: RevitSharedParametersTuple.parameterData
    :param parameter_def: The external definition of the shared parameter.
    :type parameter_def: Autodesk.Revit.DB.ExternalDefinition
    :return:
        Result class instance.
        - Parameter change status returned in result.status. False if an exception occurred, otherwise True.
        - result.message will contain the name of the family parameter and the new shared parameter name.
        - result.status will contain the new shared parameter.
        On exception (handled by optimizer itself!):
        - result.status (bool) will be False.
        - result.message will contain generic exception message.
        - result.status will be an empty list
    :rtype: :class:`.Result`
    """

    return_value = res.Result()
    # get the family manager
    manager = doc.FamilyManager
    # get family parameters
    paras = get_family_parameters(doc)
    # flag
    changed_parameter = False
    # check whether any parameter in family requires changing
    for p in paras:
        if p.Definition.Name == parameter_name:

            def action():
                action_return_value = res.Result()
                try:

                    parameter_new = manager.ReplaceParameter(
                        p,
                        parameter_def,
                        parameter_data.builtInParameterGroup,
                        parameter_data.isInstance,
                    )

                    action_return_value.update_sep(
                        True,
                        parameter_name
                        + ": Changed family parameter to shared parameter: "
                        + parameter_data.name,
                    )
                    action_return_value.result.append(parameter_new)
                except Exception as e:
                    action_return_value.update_sep(
                        False,
                        parameter_name
                        + ": Failed to change family parameter to shared parameter.",
                    )
                return action_return_value

            transaction = rdb.Transaction(doc, "change to shared parameter")
            return_value = rTran.in_transaction(transaction, action)
            changed_parameter = return_value.status
    if changed_parameter == False:
        return_value.status = False
        return_value.message = (
            "No parameter matching: "
            + parameter_name
            + " was found. No family parameter was changed."
        )
    return return_value
