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

import os
import csv

from duHast.Utilities.Objects.result import Result
from duHast.Utilities.files_csv import write_report_data_as_csv

from duHast.Revit.Family.Utility.family_swap_instances_by_type_utils import write_swap_directives_to_file
from duHast.Revit.Family.Utility.family_copy_directive_utils import write_copy_directives_to_file

from duHast.Revit.Family.Data.Objects.family_directive_copy import FamilyDirectiveCopy

from duHast.Revit.Family.LibraryCleanUp.Utility.defaults import (
    SWAP_DIRECTIVE_FILE_NAME,
    DUPLICATE_COPY_DIRECTIVE_FILE_NAME,
    COPY_DIRECTIVE_FILE_NAME,  
    MAINTAIN_TYPES_BY_FAMILY_FILE_NAME, 
    FAMILIES_WITH_MISSING_GROUP_CODES_FILE_NAME
)


def write_maintain_list(maintain_file_list, output_directory):
    """
    Writes a list of maintain directives to a specified file.

    :param maintain_file_list: List of maintain directives to write.
    :type maintain_file_list: list
    :param output_directory: Directory where the file will be written.
    :type output_directory: str

    :return: Result object indicating success or failure.
    :rtype: Result
    """

    return_value = Result()

    try:
        # build the file path for the maintain directives
        file_path = os.path.join(output_directory, MAINTAIN_TYPES_BY_FAMILY_FILE_NAME)

        print("Writing maintain directives to file: {}".format(file_path))

        # write the maintain directives to the file
        return_value = write_report_data_as_csv(
            file_name=file_path,
            header=[],  # No header needed for maintain directives
            data= maintain_file_list, 
            quoting= csv.QUOTE_MINIMAL,)
        
    except Exception as e:
        return_value.update_sep(
            False,
            "Failed to write maintain directives with exception: {}".format(e),
        )
    
    return return_value


def write_swap_directives(swap_directives, output_directory):
    """
    Writes swap directives to a specified file.

    :param swap_directives: List of swap directives to write.
    :type swap_directives: list
    :param output_directory: Directory where the file will be written.
    :type output_directory: str

    :return: Result object indicating success or failure.
    :rtype: Result
    """

    return_value = Result()

    try:
        # build the file path for the swap directives
        file_path = os.path.join(output_directory, SWAP_DIRECTIVE_FILE_NAME)

        print("Writing swap directives to file: {}".format(file_path))

        # write the swap directives to the file
        return_value = write_swap_directives_to_file(
            swap_directives=swap_directives,
            file_path=file_path
        )

    except Exception as e:
        return_value.update_sep(
            False,
            "Failed to write swap directives with exception: {}".format(e),
        )
    
    return return_value


def write_copy_directives(copy_directives, output_directory):
    """
    Writes copy directives to a specified file.

    :param copy_directives: List of copy directives to write.
    :type swap_directives: list
    :param output_directory: Directory where the file will be written.
    :type output_directory: str

    :return: Result object indicating success or failure.
    :rtype: Result
    """

    return_value = Result()

    try:


        # make sure theses are copy directives
        if not all(isinstance(directive, FamilyDirectiveCopy) for directive in copy_directives):
            return_value.update_sep(
                False,
                "All directives must be of type FamilyDirectiveCopy.",
            )
            return return_value

        # build the file path for the copy directives
        file_path = os.path.join(output_directory, COPY_DIRECTIVE_FILE_NAME)

        print("Writing copy directives to file: {}".format(file_path))

        # write the duplicate copy directives to the file
        return_value = write_copy_directives_to_file(
            copy_directives=copy_directives,
            file_path=file_path
        )

    except Exception as e:
        return_value.update_sep(
            False,
            "Failed to write swap directives with exception: {}".format(e),
        )
    
    return return_value

def write_duplicate_directives_to_file(copy_directives, output_directory):
    """
    Writes duplicate directives to a specified file.

    :param copy_directives: List of duplicate directives to write.
    :type copy_directives: list
    :param output_directory: Directory where the file will be written.
    :type output_directory: str

    :return: Result object indicating success or failure.
    :rtype: Result
    """

    return_value = Result()

    try:

        # make sure theses are copy directives
        if not all(isinstance(directive, FamilyDirectiveCopy) for directive in copy_directives):
            return_value.update_sep(
                False,
                "All directives must be of type FamilyDirectiveCopy.",
            )
            return return_value
        
        # build the file path for the duplicate copy directives
        file_path = os.path.join(output_directory, DUPLICATE_COPY_DIRECTIVE_FILE_NAME)

        print("Writing duplicate directives to file: {}".format(file_path))

        # write the duplicate copy directives to the file
        return_value = write_copy_directives_to_file(
            copy_directives=copy_directives,
            file_path=file_path
        )

    except Exception as e:
        return_value.update_sep(
            False,
            "Failed to write duplicate directives with exception: {}".format(e),
        )
    
    return return_value



def write_directives_to_file(swap_directives, copy_directives, output_directory):
    """
    Writes directives to a specified file.

    :return: Result object indicating success or failure.
    :rtype: Result
    """

    return_value = Result()

    try:
        # write swap directives to file
        result_swap = write_swap_directives(swap_directives, output_directory)
        return_value.update(result_swap)

        # write copy directives to file
        result_copy = write_copy_directives(copy_directives=copy_directives, output_directory=output_directory)
        print(result_copy)
        return_value.update(result_copy)

    except Exception as e:
        return_value.update_sep(
            False,
            "Failed to write directives with exception: {}".format(e),
        )
    
    return return_value


def write_families_with_missing_group_codes (family_instances, output_directory):
    """
    Writes a list of families with missing group codes to a specified file.

    :param family_instances: List of family instances with missing group codes.
    :type family_instances: [FamilyTypeDataStorage]
    :param output_directory: Directory where the file will be written.
    :type output_directory: str
    :return: Result object indicating success or failure.
    :rtype: Result
    """
    return_value = Result()

    try:
        # build the file path for the maintain directives
        file_path = os.path.join(output_directory, FAMILIES_WITH_MISSING_GROUP_CODES_FILE_NAME)

        data = []
        for family_instance in family_instances:
            data.append ([
                family_instance.family_name,
            ])

        # write the list to the file
        return_value = write_report_data_as_csv(
            file_name=file_path,
            header=[],  # No header needed for maintain directives
            data= data, 
            quoting= csv.QUOTE_MINIMAL,)

    except Exception as e:
        return_value.update_sep(
            False,
            "Failed to write list of families with missing group codes with exception: {}".format(e),
        )
        
    return return_value
