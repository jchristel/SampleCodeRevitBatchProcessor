'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a transaction group wrapper for revit test functions. 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Any modification of the revit model through test function past in will be rolled back so the next test 
finds the model in a pre-defined state.

'''
#
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
#

# import Autodesk
import Autodesk.Revit.DB as rdb

def in_transaction_group(doc, action):
    '''
    Encapsulates action in a transaction group which will be rolled back.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param action: An action taking the document as an argument only.
    :type action: foo(doc)
    :return: A flag indicating the action was completed successfully and a message from the action.
    :rtype: bool, str
    '''

    # create a transaction group
    tg = rdb.TransactionGroup(doc, "test")
    tg.Start()

    flag, message = action(doc)
    
    # roll every thing back
    tg.RollBack()

    return flag, message