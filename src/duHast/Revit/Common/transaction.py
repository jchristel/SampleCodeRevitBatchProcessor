"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Revit transaction wrapper utility functions.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

#!/usr/bin/python
# -*- coding: utf-8 -*-
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

# class used for stats reporting
from duHast.Utilities.Objects import result as res
from duHast.Revit.Common.Objects.FailuresPreProcessor import FailuresPreprocessor
from duHast.Revit.Common.failure_handling import process_failures
from duHast.Revit.Common.Objects.FailureHandlingConfiguration import (
    FailureHandlingConfig,
)

from Autodesk.Revit.DB import Transaction

# --------------------------------------------Transactions-----------------------------------------


def in_transaction(tranny, action, *args, **kwargs):
    """
    Revit transaction wrapper.

    This function is used to execute any actions requiring a transaction in the Revit api. On exception this will roll back the transaction.

    :param tranny: The transaction to be executed.
    :type tranny: Autodesk.Revit.DB.Transaction
    :param doc: The current model document. (not used in this function)
    :type doc: Autodesk.Revit.DB.Document
    :param action: The action to be nested within the transaction. This needs to return a Result class instance!
    :type action: action().
    :param *args: is just a placeholder in case this function is called with the same args than in_transaction_with_failure_handling
    :param **kwargs: is just a placeholder in case this function is called with the same args than in_transaction_with_failure_handling

    :return:
        Result class instance.

        - .status True if successfully executed transaction, otherwise False.

    :rtype: :class:`.Result`
    """

    if not isinstance(tranny, Transaction):
        raise ValueError(
            "The transaction parameter must be an instance of Autodesk.Revit.DB.Transaction."
        )
    if not callable(action):
        raise ValueError("The action parameter must be a callable function.")

    return_value = res.Result()
    try:
        tranny.Start()
        try:
            tranny_result = action()
            tranny.Commit()
            # check what came back
            if tranny_result != None:
                # store false value
                return_value = tranny_result
        except Exception as e:
            tranny.RollBack()
            return_value.update_sep(False, "Failed with exception: {}".format(e))
    except Exception as e:
        return_value.update_sep(False, "Failed with exception: {}".format(e))

    return return_value


def in_transaction_with_failure_handling(
    transaction,
    action,
    failure_config=FailureHandlingConfig(),
    failure_processing_func=process_failures,
):
    """
    Executes an action within a Revit transaction with Revit failure processing enabled.

    Example usage:

    def main(revit_doc, foo, bar):

        fail_config = FailureHandlingConfig()
        fail_config.print_warnings = False

        def add_func():
            # Perform actions here
            return foo + bar

        trans = Transaction(revit_doc, "Add the things together")
        added_vals = in_transaction_with_failures(trans, add_func, fail_config)

    :param transaction: The executing transaction to apply the failure handling to
    :type transaction: Transaction
    :param action: The action to be executed within the transaction
    :type action: function
    :param failure_config: Configuration for the failure handling (Optional)
    :type failure_config: FailureHandlingConfig
    :param failure_processing_func: The function to process the failures (Optional)
    :type failure_processing_func: function

    """

    if not callable(action):
        raise ValueError("The action parameter must be a callable function.")
    if not callable(failure_processing_func):
        raise ValueError(
            "The failure_processing_func parameter must be a callable function."
        )
    if not isinstance(failure_config, FailureHandlingConfig):
        raise ValueError(
            "The failure_config parameter must be an instance of FailureHandlingConfig."
        )
    if not isinstance(transaction, Transaction):
        raise ValueError(
            "The transaction parameter must be an instance of Autodesk.Revit.DB.Transaction."
        )

    # Establish the failure preprocessor
    failure_pre_processor = FailuresPreprocessor(
        failure_processor=failure_processing_func, fail_config=failure_config
    )
    # Get and overwrite the failure handling options for the transaction arg
    failure_opts = transaction.GetFailureHandlingOptions()
    failure_opts.SetForcedModalHandling(failure_config.set_forced_modal_handling)
    failure_opts.SetClearAfterRollback(failure_config.set_clear_after_rollback)
    failure_opts.SetFailuresPreprocessor(failure_pre_processor)
    transaction.SetFailureHandlingOptions(failure_opts)

    # Execute the action with the updated transaction
    result = in_transaction(transaction, action)
    return result
