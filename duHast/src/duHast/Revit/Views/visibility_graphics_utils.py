"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to Revit views. 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright © 2023, Jan Christel
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

# import common library modules
# from duHast.APISamples.Common import RevitCommonAPI as com
from duHast.Revit.Common import transaction as rTran
from duHast.Revit.Views import filters as rView

# from duHast.APISamples.Common import RevitElementParameterGetUtils as rParaGet
from duHast.Utilities.Objects import result as res

# from duHast.Utilities import Utility as util

# import Autodesk
import Autodesk.Revit.DB as rdb

# --------------------------- view filters --------------------------------


def remove_filter_from_view(doc, filter, view):
    """
    Removes a filter from a view.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param filter: The filter to be removed from the view.
    :type filter: Autodesk.Revit.DB.ParameterFilterElement
    :param view: The view (can be a view template too!)
    :type view: Autodesk.Revit.DB.View
    :return:
        Result class instance.

        - .result True if filter was removed successfully or if filter was not applied or if view does not support filters, otherwise False
        - .message will contain deletion status.
        - . result (empty list)

        on exception:

        - .result Will be False
        - .message will contain exception message.
        - . result (empty list)

    :rtype: :class:`.Result`
    """

    return_value = res.Result()
    if view.ViewType in rView.VIEW_TYPE_WHICH_CAN_HAVE_FILTERS:
        filters_applied = view.GetFilters()
        if filter.Id in filters_applied:

            def action():
                action_return_value = res.Result()
                try:
                    view.RemoveFilter(filter.Id)
                    action_return_value.update_sep(
                        True,
                        "Remove filter: {} from template: {}".format(
                            filter.Name, view.Name
                        ),
                    )
                except Exception as e:
                    action_return_value.update_sep(
                        False,
                        "Failed to remove filter: {} from template: {} with exception: {}".format(
                            filter.Name, view.Name, e
                        ),
                    )
                return action_return_value

            transaction = rdb.Transaction(
                doc, "Removing filter: {}".format(filter.Name)
            )
            # execute the transaction
            return_value = rTran.in_transaction(transaction, action)
        else:
            return_value.update_sep(
                True,
                "Filter: {} is not applied to view template: {}".format(
                    filter.Name, view.Name
                ),
            )
    else:
        return_value.update_sep(
            True,
            "View template: {} if of type: {} which does not support filters.".format(
                view.Name, view.ViewType
            ),
        )
    return return_value
