'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to Revit views. 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''
#
#License:
#
#
# Revit Batch Processor Sample Code
#
# Copyright (c) 2020  Jan Christel
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
import clr
import System

# import common library modules
#from duHast.APISamples.Common import RevitCommonAPI as com
from duHast.APISamples.Common import RevitTransaction as rTran
from duHast.APISamples.Views import RevitViewFilters as rView
#from duHast.APISamples.Common import RevitElementParameterGetUtils as rParaGet
from duHast.Utilities import Result as res
#from duHast.Utilities import Utility as util

# import Autodesk
import Autodesk.Revit.DB as rdb

# --------------------------- view filters --------------------------------

def remove_filter_from_view(doc, filter, view):
    '''
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
    '''

    return_value = res.Result()
    if (view.ViewType in rView.VIEW_TYPE_WHICH_CAN_HAVE_FILTERS):
        filters_applied = view.GetFilters()
        if(filter.Id in filters_applied):
            def action():
                action_return_value = res.Result()
                try:
                    view.RemoveFilter(filter.Id)
                    action_return_value.UpdateSep(True, 'Remove filter: {} from template: {}'.format(filter.Name, view.Name))
                except Exception as e:
                    action_return_value.UpdateSep(False, 'Failed to remove filter: {} from template: {} with exception: {}'.format(filter.Name, view.Name, e))
                return action_return_value
            transaction = rdb.Transaction(doc,'Removing filter: {}'.format(filter.Name))
		    # execute the transaction
            return_value = rTran.in_transaction(transaction, action)
        else:
            return_value.UpdateSep(True, 'Filter: {} is not applied to view template: {}'.format(filter.Name, view.Name))
    else:
        return_value.UpdateSep(True, 'View template: {} if of type: {} which does not support filters.'.format(view.Name, view.ViewType))
    return return_value