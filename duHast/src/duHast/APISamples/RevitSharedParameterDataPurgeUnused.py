'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Family shared parameters purge unused utilities.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This will delete all shared parameter definitions which are not used by any family parameter.

- requires a revit shared parameter processor object

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
from duHast.APISamples import RevitSharedParameterData as rSharedData
from duHast.APISamples import RevitCategories as rCat

import Autodesk.Revit.DB as rdb

def PurgeUnused(doc, processor):
    '''
    This will delete all shared parameter definitions which are not used by any family parameter in the family or nested families.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param processor: An RevitSharedParameterDataProcessor object containing all shared parameter information of the family document and any nested families.
    :type processor: :class:`.SharedParameterProcessor`

    :return: 
        Result class instance.

        - True if all unused shared parameters where deleted successfully or none needed to be deleted. Otherwise False.
        - Result.message property updated in format: Found unused shared parameter: shared parameter Name [GUID] 
        
        On exception:
        
        - status (bool) will be False.
        - message will contain the exception message.

    :rtype: :class:`.Result`
    '''

    # from processor instance get all root line pattern entries where usage counter == 0.
    # delete those line patterns by id

    returnValue = res.Result()

    # check the category of the family first:
    # Tags and generic annotations (may) contain labels which in turn use shared parameters to drive them
    # there is currently no way in the api (Revit 2022) to find out what parameter is driving the label...

    # get the family category name:
    famCatName = list(rCat.GetFamilyCategory(doc))[0]
    if(famCatName != 'Generic Annotations' and famCatName.endswith( 'Tags') == False):
        idsToDelete = []
        # get categories found in root processor data only
        rootFamData = processor._findRootFamilyData()
        # get all root line pattern entries where usage counter == 0.
        for rootFam in rootFamData:
            if (rootFam[IFamData.USAGE_COUNTER] == 0 ):
                returnValue.AppendMessage('Found unused shared parameter: ' + rootFam[rSharedParaData.PARAMETER_NAME] + ' [' +str(rootFam[rSharedParaData.PARAMETER_GUID])+']')
                idsToDelete.append(rdb.ElementId(rootFam[rSharedParaData.PARAMETER_ID]))
        # delete any subcategories found
        if(len(idsToDelete) > 0):
            resultDelete = com.DeleteByElementIds(doc, idsToDelete, 'Deleting unused shared parameters.', 'Shared Parameters')
            returnValue.Update(resultDelete)
            # may need to delete shared parameters one by one if one or more cant be deleted
            if (resultDelete.status == False):
                resultDeleteOneByOne = com.DeleteByElementIdsOneByOne(doc, idsToDelete, 'Deleting unused shared parameters: one by one.', 'Shared Parameters')
                returnValue.Update(resultDeleteOneByOne)
        else:
            returnValue.UpdateSep(True, 'No unused shared parameters found. Nothing was deleted.')
    else:
        returnValue.UpdateSep(True, 'This is an annotation family (tag or generic annotation). Due to limitations in the Revit API no shared parameter was purged.')
    return returnValue