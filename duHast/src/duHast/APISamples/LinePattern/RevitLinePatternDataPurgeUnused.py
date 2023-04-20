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
from duHast.APISamples.Common import RevitDeleteElements as rDel
from duHast.APISamples.Family.Reporting import IFamilyData as IFamData
from duHast.APISamples.LinePattern import RevitLinePatternData as rLinePatData

import Autodesk.Revit.DB as rdb

def purge_unused(doc, processor):
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

    return_value = res.Result()

    ids_to_delete = []
    # get categories found in root processor data only
    root_fam_data = processor._findRootFamilyData()
    # get all root line pattern entries where usage counter == 0.
    for root_fam in root_fam_data:
        if (root_fam[IFamData.USAGE_COUNTER] == 0 ):
            return_value.append_message('Found unused line patterns: {} [{}]'.format(root_fam[rLinePatData.PATTERN_NAME],root_fam[rLinePatData.PATTERN_ID]))
            ids_to_delete.append(rdb.ElementId(root_fam[rLinePatData.PATTERN_ID]))
    # delete any subcategories found
    if(len(ids_to_delete) > 0):
        result_delete = rDel.delete_by_element_ids(doc, ids_to_delete, 'Deleting unused line patterns.', 'Line patterns')
        return_value.update(result_delete)
    else:
        return_value.update_sep(True, 'No unused line patterns found. Nothing was deleted.')
    return return_value
    