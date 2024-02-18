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

import clr
import System
clr.AddReference("System.Core")
clr.ImportExtensions(System.Linq)

from Autodesk.Revit.DB import (
    FilteredElementCollector,
    LinePatternElement,
    Transaction,
    TransactionGroup,
    TransactionStatus,
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
        debug_string = ""

        if DEBUG:
            if str(e.Operation) == "TransactionCommitted":
                debug_string += "Deleted elements: {}\n".format(len(deleted_elems))
                debug_string += "Modified elements: {}\n".format(len(modified_elems))

                if len(modified_elems) == 0:
                    debug_string += (
                        "No modified elements. Line pattern will be deleted\n"
                    )
                elif len(modified_elems) > 0:
                    debug_string += (
                        "Line pattern will not be deleted. Event modified elements:\n"
                    )
                    for elem_id in modified_elems:
                        elem = rvt_doc.GetElement(elem_id)
                        try:
                            debug_string += "{}\n".format(elem.Name)
                        except:
                            debug_string += "Element Id: {}\n".format(
                                str(elem.Id.IntegerValue)
                            )

            print(debug_string)

        global modified_by_delete
        modified_by_delete = len(deleted_elems) + len(modified_elems)

    # Get the application and subscribe to the DocumentChanged event
    app = rvt_doc.Application
    app.DocumentChanged += document_change_purge_line_patterns

    # Get all line patterns in the model
    line_patterns = (
        FilteredElementCollector(rvt_doc).OfClass(LinePatternElement).ToElements()
    )

    deleted_line_patterns = ""
    unused_line_pattern_count = 0

    # Loop through the line patterns and delete them one by one
    for lp in line_patterns:
        lp_name = lp.Name
        if DEBUG:
            print("Processing line pattern: {}".format(lp_name))

        line_pattern_data = lp_name + " (id: {})".format(lp.Id)
        t_name = "Purge Line Pattern: {}".format(lp_name)
        # Transaction group is what we will roll back if there is a modified element
        trans_grp = TransactionGroup(rvt_doc, t_name)
        trans_grp.Start()

        # Transaction is what we will commit to trigger DocumentChanged
        trans = Transaction(rvt_doc, t_name)
        trans.Start()

        rvt_doc.Delete(lp.Id)
        trans.Commit()

        global modified_by_delete

        if modified_by_delete == 1:
            unused_line_pattern_count += 1
            deleted_line_patterns += line_pattern_data + "\n"
            trans_grp.Assimilate()

        else:
            trans_grp.RollBack()

        # Reset the modified_by_delete variable here incase it is
        # not reset in the DocumentChanged event
        modified_by_delete = 0

    deleted_line_patterns += "\n"
    out_message = "\nDeleted {} unused line patterns:\n\n{}".format(
        unused_line_pattern_count, deleted_line_patterns
    )

    print("\nLine patterns before purge: {}\n\n".format(len(line_patterns)))
    # Get all line patterns in the model again for a post-task count
    line_patterns = (
        FilteredElementCollector(rvt_doc).OfClass(LinePatternElement).ToElements()
    )
    print(out_message)
    print("\nLine patterns after purge: {}".format(len(line_patterns)))

    # Unsubscribe from the DocumentChanged event
    app.DocumentChanged -= document_change_purge_line_patterns

    return out_message
