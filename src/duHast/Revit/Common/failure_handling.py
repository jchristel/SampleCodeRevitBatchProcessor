﻿"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A number of helper functions regarding advanced failure handling
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Helps to suppress warning dialogues in Revit.

"""

# Python Shell Pad. Write code snippets here and hit F5 to run.
import clr
import System
from duHast.Revit.Common.common import element_ids_to_semicolon_delimited_text

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

clr.AddReference("System.Core")
clr.ImportExtensions(System.Linq)

from System import EventHandler
from Autodesk.Revit.DB.Events import FailuresProcessingEventArgs
from Autodesk.Revit.DB import (
    FailureResolutionType,
    FailureSeverity,
    FailureProcessingResult,
)


def Output(message=""):
    """
    Default Output function to print to console
    """
    print(message)


class FailureHandlingConfig:
    def __init__(
        self,
        roll_back_on_warning=False,
        print_warnings=False,
        roll_back_on_error=True,
        print_errors=False,
        output_function=Output,
    ):
        self.roll_back_on_warning = roll_back_on_warning
        self.print_warnings = print_warnings
        self.roll_back_on_error = roll_back_on_error
        self.print_errors = print_errors
        self.output_function = output_function


def get_failure_warning_report(failure, failure_definition):
    """
    Creates a string representation of the information attached to a failure

    :param failure: The failure to report
    :type failure: FailureMessage
    :param failure_definition: The failure definition
    :type failure_definition: FailureDefinition
    :return: The string representation of the failure information
    :rtype: str
    """
    failure_message = "\n"

    failure_severity = failure.GetSeverity()

    # Log basic failure information
    failure_message += "\t{} - {} - (GUID: {})".format(
        str(failure_severity),
        str(failure.GetDescriptionText()),
        str(failure.GetFailureDefinitionId().Guid),
    )

    # Log the failing ids and additional elements (if required)
    if (
        failure_severity == FailureSeverity.Error
        or failure_severity == FailureSeverity.Warning
    ):
        failing_element_ids = failure.GetFailingElementIds()
        if len(failing_element_ids) > 0:
            failure_message += "\n"
            failure_message += "\tFailing element ids: {}".format(
                element_ids_to_semicolon_delimited_text(failing_element_ids)
            )

        additional_elementIds = failure.GetAdditionalElementIds()
        if len(additional_elementIds) > 0:
            failure_message += "\n"
            failure_message += "\tAdditional element ids: {}".format(
                element_ids_to_semicolon_delimited_text(additional_elementIds)
            )

    # If there are resolutions, log them
    if failure_severity == FailureSeverity.Error:
        if failure.HasResolutions():
            failure_message += "\n\t" + "Applicable resolution types:\n"
            default_resolution_type = failure_definition.GetDefaultResolutionType()
            for resolution_type in failure_definition.GetApplicableResolutionTypes():
                res_type = (
                    " (Default)" if resolution_type == default_resolution_type else ""
                )
                failure_message += "\t\t{}{} - '{}'".format(
                    str(resolution_type),
                    res_type,
                    failure_definition.GetResolutionCaption(resolution_type),
                )
        else:
            failure_message += "\n"
            failure_message += "\t" + "WARNING: no resolutions available"

    return failure_message


def _report_failure_warning(failure, failure_definition):
    """
    Reports elements that are failing and the failure description to the output window

    :param failure: The failure to report
    :type failure: FailureMessage
    :param failure_definition: The failure definition
    :type failure_definition: FailureDefinition

    """

    failure_messages = get_failure_warning_report(failure, failure_definition)
    Output(failure_messages)
    return failure_messages


def process_failures(failures_accessor, fail_config):
    """
    Process the failures encountered when transacting with a Revit document

    :param failures_accessor: The failures accessor to process
    :type failures_accessor: FailuresAccessor
    :return: The result of the failure processing
    :rtype: FailureProcessingResult
    """

    roll_back_on_warning = fail_config.roll_back_on_warning
    print_warnings = fail_config.print_warnings
    roll_back_on_error = fail_config.roll_back_on_error
    print_errors = fail_config.print_errors
    output = fail_config.output_function

    try:
        result = None
        # Get the failure registry
        doc = failures_accessor.GetDocument()
        app = doc.Application
        failure_registry = app.GetFailureDefinitionRegistry()
        failures = failures_accessor.GetFailureMessages()
        if failures.Any():
            if print_warnings or print_errors:
                output(
                    "Processing Revit document warnings / failures ({}):".format(
                        failures.Count
                    )
                )
            # Iterate through the failures
            for failure in failures:
                failure_definition = failure_registry.FindFailureDefinition(
                    failure.GetFailureDefinitionId()
                )

                failure_severity = failure.GetSeverity()
                # If warning and rolling back
                if failure_severity == FailureSeverity.Warning and roll_back_on_warning:
                    result = FailureProcessingResult.ProceedWithRollBack
                    if print_warnings:
                        _report_failure_warning(failure, failure_definition)
                        output("\t" + "Rolled back warning")

                # If warning and not rolling back
                elif (
                    failure_severity == FailureSeverity.Warning
                    and not roll_back_on_warning
                ):
                    failures_accessor.DeleteWarning(failure)
                    if print_warnings:
                        _report_failure_warning(failure, failure_definition)
                        output("\t" + "Deleted warning")

                # If error and rolling back
                elif failure_severity == FailureSeverity.Error and roll_back_on_error:
                    result = FailureProcessingResult.ProceedWithRollBack
                    if print_errors:
                        _report_failure_warning(failure, failure_definition)
                        output("\t" + "Rolled back error")

                # If error and attempting resolution
                elif (
                    failure_severity == FailureSeverity.Error and not roll_back_on_error
                ):
                    if print_errors:
                        _report_failure_warning(failure, failure_definition)

                    # Check if elements can be modified or if they are locked by another user
                    failure_guid = str(failure.GetFailureDefinitionId().Guid)
                    if failure_guid == "3b7fcaec-c01e-4c2e-819f-67ddd102ce1f":
                        output("\t" + "Cannot solve. Element locked by other user")
                        # locked element by other user. Can't do anything but roll back
                        result = FailureProcessingResult.ProceedWithRollBack

                    # If the failure has resolutions, attempt to resolve it
                    if failure.HasResolutions():
                        # If Unlock Constraints is a valid resolution type for the current failure, use it.
                        if failure.HasResolutionOfType(
                            FailureResolutionType.UnlockConstraints
                        ):
                            failure.SetCurrentResolutionType(
                                FailureResolutionType.UnlockConstraints
                            )
                        elif failure_definition.IsResolutionApplicable(
                            FailureResolutionType.UnlockConstraints
                        ):
                            # Revit is dumb. Unlock consrtaints cannot actually be used
                            output(
                                "\tWARNING: UnlockConstraints is not a valid resolution for this failure despite the definition reporting that it is an applicable resolution!"
                            )

                        # Will attempt to resolve the failure using the Default resolution type
                        output(
                            "\tAttempting to resolve error using resolution: {}".format(
                                failure.GetCurrentResolutionType()
                            )
                        )
                        failures_accessor.ResolveFailure(failure)
                        result = FailureProcessingResult.ProceedWithCommit
                    else:
                        output(
                            "\t"
                            + "WARNING: No resolutions available for this error. Rolling back"
                        )
                        result = FailureProcessingResult.ProceedWithRollBack

                # Every other scenario not caught by above
                else:
                    # TODO: Decide if this should be the else
                    output("\t" + "No failure configuration match. Rolling back")
                    result = FailureProcessingResult.ProceedWithRollBack

        # No failures. Continue
        else:
            result = FailureProcessingResult.Continue
    except Exception as e:
        output("ERROR: the failure handler generated an error!")
        output(e.Message)
        result = FailureProcessingResult.Continue
    return result


def set_failures_accessor_failure_options(failures_accessor):
    """
    Set the failure handling options for a failures accessor

    The below settings suppress any warning dialogues and automatically clear the failures after a rollback.
    :param failures_accessor: The failures accessor to set the failure handling options for
    :type failures_accessor: FailuresAccessor
    """

    failure_options = failures_accessor.GetFailureHandlingOptions()
    failure_options.SetForcedModalHandling(True)
    failure_options.SetClearAfterRollback(True)
    failures_accessor.SetFailureHandlingOptions(failure_options)
    return


def FailuresProcessingEventHandler(sender, args, fail_config):
    """
    Function to execute when Revit raises the FailuresProcessing event
    """

    failures_accessor = args.GetFailuresAccessor()
    set_failures_accessor_failure_options(failures_accessor)
    result = process_failures(failures_accessor, fail_config)
    args.SetProcessingResult(result)
    return


def with_failures_processing_handler(app, action, fail_config):
    """
    Execute an action with Revit failure processing enabled

    :param app: The Revit application to execute the action with
    :type app: Application
    :param action: The action to perform
    :type action: function
    :return: The result of the action
    :rtype: object
    """
    result = None
    failure_processing_event_handler = EventHandler[FailuresProcessingEventArgs](
        lambda sender, args: FailuresProcessingEventHandler(sender, args, fail_config)
    )
    app.FailuresProcessing += failure_processing_event_handler
    try:
        result = action()
    finally:
        app.FailuresProcessing -= failure_processing_event_handler
    return result


# -------------------------------------------------------------------------------------------------------------
# END OF FAILURE HANDLING CODE COPIED FROM REVIT BATCH PROCESSOR
# -------------------------------------------------------------------------------------------------------------


def in_transaction_with_failures_processing(
    transaction, action, doc, fail_config=FailureHandlingConfig()
):
    """
    Executes an action within a Revit transaction with Revit failure processing enabled. Example usage:

    def main(revit_doc, foo, bar):

        fail_config = FailureHandlingConfig()
        fail_config.print_warnings = False

        def add_func():
            # Perform actions here
            return foo + bar

        trans = Transaction(revit_doc, "Transaction Name")
        added_vals = in_transaction_with_failures(trans, add_func, revit_doc, fail_config)

    :param transaction: The Revit transaction to execute in
    :type transaction: Transaction
    :param action: The action to perform in the transaction
    :type action: function
    :param doc: The document to transact with
    :type doc: Document
    :param fail_config: The failure handling configuration to use
    :type fail_config: FailureHandlingConfig
    :return: The result of the action
    :rtype: object

    """
    result = None

    def execute_action():
        transaction.Start()
        try:

            result = action()

            transaction.Commit()
        except Exception as e:
            Output("Exception: {}".format(e))
            transaction.RollBack()
        return result

    result = with_failures_processing_handler(
        doc.Application, execute_action, fail_config
    )
    return result
