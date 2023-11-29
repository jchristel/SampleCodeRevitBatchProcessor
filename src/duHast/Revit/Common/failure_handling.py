"""
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
# Revit Batch Processor
#
# Copyright (c) 2020  Dan Rumery, BVN
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

clr.AddReference("System.Core")
clr.ImportExtensions(System.Linq)

from System import EventHandler
from Autodesk.Revit.DB.Events import FailuresProcessingEventArgs
from Autodesk.Revit.DB import (
    FailureResolutionType,
    FailureSeverity,
    FailureProcessingResult,
    IFailuresPreprocessor,
)


def Output(message=""):
    """
    Default Output function to print to console
    """
    print(message)


def _report_failure_warning(failure, failure_definition):
    """
    Reports elements that are failing and the failure description to the output window

    :param failure: The failure to report
    :type failure: FailureMessage
    :param failure_definition: The failure definition
    :type failure_definition: FailureDefinition

    """
    failure_severity = failure.GetSeverity()
    # TODO: more thorough reporting?
    Output()
    Output(
        "\t"
        + str(failure_severity)
        + " - "
        + str(failure.GetDescriptionText())
        + " - "
        + "("
        + "GUID: "
        + str(failure.GetFailureDefinitionId().Guid)
        + ")"
    )

    if (
        failure_severity == FailureSeverity.Error
        or failure_severity == FailureSeverity.Warning
    ):
        failing_element_ids = failure.GetFailingElementIds()
        if len(failing_element_ids) > 0:
            Output()
            Output(
                "\t"
                + "Failing element ids: {}".format(
                    element_ids_to_semicolon_delimited_text(failing_element_ids)
                )
            )
        additional_elementIds = failure.GetAdditionalElementIds()
        if len(additional_elementIds) > 0:
            Output()
            Output(
                "\t"
                + "Additional element ids: {}".format(
                    element_ids_to_semicolon_delimited_text(additional_elementIds)
                )
            )

    if failure_severity == FailureSeverity.Error:
        if failure.HasResolutions():
            Output()
            Output("\t" + "Applicable resolution types:")
            Output()
            default_resolution_type = failure_definition.GetDefaultResolutionType()
            for resolution_type in failure_definition.GetApplicableResolutionTypes():
                Output(
                    "\t\t"
                    + str(resolution_type)
                    + (
                        " (Default)"
                        if (resolution_type == default_resolution_type)
                        else str.Empty
                    )
                    + " - "
                    + "'"
                    + failure_definition.GetResolutionCaption(resolution_type)
                    + "'"
                )
        else:
            Output()
            Output("\t" + "WARNING: no resolutions available")

    return


def process_failures(failures_accessor, roll_back_on_warning=False):
    """
    Process the failures encountered when transacting with a Revit document

    :param failures_accessor: The failures accessor to process
    :type failures_accessor: FailuresAccessor
    :param roll_back_on_warning: Whether to roll back the transaction on warnings
    :type roll_back_on_warning: bool
    :return: The result of the failure processing
    :rtype: FailureProcessingResult
    """
    try:
        result = FailureProcessingResult.Continue
        doc = failures_accessor.GetDocument()
        app = doc.Application
        failure_registry = app.GetFailureDefinitionRegistry()
        failures = failures_accessor.GetFailureMessages()
        if failures.Any():
            Output()
            Output(
                "Processing Revit document warnings / failures ({}):".format(
                    failures.Count
                )
            )
            for failure in failures:
                failure_definition = failure_registry.FindFailureDefinition(
                    failure.GetFailureDefinitionId()
                )
                _report_failure_warning(failure, failure_definition)
                failure_severity = failure.GetSeverity()
                if (
                    failure_severity == FailureSeverity.Warning
                    and not roll_back_on_warning
                ):
                    failures_accessor.DeleteWarning(failure)
                elif (
                    failure_severity == FailureSeverity.Error
                    and failure.HasResolutions()
                    and result != FailureProcessingResult.ProceedWithRollBack
                    and not roll_back_on_warning
                    and str(failure.GetFailureDefinitionId().Guid)
                    != "3b7fcaec-c01e-4c2e-819f-67ddd102ce1f"  # locked element by other user
                ):
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
                        Output()
                        Output(
                            "\t"
                            + "WARNING: UnlockConstraints is not a valid resolution for this failure despite the definition reporting that it is an applicable resolution!"
                        )
                    Output()
                    Output(
                        "\t"
                        + "Attempting to resolve error using resolution: {}".format(
                            failure.GetCurrentResolutionType()
                        )
                    )
                    failures_accessor.ResolveFailure(failure)
                    result = FailureProcessingResult.ProceedWithCommit
                else:
                    result = FailureProcessingResult.ProceedWithRollBack
        else:
            result = FailureProcessingResult.Continue
    except Exception as e:
        Output()
        Output("ERROR: the failure handler generated an error!")
        Output(e.Message)
        result = FailureProcessingResult.Continue
    return result


class FailuresPreprocessor(IFailuresPreprocessor):
    def __init__(self, output):
        self.output = output
        return

    def PreprocessFailures(self, failures_accessor):
        result = process_failures(failures_accessor, self.output)
        return result


def SetTransactionFailureOptions(transaction, output):
    failureOptions = transaction.GetFailureHandlingOptions()
    failureOptions.SetForcedModalHandling(True)
    failureOptions.SetClearAfterRollback(True)
    failureOptions.SetFailuresPreprocessor(FailuresPreprocessor(output))
    transaction.SetFailureHandlingOptions(failureOptions)
    return


def set_failures_accessor_failure_options(failures_accessor):
    failureOptions = failures_accessor.GetFailureHandlingOptions()
    failureOptions.SetForcedModalHandling(True)
    failureOptions.SetClearAfterRollback(True)
    failures_accessor.SetFailureHandlingOptions(failureOptions)
    return


def FailuresProcessingEventHandler(sender, args):
    """
    Function to execute when Revit raises the FailuresProcessing event
    """

    failures_accessor = args.GetFailuresAccessor()
    set_failures_accessor_failure_options(failures_accessor)
    result = process_failures(failures_accessor)
    args.SetProcessingResult(result)
    return


def with_failures_processing_handler(app, action):
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
        lambda sender, args: FailuresProcessingEventHandler(sender, args)
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

# ----------------------------------------------
# AREA OUTLINE REPLICATION CODE START
# ----------------------------------------------


def in_transaction_with_failures_processing(tranny, action, doc):
    """
    Executes an action within a Revit transaction with Revit failure processing enabled

    :param tranny: The Revit transaction to execute in
    :type tranny: Transaction
    :param action: The action to perform in the transaction
    :type action: function
    :param doc: The document to transact with
    :type doc: Document
    :return: The result of the action
    :rtype: object

    """
    result = None

    def inAction():
        tranny.Start()
        try:
            result = action()
            tranny.Commit()
        except Exception as e:
            Output("Exception: {}".format(e))
            tranny.RollBack()
        return result

    result = with_failures_processing_handler(doc.Application, inAction)
    return result
