'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Revit transaction wrapper utility functions.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

#!/usr/bin/python
# -*- coding: utf-8 -*-
#License:
#
#
# Revit Batch Processor Sample Code
#
# Copyright (c) 2023  Jan Christel
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

# class used for stats reporting
from duHast.Utilities import Result as res

# type checker
#from typing import List, Callable

#--------------------------------------------Transactions-----------------------------------------

def in_transaction(
    tranny, # 
    action, # type: Callable[[], res.Result]
    doc = None    # used as placeholder...
    ):
    # type: (...) -> res.Result
    '''
    Revit transaction wrapper.

    This function is used to execute any actions requiring a transaction in the Revit api. On exception this will roll back the transaction.

    :param tranny: The transaction to be executed.
    :type tranny: Autodesk.Revit.DB.Transaction 
    :param doc: The current model document. (not used in this function)
    :type doc: Autodesk.Revit.DB.Document 
    :param action: The action to be nested within the transaction. This needs to return a Result class instance!
    :type action: action().
    
    :return: 
        Result class instance.
        
        - .result = True if successfully executed transaction, otherwise False.
        
    :rtype: :class:`.Result`
    '''

    return_value = res.Result()
    try:
        tranny.Start()
        try:
            tranny_result = action()
            tranny.Commit()
            # check what came back
            if (tranny_result != None):
                # store false value 
                return_value = tranny_result
        except Exception as e:
            tranny.RollBack()
            return_value.UpdateSep(False, 'Failed with exception: {}'.format(e))
    except Exception as e:
        return_value.UpdateSep(False, 'Failed with exception: {}'.format(e))
    return return_value