"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Function to purge unused elements by delete test.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This purge approach deletes an element from the model and checks whether that deletion changed any other elements. 
If not, means the element is unused and can be deleted.

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

# the following import statements are required to use the c# List.Any() method
import clr
import System

clr.AddReference("System.Core")
clr.ImportExtensions(System.Linq)

from duHast.Utilities.Objects.result import Result
from duHast.Utilities.Objects.timer import Timer
from duHast.Revit.Common.failure_handling import (
    get_failure_warning_report,
)

from duHast.Revit.Common.Objects.FailureHandlingConfiguration import (
    FailureHandlingConfig,
)
from duHast.Revit.Common.transaction import in_transaction_with_failure_handling

from duHast.Revit.Purge.Objects.ModifierBase import ModifierBase
from duHast.UI.Objects.ProgressBase import ProgressBase

from Autodesk.Revit.DB import (
    Element,
    Transaction,
    TransactionGroup,
    FailureProcessingResult,
)

# keeps track of number of deleted / modified elements
# 1: only the element is question got deleted...no further dependencies
# greater than 1: the element itself got deleted and as a result some other element got modified
_modified_by_delete = 0


def document_change_purge_element(
    sender, e, doc, debug, deleted_elements_modifier, modified_elements_modifier, result
):
    """
    Function to execute on DocumentChanged event and inspect the modified & deleted elements.
    An unused element will have 1 deleted element and 0 modified elements.
    """

    deleted_elements = e.GetDeletedElementIds()
    modified_elements = e.GetModifiedElementIds()
    debug_string = ""
    # check if anything got deleted or modified
    if (len(deleted_elements) == 0 and len(modified_elements) == 0) and debug:
        debug_string += "No deleted and modified elements. Element will be ignored\n"
    else:
        try:
            if debug:
                if str(e.Operation) == "TransactionCommitted":
                    debug_string += "Deleted elements before adjustment: {}\n".format(
                        len(deleted_elements)
                    )
                    debug_string += "Modified elements before adjustment: {}\n".format(
                        len(modified_elements)
                    )

            # adjust deleted elements if necessary
            if deleted_elements_modifier != None:
                deleted_elements = deleted_elements_modifier.modify_deleted(
                    doc, deleted_elements
                )
                if debug:
                    debug_string += "Applying delete elements modifier\n"
                    debug_string += "Deleted elements after adjustment: {}\n".format(
                        len(deleted_elements)
                    )
            else:
                if debug:
                    debug_string += "No delete elements modifier provided.\n"

            # adjust deleted and modified elements if necessary:
            # this might be required where an element is presented through 2 or more elements in the revit api:
            # e.g. a line style is represented to a line style and a graphics style
            # this function will only purge elements which result in only 1 element  deleted and no other element modified
            # hence a delete modifier should check the deleted elements and if appropriate return only one element to be deleted
            # same applies to modified elements: a custom modifier should return 0 elements if appropriate in order for the element to be purged

            if modified_elements_modifier != None:
                modified_elements = modified_elements_modifier.modify_modified(
                    doc, modified_elements
                )
                if debug:
                    debug_string += "Applying modified elements modifier\n"
                    debug_string += "Modified elements after adjustment: {}\n".format(
                        len(modified_elements)
                    )
            else:
                if debug:
                    debug_string += "No modified elements modifier provided.\n"

            if debug:
                if len(modified_elements) == 0 and len(deleted_elements) == 1:
                    debug_string += "No modified elements. Element will be deleted\n"
                elif len(modified_elements) > 0:
                    debug_string += (
                        "Element will not be deleted. Event modified elements:\n"
                    )
                    for elem_id in modified_elements:
                        debug_string += "element id is of type: {}\n".format(
                            type(elem_id)
                        )
                        elem = doc.GetElement(elem_id)
                        debug_string += "element is of type: {}\n{}\n".format(
                            type(elem), elem
                        )
                        try:
                            if isinstance(elem, Element):
                                debug_string_temp = "Nameless Element"
                                try:
                                    debug_string += "{}\n".format(
                                        Element.Name.GetValue(elem)
                                    )
                                except:
                                    debug_string += debug_string_temp
                        except Exception as e:
                            debug_string += "An exception occurred when building debug string in modified elements: {}\n".format(
                                e
                            )

                elif len(deleted_elements) > 1:
                    debug_string += "Element will not be deleted. More than one element got deleted:\n"
                    for elem_id in deleted_elements:
                        debug_string += "Element Id: {}\n".format(str(elem_id))
                        elem = doc.GetElement(elem_id)
                        debug_string += "element is of type: {}\n{}\n".format(
                            type(elem), elem
                        )
                        try:
                            if isinstance(elem, Element):
                                debug_string += "{}\n".format(elem.Name)
                        except Exception as e:
                            debug_string += "An exception occurred when building debug string in deleted elements: {}\n".format(
                                e
                            )
                elif len(deleted_elements) == 0 and len(modified_elements) == 0:
                    # just in case modifiers applied reduce both counts to 0...should not happen?
                    debug_string += (
                        "No deleted and modified elements. Element will be ignored\n"
                    )
                else:
                    debug_string += "Element will not be deleted. Deleted {} and modified elements: {}\n".format(
                        len(deleted_elements), len(modified_elements)
                    )

        except Exception as e:
            debug_string += "Error adjusting deleted / modified elements: {}".format(e)

    # update logs
    if debug:
        result.append_message(debug_string)
    # update global variable
    global _modified_by_delete
    _modified_by_delete = len(deleted_elements) + len(modified_elements)


