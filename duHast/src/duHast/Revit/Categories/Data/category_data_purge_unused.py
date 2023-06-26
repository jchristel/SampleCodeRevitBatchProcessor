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
from duHast.Utilities.Objects import result as res
from duHast.Revit.Common import delete as rDel
from duHast.Revit.Family.Data import ifamily_data as IFamData
from duHast.Revit.Categories import category_data as rCatData

import Autodesk.Revit.DB as rdb

def purge_unused_sub_categories(doc, processor):
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

    return_value = res.Result()

    ids_to_delete = []
    # get categories found in root processor data only
    root_fam_data = processor._findRootFamilyData()
    # get all root category entries where usage counter == 0 and subCategoryId > 0 (pointing to a custom sub category and not a built in one).
    for root_fam in root_fam_data:
        if (root_fam[IFamData.USAGE_COUNTER] == 0 and root_fam[rCatData.SUB_CATEGORY_ID] > 0):
            return_value.append_message('Found unused sub category: {} : {} [{}]'.format(root_fam[rCatData.CATEGORY_NAME],root_fam[rCatData.SUB_CATEGORY_NAME],(root_fam[rCatData.SUB_CATEGORY_ID])))
            ids_to_delete.append(rdb.ElementId(root_fam[rCatData.SUB_CATEGORY_ID]))
    # delete any subcategories found
    if(len(ids_to_delete) > 0):
        result_delete = rDel.delete_by_element_ids(doc, ids_to_delete, 'Deleting unused sub categories.', 'Subcategories')
        return_value.update(result_delete)
    else:
        return_value.update_sep(True, 'No unused categories found. Nothing was deleted.')
    return return_value
    