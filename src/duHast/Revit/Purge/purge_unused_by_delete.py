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
from duHast.Revit.Common.failure_handling import get_failure_warning_report, set_failures_accessor_failure_options
from duHast.Revit.Common.Objects.FailuresPreProcessor import FailuresPreprocessor

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


def document_change_purge_element(sender, e, doc, debug, result):
    """
    Function to execute on DocumentChanged event and inspect the modified & deleted elements.
    An unused element will have 1 deleted element and 0 modified elements.
    """

    deleted_elements = e.GetDeletedElementIds()
    modified_elements = e.GetModifiedElementIds()
    debug_string = ""

    if debug:
        if str(e.Operation) == "TransactionCommitted":
            debug_string += "Deleted elements: {}\n".format(len(deleted_elements))
            debug_string += "Modified elements: {}\n".format(len(modified_elements))

            if len(modified_elements) == 0:
                debug_string += "No modified elements. Element will be deleted\n"
            elif len(modified_elements) > 0:
                debug_string += (
                    "Element will not be deleted. Event modified elements:\n"
                )
                for elem_id in modified_elements:
                    elem = doc.GetElement(elem_id)
                    try:
                        debug_string += "{}\n".format(elem.Name)
                    except:
                        debug_string += "Element Id: {}\n".format(
                            str(elem.Id.IntegerValue)
                        )

        result.append_message(debug_string)

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
        # attempt to set failure accessor options
        # to suppress any warning dialogues
        set_failures_accessor_failure_options(failures_accessor)
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
    # Get the application and subscribe to the DocumentChanged event
    app = doc.Application
    # This is a lambda function that acts as the event handler.
    # It takes two parameters sender and e (representing the sender and event arguments),
    # and then it calls the document_change_purge_element function passing the sender, e, doc, and DEBUG arguments to it.
    app.DocumentChanged += lambda sender, e: document_change_purge_element(
        sender, e, doc, debug, return_value
    )

    # Get all element ids from getter function
    element_ids = element_id_getter(doc)

    # check if there are any elements to purge
    if(len(element_ids) == 0):
        return_value.append_message("No elements found to purge")
        return return_value
    
    deleted_elements = ""
    unused_elements_count = 0
    callback_counter = 0

    # Loop through the line patterns and delete them one by one
    for element_id in element_ids:
        # progress call back
        callback_counter += 1
        if progress_callback != None:
            progress_callback(callback_counter, len(element_ids))

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

        # Transaction is what we will commit to trigger DocumentChanged
        # add a custom pre failure processor to suppress any revit warning dialogues
        failure_pre_processor = FailuresPreprocessor(
            output=None, failure_processor=pre_process_failures, result=return_value
        )
        trans = Transaction(doc, transaction_name)
        options = trans.GetFailureHandlingOptions()
        options.SetFailuresPreprocessor(failure_pre_processor)
        trans.SetFailureHandlingOptions(options)

        trans.Start()
        # Delete the element
        # check whether invalid element id or a negative id indicating a built-in element which cannot be deleted
        # modified_by_delete is at this case 0, which will stop the element from being deleted and the transaction will be rolled back
        if(element_id.IntegerValue < 0):
            return_value.append_message("Element {} is a built-in element and cannot be deleted".format(element_name))
        else:
            try:
                doc.Delete(element_id)
            except Exception as e:
                return_value.append_message("Element {} could not be deleted: {}".format(element_name, e))
                # note if an exception is thrown at delete step 
                # the modified_by_delete will remain 0 and the transaction will be rolled back
                # document change event does not get triggered
        trans.Commit()

        global _modified_by_delete

        if _modified_by_delete == 1:
            unused_elements_count += 1
            deleted_elements += element_data + "\n"
            trans_grp.Assimilate()

        else:
            trans_grp.RollBack()

        # Reset the modified_by_delete variable here incase it is
        # not reset in the DocumentChanged event
        _modified_by_delete = 0

    deleted_elements += "\n"
    return_value.append_message(
        "\nDeleted {} unused elements:\n\n{}".format(
            unused_elements_count, deleted_elements
        )
    )

    return_value.append_message(
        "Elements before purge: {}\n".format(len(element_ids))
    )
    # Get all line patterns in the model again for a post-task count
    element_ids = element_id_getter(doc)
    return_value.append_message(
        "Line patterns after purge: {}".format(len(element_ids))
    )

    # Unsubscribe from the DocumentChanged event
    app.DocumentChanged -= lambda sender, e: document_change_purge_element(
        sender, e, doc, debug
    )

    return return_value
