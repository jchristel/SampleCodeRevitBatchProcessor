"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Revit family instance placement helper functions.
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


# class used for stats reporting
from duHast.Utilities.Objects import result as res
from duHast.Revit.Common.transaction import in_transaction

from Autodesk.Revit.DB import (
    Transaction,
)


from Autodesk.Revit.DB.Structure import StructuralType


def place_a_family_instance_by_level(
    doc,
    location_point,
    family_symbol,
    target_placement_level,
    transaction_manager=in_transaction,
    modify_action=None,
):
    """
    Places a family instance by level.

    Note: It is much faster to modify the family instance after placement in the same transaction than to place it in one transaction
    and modify its parameters in a separate transaction.
    Use the modify_action parameter to provide a function that modifies the family instance after placement. Function to accept a family instance as a parameter.

    :param doc: The revit document.
    :type doc: Autodesk.Revit.DB.Document
    :param location_point: The location point of the family instance.
    :type location_point: Autodesk.Revit.DB.XYZ
    :param family_symbol: The family symbol to place.
    :type family_symbol: Autodesk.Revit.DB.FamilySymbol
    :param target_placement_level: The level to place the family instance on.
    :type target_placement_level: Autodesk.Revit.DB.Level
    :param transaction_manager: The transaction manager to use.
    :type transaction_manager: function
    :param modify_action: An action to run after the family instance is placed to modify its properties.
    :type modify_action: function

    :return: A result object.
    :rtype: duHast.Utilities.Objects.result.Result
    """

    return_value = res.Result()

    # places a family in the model
    def action():
        action_return_value = res.Result()
        try:
            # the symbol needs to be activated before using it
            # https://thebuildingcoder.typepad.com/blog/2014/08/activate-your-family-symbol-before-using-it.html
            if not family_symbol.IsActive:
                family_symbol.Activate()
                doc.Regenerate()

            # create a new instance
            element = doc.Create.NewFamilyInstance(
                location_point,
                family_symbol,
                target_placement_level,
                StructuralType.NonStructural,
            )

            action_return_value.append_message("Family placed successfully.")
            action_return_value.result.append(element)

            # if a modify action is provided, run it
            if modify_action:
                modify_result = modify_action(element)
                if isinstance(modify_result, res.Result):
                    action_return_value.update(modify_result)
            else:
                action_return_value.append_message(
                    "No modify action provided, skipping."
                )

        except Exception as e:
            action_return_value.update_sep(
                False, "Failed to place family instance: {}".format(e)
            )
        return action_return_value

    transaction = Transaction(doc, "Placing Family")
    return_value = transaction_manager(transaction, action)

    return return_value


def place_a_family_instance_in_basic_wall(
    doc,
    location_point,
    wall,
    family_symbol,
    target_placement_level,
    transaction_manager=in_transaction,
    modify_action=None,
):
    """
    Places a family instance in a basic wall.

    Note: It is much faster to modify the family instance after placement in the same transaction than to place it in one transaction
    and modify its parameters in a separate transaction.
    Use the modify_action parameter to provide a function that modifies the family instance after placement. Function to accept a family instance as a parameter.

    :param doc: The revit document.
    :type doc: Autodesk.Revit.DB.Document
    :param location_point: The location point of the family instance.
    :type location_point: Autodesk.Revit.DB.XYZ
    :param wall: The wall to place the family instance in.
    :type wall: Autodesk.Revit.DB.Wall
    :param family_symbol: The family symbol to place.
    :type family_symbol: Autodesk.Revit.DB.FamilySymbol
    :param target_placement_level: The level to place the family instance on.
    :type target_placement_level: Autodesk.Revit.DB.Level
    :param transaction_manager: The transaction manager to use.
    :type transaction_manager: function
    :param modify_action: An action to run after the family instance is placed to modify its properties.
    :type modify_action: function

    :return: A result object.
    :rtype: duHast.Utilities.Objects.result.Result
    """

    # places a family in the model
    def action():
        action_return_value = res.Result()
        try:
            # the symbol needs to be activated before using it
            # https://thebuildingcoder.typepad.com/blog/2014/08/activate-your-family-symbol-before-using-it.html
            if not family_symbol.IsActive:
                family_symbol.Activate()
                doc.Regenerate()
            # create a new instance
            element = doc.Create.NewFamilyInstance(
                location_point,
                family_symbol,
                wall,
                target_placement_level,
                StructuralType.NonStructural,
            )

            action_return_value.append_message("Family placed successfully.")
            action_return_value.result.append(element)

            # if a modify action is provided, run it
            if modify_action:
                modify_result = modify_action(element)
                if isinstance(modify_result, res.Result):
                    action_return_value.update(modify_result)
            else:
                action_return_value.append_message(
                    "No modify action provided, skipping."
                )

        except Exception as e:
            action_return_value.update_sep(
                False, "Failed to place family instance: {}".format(e)
            )
        return action_return_value

    transaction = Transaction(doc, "Placing Family")
    return_value = transaction_manager(transaction, action)
    return return_value
