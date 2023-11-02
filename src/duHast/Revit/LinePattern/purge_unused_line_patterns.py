"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Function to purge Revit line patterns.
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

from Autodesk.Revit.DB import (
    FilteredElementCollector,
    LinePatternElement,
    Transaction,
    TransactionGroup,
)

modified_by_delete = 0


def purge_unused_line_patterns(rvt_doc, DEBUG=False):
    """
    This script will ascertain line patterns not used in your model and delete them.
    It deletes the line patterns one by one and checks if there is modified elements
    which indicates an element was using the line pattern. The trasaction is rolled
    back if there is a modified element.

    IMPORTANT: This has flushed out some corrupt families with unresolvable geometry
    so it is advisable to run on a detached copy of your model first and rectify any
    family errors

    Credit for this script goes to Autodesk forum
    user so-chong from the below forum post
    https://forums.autodesk.com/t5/revit-api-forum/check-if-linepattern-is-in-use/td-p/7435014

    :param rvt_doc: The Revit document to purge line patterns from
    :type rvt_doc: Document
    :param DEBUG: Whether to print debug information or not. Optional. Defaults to False
    :type DEBUG: bool
    """

    def document_change_purge_line_patterns(sender, e):
        """
        Function to execute on DocumentChanged and inspect the modified & deleted elements.
        An unused line pattern will have 1 deleted element and 0 modified elements.

        """
        deleted_elems = e.GetDeletedElementIds()
        modified_elems = e.GetModifiedElementIds()

        if DEBUG:
            debug_string = ""

            for elem_id in modified_elems:
                elem = rvt_doc.GetElement(elem_id)
                debug_string += "MODIFIED: {} - {}\n".format(elem_id, elem.Name)

            print(
                "Modified_by_delete for operation {} is: {}".format(
                    e.Operation, modified_by_delete
                )
            )

        global modified_by_delete
        modified_by_delete = len(deleted_elems) + len(modified_elems)

    # Get the application and subscribe to the DocumentChanged event
    app = rvt_doc.Application
    app.DocumentChanged += document_change_purge_line_patterns

    # Get all line patterns in the model
    line_patterns = (
        FilteredElementCollector(rvt_doc).OfClass(LinePatternElement).ToElements()
    )
    print("Line patterns before purge: {}".format(len(line_patterns)))
    deleted_line_patterns = ""
    unused_line_pattern_count = 0

    # Loop through the line patterns and delete them one by one
    for lp in line_patterns:
        if DEBUG:
            print("Line pattern: {}".format(lp.Name))

        line_pattern_data = lp.Name + " (id: {})".format(lp.Id)

        # Transaction group is what we will roll back if there is a modified element
        trans_grp = TransactionGroup(rvt_doc, "Purge Line Patterns")
        trans_grp.Start()

        # Transaction is what we will commit to trigger DocumentChanged
        trans = Transaction(rvt_doc, "Purge Line Pattern")
        trans.Start()

        rvt_doc.Delete(lp.Id)
        trans.Commit()

        global modified_by_delete
        if DEBUG:
            print("Modified by delete in main: {}".format(modified_by_delete))

        if modified_by_delete == 1:
            unused_line_pattern_count += 1
            deleted_line_patterns += line_pattern_data + "\n"
            trans_grp.Assimilate()

        else:
            trans_grp.RollBack()

    out_message = "Deleted {} unused line patterns:\n{}".format(
        unused_line_pattern_count, deleted_line_patterns
    )

    # Get all line patterns in the model again for a post-task count
    line_patterns = (
        FilteredElementCollector(rvt_doc).OfClass(LinePatternElement).ToElements()
    )

    print(out_message)

    print("Line patterns after purge: {}".format(len(line_patterns)))

    # Unsubscribe from the DocumentChanged event
    app.DocumentChanged -= document_change_purge_line_patterns

    return out_message
