"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Family line pattern purge unused utilities.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This will delete all line patterns which are not used by any element in the family or nested families.

- requires a revit line pattern processor object

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

# class used for stats reporting
from duHast.Utilities.Objects import result as res
from duHast.Revit.Common import delete as rDel
from duHast.Revit.Family.Data import ifamily_data as IFamData
from duHast.Revit.LinePattern import line_pattern_data as rLinePatData

import Autodesk.Revit.DB as rdb


def purge_unused(doc, processor):
    """
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
    """

    # from processor instance get all root line pattern entries where usage counter == 0.
    # delete those line patterns by id

    return_value = res.Result()

    ids_to_delete = []
    # get categories found in root processor data only
    root_fam_data = processor._findRootFamilyData()
    # get all root line pattern entries where usage counter == 0.
    for root_fam in root_fam_data:
        if root_fam[IFamData.USAGE_COUNTER] == 0:
            return_value.append_message(
                "Found unused line patterns: {} [{}]".format(
                    root_fam[rLinePatData.PATTERN_NAME],
                    root_fam[rLinePatData.PATTERN_ID],
                )
            )
            ids_to_delete.append(rdb.ElementId(root_fam[rLinePatData.PATTERN_ID]))
    # delete any subcategories found
    if len(ids_to_delete) > 0:
        result_delete = rDel.delete_by_element_ids(
            doc, ids_to_delete, "Deleting unused line patterns.", "Line patterns"
        )
        return_value.update(result_delete)
    else:
        return_value.update_sep(
            True, "No unused line patterns found. Nothing was deleted."
        )
    return return_value