def pre_process_failures(failures_accessor, process_result):
    """
    Rolls back the processing if any warning is encountered

    :param failures_accessor: The failures accessor to process
    :type failures_accessor: FailuresAccessor
    :param process_result: A Result class instance used to store any failure messages only
    :type process_result: :class:`.Result`
    :return: The result of the failure processing
    :rtype: FailureProcessingResult
    """
    try:
        # process warnings if any
        result = FailureProcessingResult.Continue
        doc = failures_accessor.GetDocument()
        app = doc.Application
        failure_registry = app.GetFailureDefinitionRegistry()
        failures = failures_accessor.GetFailureMessages()
        if failures.Any():
            process_result.append_message("")
            process_result.append_message(
                "Processing Revit document warnings / failures ({}):".format(
                    failures.Count
                )
            )
            for failure in failures:
                failure_definition = failure_registry.FindFailureDefinition(
                    failure.GetFailureDefinitionId()
                )

                # get a description of the warning which occurred
                warning_report = get_failure_warning_report(failure, failure_definition)
                process_result.append_message("\n".join(warning_report))

                # continue will roll back ( do not attempt to address the warning )
                result = FailureProcessingResult.ProceedWithRollBack
        else:
            result = FailureProcessingResult.Continue
    except Exception as e:
        process_result.update_sep(
            False, "The failure handler generated an error: {}".format(e)
        )
        result = FailureProcessingResult.Continue
    return result


