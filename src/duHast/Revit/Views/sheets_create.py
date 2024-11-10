"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to Revit sheet creation. 
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

from duHast.Utilities.Objects.result import Result
from duHast.Revit.Common.transaction import in_transaction_with_failure_handling
from duHast.Revit.Common.parameter_set_utils import set_parameter_without_transaction_wrapper_by_name
from duHast.Revit.Common.Objects.FailureHandlingConfiguration import (
    FailureHandlingConfig,
)


from Autodesk.Revit.DB import FamilySymbol, Transaction, ViewSheet

def create_sheet(doc, sheet_number, sheet_name, title_block_family_symbol, additional_properties={}):
    """
    Creates a revit sheet.

    :param doc: The Revit document.
    :type doc: Document
    :param sheet_number: The new sheet number
    :type sheet_number: str
    :param sheet_name: The new sheet name
    :type sheet_name: str
    :param title_block_family_symbol: The title block type to be used
    :type title_block_family_symbol: Autodesk.Revit.DB.FamilySymbol
    :param additional_properties: a dictionary representing parameter names on the new sheet and their value, defaults to {}
    :type additional_properties: dict, optional
    :raises ValueError: If sheet number is not a string
    :raises ValueError: If sheet name is not a string
    :raises ValueError: If title_block_family_symbol is not a Autodesk.Revit.DB.FamilySymbol
    :raises ValueError: If sheet failed to create

    :return: Result class instance.

            - .status True if sheet was created and parameters where updated successfully. Otherwise False.
            - .message will contain stats.
            - .result will be a list containing the sheet instance created.

    :rtype: :class:`.Result`

    """
    return_value = Result()

    try:
        # type checking
        if not(isinstance (sheet_number, str)):
            raise ValueError ("sheet number needs to be of type str, got {} instead.".format(type(sheet_number)))
        
        if not(isinstance(sheet_name, str)):
            raise ValueError ("sheet name needs to be of type str, got {} instead.".format(type(sheet_name)))
        
        if (not(isinstance(title_block_family_symbol, FamilySymbol))):
            raise ValueError ("title_block_family_symbol needs to be of type Autodesk.Revit.DB.FamilySymbol, got {} instead.".format(type(title_block_family_symbol)))
        
        # set up an action which creates the sheet and assigns properties
        def action():
            action_return_value = Result()
            try:
                view_sheet = ViewSheet.Create(doc, title_block_family_symbol.Id)

                # check if sheet was actually created?
                if not view_sheet:
                    raise ValueError("Failed to create new ViewSheet.")
                
                # set sheet standard properties
                view_sheet.SheetNumber = sheet_number
                view_sheet.Name = sheet_name

                # set additional sheet parameter values if required
                for key,value in additional_properties.items():
                    # convert value to string if not already
                    new_value = value
                    if not(isinstance(new_value, str)):
                        new_value=str(new_value)
                    # set the new value
                    set_parameter_status = set_parameter_without_transaction_wrapper_by_name(element=view_sheet, parameter_name=key,parameter_value=new_value)
                    # update the return value
                    action_return_value.update(set_parameter_status)
                
                action_return_value.append_message("Successfully created sheet {} {}".format(sheet_number, sheet_name))
                action_return_value.result.append(view_sheet)
            except Exception as e:
                action_return_value.update_sep(False,"{}".format(e))
            return action_return_value
        
        # define failure handling for the transaction ( roll back on any warnings or errors )
        failure_handling_settings = FailureHandlingConfig(
            roll_back_on_warning=True,
            print_warnings=False,
            roll_back_on_error=True,
            print_errors=False,
        )

        # set up the transaction
        trans = Transaction(doc, "creating sheet {} {}".format(sheet_number, sheet_name))

        # execute the transaction with failure handling
        result_transaction = in_transaction_with_failure_handling(
            transaction=trans,
            action=action,
            failure_config=failure_handling_settings,
        )

        # update the return value with the result of the transaction
        return_value.update(result_transaction)
        
    except Exception as e:
        return_value.update_sep(False, "failed to create sheet with exception: {}".format(e))

    return return_value