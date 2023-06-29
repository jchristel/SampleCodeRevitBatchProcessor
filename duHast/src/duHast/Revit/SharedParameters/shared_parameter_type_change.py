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
# Copyright (c) 2023  Jan Christel
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
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