def purge_unused_elements(
    doc,
    element_id_getter=None,
    deleted_elements_modifier=None,
    modified_elements_modifier=None,
    progress_callback=None,
    debug=False,
):
    """
    This script will ascertain elements not used in your model and delete them.
    It deletes the elements one by one and checks if there is modified elements
    which indicates another element was using the element. The transaction is rolled
    back if there is a modified element.

    IMPORTANT: This has flushed out some corrupt families with unresolvable geometry
    so it is advisable to run on a detached copy of your model first and rectify any
    family errors

    Credit for this script goes to Autodesk forum
    user so-chong from the below forum post
    https://forums.autodesk.com/t5/revit-api-forum/check-if-linepattern-is-in-use/td-p/7435014

    :param doc: The Revit document to purge line patterns from
    :type doc: Document
    :param DEBUG: Whether to print debug information or not. Optional. Defaults to False
    :type DEBUG: bool
    """

    return_value = Result()

    # check variables first
    if element_id_getter != None:
        if not callable(element_id_getter):
            raise TypeError("element_id_getter must be a function")
    if deleted_elements_modifier != None:
        if not isinstance(deleted_elements_modifier, ModifierBase):
            raise TypeError(
                "deleted_elements_modifier must be an instance of ModifierBase"
            )
    if modified_elements_modifier != None:
        if not isinstance(modified_elements_modifier, ModifierBase):
            raise TypeError(
                "modified_elements_modifier must be an instance of ModifierBase"
            )
    if progress_callback != None:
        if not isinstance(progress_callback, ProgressBase):
            raise TypeError("progress_callback must be an instance of ProgressBase")

    # Get the application and subscribe to the DocumentChanged event
    app = doc.Application
    # This is a lambda function that acts as the event handler.
    # It takes two parameters sender and e (representing the sender and event arguments),
    # and then it calls the document_change_purge_element function passing the sender, e, doc, and DEBUG arguments to it.
    app.DocumentChanged += lambda sender, e: document_change_purge_element(
        sender,
        e,
        doc,
        debug,
        deleted_elements_modifier,
        modified_elements_modifier,
        return_value,
    )

    # Get all element ids from getter function
    element_ids = element_id_getter(doc)

    # check if there are any elements to purge
    if len(element_ids) == 0:
        return_value.append_message("No elements found to purge")
        return return_value

    deleted_elements_data = ""
    unused_elements_count = 0
    callback_counter = 0

    # set up a timer fro each element and an overall timer
    t_by_element = Timer()
    t_overall = Timer()
    t_overall.start()

    # Loop through the line patterns and delete them one by one
    for element_id in element_ids:
        # start the timer
        t_by_element.start()
        # progress call back
        callback_counter += 1
        if progress_callback != None:
            progress_callback.update(callback_counter, len(element_ids))

        # get the actual element from the document
        element = doc.GetElement(element_id)
        # store its name for reporting later on
        element_name = Element.Name.GetValue(element)

        if debug:
            return_value.append_message("Processing element: {}".format(element_name))

        element_data = "{} (id: {})".format(element_name, element_id)
        transaction_name = "Purge element: {}".format(element_name)
        # Transaction group is what we will roll back if there is a modified element
        trans_grp = TransactionGroup(doc, transaction_name)
        trans_grp.Start()

        # set up action attempting to delete an element
        def action():
            action_return_value = Result()
            if element_id.IntegerValue < 0:
                action_return_value.append_message(
                    "Element {} {} is a built-in element and cannot be deleted".format(
                        element_id.IntegerValue, element_name
                    )
                )
            else:
                try:
                    doc.Delete(element_id)
                    action_return_value.append_message(
                        "Attempted to delete element {} :: {}".format(
                            element_id, element_name
                        )
                    )
                except Exception as e:
                    action_return_value.update_sep(
                        False,
                        "Element {} could not be deleted: {}".format(element_name, e),
                    )
                    # note if an exception is thrown at delete step
                    # the modified_by_delete will remain 0 and the transaction will be rolled back
                    # document change event does not get triggered
            return action_return_value

        # define failure handling for the transaction ( roll back on any warnings or errors )
        failure_handling_settings = FailureHandlingConfig(
            roll_back_on_warning=True,
            print_warnings=False,
            roll_back_on_error=True,
            print_errors=False,
        )

        # set up the transaction
        trans = Transaction(doc, transaction_name)

        # execute the transaction with failure handling
        result_transaction = in_transaction_with_failure_handling(
            transaction=trans,
            action=action,
            failure_config=failure_handling_settings,
            failure_processing_func=pre_process_failures,
        )

        # update the return value with the result of the transaction
        return_value.update(result_transaction)

        global _modified_by_delete

        if _modified_by_delete == 1:
            unused_elements_count += 1
            deleted_elements_data += element_data + "\n"
            trans_grp.Assimilate()

        else:
            trans_grp.RollBack()

        # Reset the modified_by_delete variable here incase it is
        # not reset in the DocumentChanged event
        _modified_by_delete = 0

        return_value.append_message(
            "Element {} took: {}".format(element_id, t_by_element.stop())
        )

        # check for user cancel
        if progress_callback != None:
            if progress_callback.is_cancelled():
                return_value.append_message("User cancelled!")
                break

    deleted_elements_data += "\n"
    return_value.append_message(
        "\nDeleted {} unused elements:\n\n{}".format(
            unused_elements_count, deleted_elements_data
        )
    )

    return_value.append_message("Elements before purge: {}\n".format(len(element_ids)))
    # Get all line patterns in the model again for a post-task count
    element_ids = element_id_getter(doc)
    return_value.append_message("Elements after purge: {}".format(len(element_ids)))

    # Unsubscribe from the DocumentChanged event
    app.DocumentChanged -= lambda sender, e: document_change_purge_element(
        sender, e, doc, debug
    )

    return_value.append_message("Purge took: {}".format(t_overall.stop()))
    return return_value
