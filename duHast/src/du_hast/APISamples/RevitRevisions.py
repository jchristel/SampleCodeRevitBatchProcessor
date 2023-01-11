'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to Revit revisions.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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

import clr
import System
from collections import namedtuple

import RevitCommonAPI as com
import Result as res

# import Autodesk
import Autodesk.Revit.DB as rdb

# tuples containing revision information
revisionData = namedtuple('revisionData', 'description issuedBy issuedTo revisionNumberType revisionDate tagCloudVisibility')


def CreateRevision (doc, revData):
    '''
    Creates a revision in the document.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param revData: Named tuple containing revision data
    :type revData: :class:`.revisionData`

    :return:  
        Result class instance.
        
        - Revision status returned in result.status. False if an exception occurred, otherwise True.
        - result.message will contain the message revision created successfully.
        - result.result: will contain list with single entry: the new revision created
        
        On exception:
        
        - result.status (bool) will be False.
        - result.message will contain the exception message.
    
    :rtype: :class:`.Result`
    '''

    returnValue = res.Result()
    def action():
        actionReturnValue = res.Result()
        try:
            newRevision = rdb.Revision.Create(doc)
            newRevision.Description = revData.description
            newRevision.IssuedBy = revData.issuedBy
            newRevision.IssuedTo = revData.issuedTo
            newRevision.NumberType = revData.revisionNumberType
            newRevision.RevisionDate = revData.revisionDate
            newRevision.Visibility = revData.tagCloudVisibility #rdb.RevisionVisibility.Hidden
            actionReturnValue.result.append(newRevision)
            actionReturnValue.UpdateSep(True, 'Created new revision in document.')
        except Exception as e:
            actionReturnValue.UpdateSep(False, 'Failed to create new revision in document!')
        return actionReturnValue
    transaction = rdb.Transaction(doc, "adding revision to file")
    returnValue = com.InTransaction(transaction, action)
    return returnValue