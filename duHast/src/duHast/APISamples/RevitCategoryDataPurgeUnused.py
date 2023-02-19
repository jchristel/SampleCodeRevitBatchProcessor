'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Family category purge unused utilities.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This will delete all subcategories which are user created ( id greater then 0) and are not used by any element in the family or nested families.

- requires a revit category processor object

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
from duHast.APISamples import RevitCategoryData as rCatData

import Autodesk.Revit.DB as rdb

def PurgeUnused(doc, processor):
    '''
    This will delete all subcategories which are user created ( id greater then 0) and are not used by any element in the family or nested families.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param processor: An CategoryProcessor object containing all subcategory information of the family document and any nested families.
    :type processor: :class:`.CategoryProcessor'

    :return: 
        Result class instance.

        - True if all unused subcategories where deleted successfully or none needed to be deleted. Otherwise False.
        - Result.message property updated in format: Found unused sub category: family category Name : subcategory Name [subcategory Id] 
        
        On exception:
        
        - status (bool) will be False.
        - message will contain the exception message.

    :rtype: :class:`.Result`
    '''

    # from processor instance get all root category entries where usage counter == 0 and subCategoryId > 0 (pointing to a custom sub category and not a built in one).
    # delete those subcategories by id

    returnValue = res.Result()

    idsToDelete = []
    # get categories found in root processor data only
    rootFamData = processor._findRootFamilyData()
    # get all root category entries where usage counter == 0 and subCategoryId > 0 (pointing to a custom sub category and not a built in one).
    for rootFam in rootFamData:
        if (rootFam[IFamData.USAGE_COUNTER] == 0 and rootFam[rCatData.SUB_CATEGORY_ID] > 0):
            returnValue.AppendMessage('Found unused sub category: ' + rootFam[rCatData.CATEGORY_NAME] + ':' + rootFam[rCatData.SUB_CATEGORY_NAME] +' ['+str(rootFam[rCatData.SUB_CATEGORY_ID])+']')
            idsToDelete.append(rdb.ElementId(rootFam[rCatData.SUB_CATEGORY_ID]))
    # delete any subcategories found
    if(len(idsToDelete) > 0):
        resultDelete = com.DeleteByElementIds(doc, idsToDelete, 'Deleting unused sub categories.', 'Subcategories')
        returnValue.Update(resultDelete)
    else:
        returnValue.UpdateSep(True, 'No unused categories found. Nothing was deleted.')
    return returnValue
    