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
from duHast.Revit.Family.LibraryCleanUp.Utility.directives_write_to_file import write_duplicate_directives_to_file, write_families_with_missing_group_codes


def verify_copy_directives_are_unique(copy_directives):

    """
    Verify that the copy directives are unique based on their new names.

    :param copy_directives: A list of copy directives to verify.
    :type copy_directives: list[:class:`.FamilyDirectiveCopy`]
    
    :return: True if all copy directives are unique, False otherwise.
    :rtype: bool
    """
    
    seen_names = set()
    duplicate_directive_new_names = []
    duplicate_directives = []

    # find all duplicate new names
    for directive in copy_directives:
        if directive.new_name in seen_names:
            duplicate_directive_new_names.append(directive.new_name)
            continue
        seen_names.add(directive.new_name)
    
    # get all directive with duplicate new names
    for directive in copy_directives:
        if directive.new_name in duplicate_directive_new_names:
            duplicate_directives.append(directive)


    return duplicate_directives

def check_directives(output_path, copy_directives, families_with__missing_group_codes = None):
    """
    Check the copy directives for duplicates and missing group codes.
    :param output_path: The path where the output files will be written.
    :type output_path: str
    :param copy_directives: A list of copy directives to check.
    :type copy_directives: list[:class:`.FamilyDirectiveCopy`]
    :param families_with__missing_group_codes: A list of families with missing group codes.
    :type families_with__missing_group_codes: list[:class:`.FamilyTypeDataStorageManager`]
    
    :return: A Result object containing the status and messages of the checks.
    :rtype: :class:`.Result`
    """

    return_value = Result()
    try:

        # check missing group codes
        if families_with__missing_group_codes is not None and len(families_with__missing_group_codes) > 0:
            return_value.update_sep(
                False,
                "Found families with missing group codes. Please check the output file for details.",
            )
            write_missing_result = write_families_with_missing_group_codes(families_with__missing_group_codes, output_path)
            return_value.append_message(
                write_missing_result.message,
            )

        else:
            return_value.append_message(
                "No families with missing group codes found."
            )

        # check if families with missing group codes are provided
        duplicate_directives = verify_copy_directives_are_unique(copy_directives)

        # check if any duplicate copy directives were found
        if len(duplicate_directives) > 0:

            return_value.update_sep(
                False,
                "Found duplicate copy directives with the same new name. Please check the output file for details.",
            )
            # write duplicate directives to file
            write_duplicate_directives_result = write_duplicate_directives_to_file(duplicate_directives, output_path)

            return_value.append_message(
                write_duplicate_directives_result.message,
            )

        else:
            return_value.append_message(
                "No duplicate copy directives found."
            )

    except Exception as e:
        return_value.update_sep(
            False,
            "Failed to check directives with exception: {}".format(e),
        )
       
    return return_value