"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Copies annotation samples.
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

# required for ToList() call
import clr

clr.AddReference("System.Core")
from System import Linq

clr.ImportExtensions(Linq)

from Autodesk.Revit.DB import (
    CopyPasteOptions,
    Document,
    ElementId,
    ElementTransformUtils,
    Transaction,
    Transform,
    View,
)

from duHast.Utilities.Objects.timer import Timer
from duHast.Utilities.Objects import result as res
from duHast.Revit.Common.transaction import in_transaction
from duHast.UI.Objects.ProgressBase import ProgressBase


def copy_annotation_to_views(
    doc,
    source_dims_by_view_name,
    active_view,
    views_by_name_selected,
    callback_progress=None,
):
    """
    Copy annotation from one view to another.

    :param doc: Revit Document
    :type doc: Autodesk.Revit.DB.Document
    :param source_dims_by_view_name: Dictionary containing the source annotations by target view name. ( not all annotations from the active view may want to be copied to all views )
    :type source_dims_by_view_name: dict
    :param active_view: The active view containing all source annotations
    :type active_view: Autodesk.Revit.DB.View
    :param views_by_name_selected: Dictionary containing the selected views by name
    :type views_by_name_selected: dict
    :param callback_progress: Progress callback
    :type callback_progress: ProgressBase
    :return: Result object
    :rtype: Result
    """

    if isinstance(doc, Document) == False:
        raise ValueError("doc is not a Document")
    if isinstance(active_view, View) == False:
        raise ValueError("active_view is not a View")
    if isinstance(source_dims_by_view_name, dict) == False:
        raise ValueError("source_dims_by_view_name is not a dict")

    return_value = res.Result()

    t = Timer()
    t.start()

    # progress bar data
    max = len(source_dims_by_view_name)
    counter = 0

    # loop over target views and copy specific annotation form active view to it
    for target_view_name, source_dims in source_dims_by_view_name.items():

        # update the progress bar
        counter += 1
        if callback_progress:
            callback_progress.update(counter, max)

        # only copy unique dims ( when a string of dimensions is associated with a number of elements it may occur more then once in the list of dims to copy)
        dim_ids = []
        dim_ids_int = []
        for dim in source_dims:
            if dim.Id.IntegerValue not in dim_ids_int:
                # add dim to list
                dim_ids.append(dim.Id)
                dim_ids_int.append(dim.Id.IntegerValue)

        # cast to .net list of Autodesk.Revit.DB.ElementId
        dim_ids = dim_ids.ToList[ElementId]()

        # get the target view element from the dictionary by its name
        target_view = views_by_name_selected[target_view_name]

        def action():
            action_return_value = res.Result()
            try:
                # Define Transform and CopyPasteOptions()
                transform = Transform.Identity
                opts = CopyPasteOptions()
                # copy elements to other view
                ElementTransformUtils.CopyElements(
                    active_view,
                    dim_ids,
                    target_view,
                    transform,
                    opts,
                )
                action_return_value.append_message(
                    "Copied {} annotations(s) from view: {} to view: {}".format(
                        len(dim_ids),
                        active_view.Name,
                        target_view.Name,
                    )
                )
            except Exception as e:
                action_return_value.update_sep(
                    False,
                    "Failed to copy {} annotations(s) from view: {} to view: {} with exception: {}".format(
                        len(dim_ids),
                        active_view.Name,
                        target_view.Name,
                        e,
                    ),
                )
            return action_return_value

        transaction = Transaction(
            doc,
            "Copy annotations {} to view: {}".format(len(dim_ids), target_view_name),
        )

        # TODO: replace with transaction suppression version
        transaction_result = in_transaction(transaction, action)
        # return views where annotations where added successfully so existing annotations can be deleted later on if required
        if transaction_result.status == True:
            return_value.result.append(target_view_name)

        # update the return value
        return_value.update(transaction_result)

        # check if cancelled
        if callback_progress and callback_progress.is_cancelled() == True:
            return_value.append_message("Cancelled by user")
            break

    return_value.append_message("{}".format(t.stop()))
    return return_value
