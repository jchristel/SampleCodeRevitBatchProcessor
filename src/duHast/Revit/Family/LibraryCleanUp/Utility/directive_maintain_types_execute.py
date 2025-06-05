# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2025, Jan Christel
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

from duHast.Utilities.Objects.result import Result
from duHast.Revit.Family.family_types import get_all_family_type_names, delete_family_type

def get_names_of_types_to_keep(family_name, maintain_types_list):

    types_to_keep = []
    search_name = "{}.rfa".format(family_name)

    # loop over maintain types list and find the family name
    for family_type_row in maintain_types_list:
        if family_type_row[0] == search_name:
            types_to_keep.append(family_type_row[1])

    return types_to_keep


def delete_non_conforming_types(doc, maintain_types_list):
    """
    Delete non-conforming types in a family document based on a list of types to maintain.

    :param doc: The family document to process.
    :type doc: :class:`Autodesk.Revit.DB.Document`
    :param maintain_types_list: A list of types to maintain, where each entry is a tuple (family_name, type_name).
    :type maintain_types_list: list of nested lists, each containing two strings: [family_name, type_name]

    :return: Result object containing the status and messages.
    :rtype: :class:`duHast.Utilities.Objects.result.Result`
    """
    return_value = Result()

    try:
        # get the family name
        family_name = doc.Title

        # build list of types to keep
        types_to_keep = get_names_of_types_to_keep(family_name, maintain_types_list)

        all_type_names_result = get_all_family_type_names(doc)

        if (not all_type_names_result.status):
            return_value.update_sep(
                False,
                "Failed to get all family type names: {}".format(all_type_names_result.message),
            )
            return return_value
        
        # get all type names in family
        all_type_names = all_type_names_result.result

        # get list of names to delete
        types_to_delete = [name for name in all_type_names if name not in types_to_keep]

        if len(types_to_delete) == 0:
            return_value.update_sep(
                True,
                "No types to delete in family '{}'.".format(family_name),
            )
            return return_value
        
        # delete types
        for type_name in types_to_delete:
            print("Deleting type '{}' in family '{}'...".format(type_name, family_name))
            delete_result = delete_family_type(doc, type_name)
            if not delete_result.status:
                return_value.append_message(
                    "Failed to delete type '{}': {}".format(type_name, delete_result.message)
                )
            else:
                return_value.append_message(
                    "Deleted type '{}' successfully.".format(type_name)
                )

        
    except Exception as e:
        return_value.update_sep(
            False,
            "Failed to delete non confirming types: {}".format(e),
        )
    
    return return_value