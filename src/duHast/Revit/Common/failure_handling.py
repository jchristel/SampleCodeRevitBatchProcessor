"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A number of helper functions regarding advanced failure handling
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Helps to suppress warning dialogues in Revit.

"""

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

clr.AddReference("System.Core")
clr.ImportExtensions(System.Linq)

from System import EventHandler
from Autodesk.Revit.DB.Events import FailuresProcessingEventArgs
from Autodesk.Revit.DB import (
    FailureResolutionType,
    FailureSeverity,
    FailureProcessingResult,
)


from duHast.Utilities.Objects.result import Result
from duHast.Revit.Common.Objects.FailureHandlingConfiguration import (
    FailureHandlingConfig,
)
from duHast.Revit.Common.common import element_ids_to_semicolon_delimited_text


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

    result = Result()
    failure_message = []

    try:
        failure_severity = failure.GetSeverity()
        # Log basic failure information
        failure_message.append(
            "\t{} - {} - (GUID: {})".format(
                str(failure_severity),
                str(failure.GetDescriptionText()),
                str(failure.GetFailureDefinitionId().Guid),
            )
        )

        # Log the failing ids and additional elements (if required)
        if (
            failure_severity == FailureSeverity.Error
            or failure_severity == FailureSeverity.Warning
        ):
            failing_element_ids = failure.GetFailingElementIds()
            if len(failing_element_ids) > 0:
                failure_message.append("\n")
                failure_message.append(
                    "\tFailing element ids: {}".format(
                        element_ids_to_semicolon_delimited_text(failing_element_ids)
                    )
                )

            additional_elementIds = failure.GetAdditionalElementIds()
            if len(additional_elementIds) > 0:
                failure_message.append("\n")
                failure_message.append(
                    "\tAdditional element ids: {}".format(
                        element_ids_to_semicolon_delimited_text(additional_elementIds)
                    )
                )

        # If there are resolutions, log them
        if failure_severity == FailureSeverity.Error:
            if failure.HasResolutions():
                failure_message.append("\n\t" + "Applicable resolution types:\n")
                default_resolution_type = failure_definition.GetDefaultResolutionType()
                for (
                    resolution_type
                ) in failure_definition.GetApplicableResolutionTypes():
                    res_type = (
                        " (Default)"
                        if resolution_type == default_resolution_type
                        else ""
                    )
                    failure_message.append(
                        "\t\t{}{} - '{}'".format(
                            str(resolution_type),
                            res_type,
                            failure_definition.GetResolutionCaption(resolution_type),
                        )
                    )
            else:
                failure_message.append("\n")
                failure_message.append("\t" + "WARNING: no resolutions available")

        result.message = "\n".join(failure_message)
    except Exception as e:
        result.update_sep(False, "Failed to get failure warning report: {}".format(e))
    return result.message


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
                        output(get_failure_warning_report(failure, failure_definition))
                        output("\t" + "Rolled back warning")
                # If warning and not rolling back
                elif (
                    failure_severity == FailureSeverity.Warning
                    and not roll_back_on_warning
                ):
                    if print_warnings:
                        output(get_failure_warning_report(failure, failure_definition))
                    failures_accessor.DeleteWarning(failure)
                    result = FailureProcessingResult.ProceedWithCommit
                    if print_warnings:
                        output("\t" + "Deleted warning")

                # If error and rolling back
                elif failure_severity == FailureSeverity.Error and roll_back_on_error:
                    result = FailureProcessingResult.ProceedWithRollBack
                    if print_errors:
                        output(get_failure_warning_report(failure, failure_definition))
                        output("\t" + "Rolled back error")

                # If error and attempting resolution
                elif (
                    failure_severity == FailureSeverity.Error and not roll_back_on_error
                ):
                    if print_errors:
                        output(get_failure_warning_report(failure, failure_definition))

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
                            # Revit is dumb. Unlock constraints cannot actually be used
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
                    output("\t" + "No failure configuration match. Rolling back")
                    result = FailureProcessingResult.ProceedWithRollBack

        # No failures. Continue
        else:
            result = FailureProcessingResult.Continue
    except Exception as e:
        output("ERROR: the failure handler generated an error! \n{}".format(e))
        result = FailureProcessingResult.ProceedWithRollBack
    return result


def FailuresProcessingEventHandler(sender, args, fail_config):
    """
    Function to execute when Revit raises the FailuresProcessing event
    """

    failures_accessor = args.GetFailuresAccessor()
    failure_options = failures_accessor.GetFailureHandlingOptions()
    failure_options.SetForcedModalHandling(fail_config.set_forced_modal_handling)
    failure_options.SetClearAfterRollback(fail_config.set_clear_after_rollback)
    failures_accessor.SetFailureHandlingOptions(failure_options)
    failure_process_result = process_failures(failures_accessor, fail_config)
    args.SetProcessingResult(failure_process_result)
    return


def with_failures_processing_handler(app, action, fail_config=FailureHandlingConfig()):
    """
    Executes an action with Revit failure processing enabled by adding
    a handler to the FailuresProcessing event. This function will need
    to be wrapped in a transaction.

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
