"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Helper functions to rename family loaded family types in a project file or family file.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This helper function expect a folder containing rename directive files. For format of those files refer to module family_rename_files_utils.


"""

#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2023, Jan Christel
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

# import clr
# import System

from duHast.Utilities.Objects.result import Result
from duHast.Revit.Family.Utility import family_rename_types_utils as rFamRenameUtils
from duHast.Revit.Family.Data.Objects.family_base_data_processor_defaults  import NESTING_SEPARATOR
from duHast.Revit.Common import transaction as rTran

from Autodesk.Revit.DB import Element, Transaction


def _rename_loaded_family_types(doc, rename_directives, families, progress_callback=None):
    """
    Loops over families and if a match in rename directives is found will rename the family type accordingly.

    :param doc: The current family document.
    :type doc: Autodesk.Revit.DB.Document
    :param rename_directives: List of rename directives.
    :type rename_directives: [rename_directive]
    :param family_ids: dictionary of families where key is concatenated name + category and value is the family element.
    :type family_ids: {str:Autodesk.Revit.DB.Family}

    :return:
        Result class instance.

        - result.status. True if all families where renamed successfully, otherwise False.
        - result.message will contain each rename messages in format 'Renamed family from :' +current Name + ' to ' + newName.
        - result.result empty list

        On exception:

        - result.status (bool) will be False.
        - result.message will contain an exception message in format: 'Failed to rename family from :' + currentName + ' to ' + newName
        - result.result will be empty

    :rtype: :class:`.Result`
    """

    return_value = Result()
    return_value.status = False
    rename_match_counter = 0

    # progress call back
    callback_counter = 1

    for rename_directive in rename_directives:

        # update progress
        if progress_callback != None:
            progress_callback.update(callback_counter, len(rename_directives))

        fam_key = "{}{}{}".format(rename_directive.name,NESTING_SEPARATOR,rename_directive.category)
        # check if match for rename directive
        if fam_key in families:

            # set counter indicating that at least one family was renamed
            rename_match_counter = rename_match_counter + 1

            # get the family
            family = families[fam_key]

            # reset flag
            found_type_name_match = False

            # get the type to rename
            for fam_type_id in family.GetFamilySymbolIds():
                family_type = doc.GetElement(fam_type_id)
                if Element.Name.GetValue(family_type)== rename_directive.old_type_name:
                    # flag that a match was found
                    found_type_name_match = True
                    # rename this family type
                    def action():
                        action_return_value = Result()
                        try:
                            # rename the type
                            family_type.Name = rename_directive.new_type_name
                                    
                            # give user feedback
                            if not found_type_name_match:
                                action_return_value.append_message("No match found for family [{}] of category [{}] vs directive category [{}] type: [{}] ".format(
                                    rename_directive.name,
                                    family.FamilyCategory.Name,
                                    rename_directive.category,
                                    rename_directive.old_type_name
                                ))
                            else:
                                action_return_value.update_sep(
                                    True,
                                    "Renamed family [{}] of category [{}] vs directive category [{}] from: [{}] to: [{}]".format(
                                        rename_directive.name,
                                        family.FamilyCategory.Name,
                                        rename_directive.category,
                                        rename_directive.old_type_name,
                                        rename_directive.new_type_name,
                                    ),
                                )
                        except Exception as e:
                            action_return_value.update_sep(
                                False,
                                "Failed to rename type of family [{}] of category [{}] vs directive category [{}] from: [{}] to: [{}]".format(
                                        rename_directive.name,
                                        family.FamilyCategory.Name,
                                        rename_directive.category,
                                        rename_directive.old_type_name,
                                        rename_directive.new_type_name,
                                    ),
                                )
                        return action_return_value

                    # start a transaction and rename the type
                    transaction = Transaction(doc, "Renaming: {} {}".format(rename_directive.name, rename_directive.old_type_name))
                    rename_result = rTran.in_transaction(transaction, action)
                    if rename_result.status:
                        # make sure that this returns true as soon as one family renamed successfully
                        return_value.status = True
                    # update messages
                    return_value.append_message(rename_result.message)
                    
                    # exit inner for loop
                    break
            
            if not found_type_name_match:
                return_value.append_message("No match found for family [{}] of category [{}] vs directive category [{}] type: [{}] ".format(
                    rename_directive.name,
                    family.FamilyCategory.Name,
                    rename_directive.category,
                    rename_directive.old_type_name
                ))
                
        else:
            # flag no match found
            return_value.append_message(
                "No match for rename directive for of name: {} and category: {} found.".format(
                    rename_directive.name, rename_directive.category
                )
            )

        # check for user cancel
        if progress_callback != None:
            if progress_callback.is_cancelled():
                return_value.append_message("User cancelled!")
                break
        # progress call back
        callback_counter += 1

    # check if anything got renamed at all
    if rename_match_counter == 0:
        return_value.append_message(
            "No match for rename directives found. Nothing was renamed."
        )
    return return_value


def rename_loaded_family_types(doc, directory_path):
    """
    Entry point for this module. Will read rename directives files in given directory and attempt to rename
    loaded family types accordingly.

    Note: for rename directive file structure refer to module family_rename_files_utils

    :param directory_path: Fully qualified directory path to where rename directive files are located.
    :type directory_path: str
    :return:
        Result class instance.

        - result.status. True if a single families was renamed successfully, otherwise False.
        - result.message will contain each rename messages in format 'Renamed family from :' +current Name + ' to ' + newName.
        - result.result empty list

        On exception:

        - result.status (bool) will be False.
        - result.message will contain an exception message in format: 'Failed to rename family from :' + currentName + ' to ' + newName
        - result.result will be empty

    :rtype: :class:`.Result`
    """

    return_value = Result()
    # get directives from folder
    rename_directives_result = rFamRenameUtils.get_rename_directives(directory_path)
    # check if anything came back
    if rename_directives_result.status:
        rename_directives = rename_directives_result.result
        # get all family in file
        families = get_name_and_category_to_family_dict(doc)
        # check if any families are loaded
        if len(families) > 0:
            # rename files as per directives
            return_value = _rename_loaded_family_types(
                doc=doc, rename_directives=rename_directives, families=families
            )
        else:
            return_value.update_sep(True, "Mo loadable families in file.")
    else:
        return_value = rename_directives_result

    return return_value