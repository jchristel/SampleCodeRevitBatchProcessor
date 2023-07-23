"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Family shared parameters purge unused utilities.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This will delete all shared parameter definitions which are not used by any family parameter.

- requires a revit shared parameter processor object

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
from duHast.Revit.Family.Data import ifamily_data as IFamData
from duHast.Revit.SharedParameters import shared_parameter_data as rSharedParaData
from duHast.Revit.Categories import categories as rCat
from duHast.Revit.Common import delete as rDel

import Autodesk.Revit.DB as rdb


def purge_unused(doc, processor):
    """
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
    """

    # from processor instance get all root line pattern entries where usage counter == 0.
    # delete those line patterns by id

    return_value = res.Result()

    # check the category of the family first:
    # Tags and generic annotations (may) contain labels which in turn use shared parameters to drive them
    # there is currently no way in the api (Revit 2022) to find out what parameter is driving the label...

    # get the family category name:
    fam_cat_name = list(rCat.get_family_category(doc))[0]
    if fam_cat_name != "Generic Annotations" and fam_cat_name.endswith("Tags") == False:
        ids_to_delete = []
        # get categories found in root processor data only
        root_fam_data = processor._findRootFamilyData()
        # get all root line pattern entries where usage counter == 0.
        for root_fam in root_fam_data:
            if root_fam[IFamData.USAGE_COUNTER] == 0:
                return_value.append_message(
                    "Found unused shared parameter: {} [{}]".format(
                        root_fam[rSharedParaData.PARAMETER_NAME],
                        root_fam[rSharedParaData.PARAMETER_GUID],
                    )
                )
                ids_to_delete.append(
                    rdb.ElementId(root_fam[rSharedParaData.PARAMETER_ID])
                )
        # delete any subcategories found
        if len(ids_to_delete) > 0:
            result_delete = rDel.delete_by_element_ids(
                doc,
                ids_to_delete,
                "Deleting unused shared parameters.",
                "Shared Parameters",
            )
            return_value.update(result_delete)
            # may need to delete shared parameters one by one if one or more cant be deleted
            if result_delete.status == False:
                result_delete_one_by_one = rDel.delete_by_element_ids_one_by_one(
                    doc,
                    ids_to_delete,
                    "Deleting unused shared parameters: one by one.",
                    "Shared Parameters",
                )
                return_value.update(result_delete_one_by_one)
        else:
            return_value.update_sep(
                True, "No unused shared parameters found. Nothing was deleted."
            )
    else:
        return_value.update_sep(
            True,
            "This is an annotation family (tag or generic annotation). Due to limitations in the Revit API no shared parameter was purged.",
        )
    return return_value
