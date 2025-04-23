"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of functions around creating Revit filled regions.
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

from duHast.Utilities.Objects.result import Result
from duHast.Revit.Common.transaction import in_transaction


# import Autodesk
from Autodesk.Revit.DB import (
    FilledRegion,
    Transaction,
)

def create_filled_region_by_view(doc, view, curve_loops, filled_region_type, transaction_manager = in_transaction):
    """
    Creates a filled region in the specified view.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param view: The view to create the filled region in.
    :type view: Autodesk.Revit.DB.View
    :param curve_loops: The curve loops to use for the filled region.
    :type curve_loops: list Autodesk.Revit.DB.CurveLoop
    :param filled_region_type: The type of filled region to create.
    :type filled_region_type: Autodesk.Revit.DB.ElementId

    :return: A result object containing the created filled region instance.
    :rtype: Result
    """


    # set up a status tracker
    return_value = Result()

    # set up an action creating a filled region
    def action():
         # set up a status tracker
        action_return_value = Result()
        try:
            # create the filled region
            filled_region = FilledRegion.Create(doc, filled_region_type, view.Id, curve_loops)
            # store the filled region in the return value
            action_return_value.result.append(filled_region)
            action_return_value.append_message("Filled region created successfully.")
        except Exception as e:
            action_return_value.update_sep(False, "Failed to create filled region with error: {}".format(e))
        return action_return_value

    if transaction_manager:
        transaction = Transaction(doc, "Drawing filled region")
        return_value = transaction_manager(transaction, action)
    else:
        return_value = action()

    return return_value