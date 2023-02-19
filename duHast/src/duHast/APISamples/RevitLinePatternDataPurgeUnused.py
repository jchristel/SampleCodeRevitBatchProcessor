'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Family line pattern purge unused utilities.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This will delete all line patterns which are not used by any element in the family or nested families.

- requires a revit line pattern processor object

'''
#
#License:
#
#
# Revit Batch Processor Sample Code
#
# Copyright (c) 2022  Jan Christel
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

# class used for stats reporting
from duHast.Utilities import Result as res
from duHast.APISamples import RevitCommonAPI as com
from duHast.APISamples import IFamilyData as IFamData
from duHast.APISamples import RevitLinePatternData as rLinePatData

import Autodesk.Revit.DB as rdb

def PurgeUnused(doc, processor):
    '''
    This will delete all line patterns which are not used by any element in the family or nested families.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param processor: An LinePatternProcessor object containing all line pattern information of the family document and any nested families.
    :type processor: :class:`.LinePatternProcessor'

    :return: 
        Result class instance.

        - True if all unused line patterns where deleted successfully or none needed to be deleted. Otherwise False.
        - Result.message property updated in format: Found unused line pattern: line pattern Name [subcategory Id] 
        
        On exception:
        
        - status (bool) will be False.
        - message will contain the exception message.

    :rtype: :class:`.Result`
    '''

    # from processor instance get all root line pattern entries where usage counter == 0.
    # delete those line patterns by id

    returnValue = res.Result()

    idsToDelete = []
    # get categories found in root processor data only
    rootFamData = processor._findRootFamilyData()
    # get all root line pattern entries where usage counter == 0.
    for rootFam in rootFamData:
        if (rootFam[IFamData.USAGE_COUNTER] == 0 ):
            returnValue.AppendMessage('Found unused line patterns: ' + rootFam[rLinePatData.PATTERN_NAME] + ' ['+str(rootFam[rLinePatData.PATTERN_ID])+']')
            idsToDelete.append(rdb.ElementId(rootFam[rLinePatData.PATTERN_ID]))
    # delete any subcategories found
    if(len(idsToDelete) > 0):
        resultDelete = com.DeleteByElementIds(doc, idsToDelete, 'Deleting unused line patterns.', 'Line patterns')
        returnValue.Update(resultDelete)
    else:
        returnValue.UpdateSep(True, 'No unused line patterns found. Nothing was deleted.')
    return returnValue
    