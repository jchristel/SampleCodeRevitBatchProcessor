"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Helper functions to read copy  directives file(s) and return them to the caller
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

These helper function expect a text file in csv format with 5 columns:

- CURRENT_FAMILY_NAME = 0
- FAMILY_FILE_PATH = 1
- CATEGORY = 2
- NEW_FAMILY_NAME = 3
- NEW_DIRECTORY = 4

Note:

- There is no header row in the file, so all rows are treated as data rows.

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

import os


from duHast.Utilities import files_csv as fileCSV, files_get as fileGet
from duHast.Utilities.files_io import copy_file, file_exist
from duHast.Utilities.Objects import result as res
from duHast.Revit.Family.Data.Objects.family_directive_copy import FamilyDirectiveCopy


def get_copy_directives(directory_path):
    """
    Retrieves file rename  directives from a given folder location.

    :param directory_path: Fully qualified folder path to folder containing directives.
    :type directory_path: str

    :return:
        Result class instance.

        - result.status. True if rename directives where found and loaded successfully, otherwise False.
        - result.message will contain number of directives found in format:'Found rename directives: ' + number
        - result.result list of directives

        On exception:

        - result.status (bool) will be False.
        - result.message will contain an exception message.
        - result.result will be empty

    :rtype: :class:`.Result`
    """

    return_value = res.Result()
    # check whether csv files matching file name filter exist in directory path
    rename_directive_files = fileGet.get_files_from_directory_walker_with_filters(
        directory_path,
        FamilyDirectiveCopy.COPY_DIRECTIVE_FILE_NAME_PREFIX,
        "",
        FamilyDirectiveCopy.COPY_DIRECTIVE_FILE_EXTENSION,
    )

    # check whether any files where found?
    if len(rename_directive_files) > 0:
        # attempt to re rename directives from files
        rename_directives =get_copy_directives(rename_directive_files)
        # check whether any rename directives where found in files
        if len(rename_directives) > 0:
            return_value.update_sep(
                True, "Found copy directives: {}".format(len(rename_directives))
            )
            # store rename directives in result object
            return_value.result = rename_directives
        else:
            return_value.update_sep(
                False, FamilyDirectiveCopy.EXCEPTION_EMPTY_COPY_DIRECTIVE_FILES
            )
    else:
        return_value.update_sep(
            False, FamilyDirectiveCopy.EXCEPTION_NO_COPY_DIRECTIVE_FILES
        )

    return return_value

def get_copy_directives(files):
    """
    Reads list of copy directives from files.

    :param filePath: List of fully qualified file path to copy and rename directives file.
    :type filePath: [str]
    :return: List of copy and rename directives.
    :rtype: [copy_and_rename_directive]
    """

    copy_and_rename_directives = []

    for file in files:
        rows_result = fileCSV.read_csv_file(file)
        # check whether file was read successfully
        if rows_result.status is False:
            return copy_and_rename_directives
        
        rows = rows_result.result
        
        # read rows in tuples ignoring the header row
        for i in range(0, len(rows)):
            data = None
            if len(rows[i]) == 5:
                data = FamilyDirectiveCopy(
                    name=rows[i][
                        FamilyDirectiveCopy. COPY_DIRECTIVE_LIST_INDEX_CURRENT_FAMILY_NAME
                    ],
                    source_file_path=rows[i][
                        FamilyDirectiveCopy.COPY_DIRECTIVE_INDEX_FAMILY_FILE_PATH
                    ],
                    category=rows[i][
                        FamilyDirectiveCopy.COPY_DIRECTIVE_INDEX_CATEGORY
                    ],
                    new_name=rows[i][
                        FamilyDirectiveCopy.COPY_DIRECTIVE_LIST_INDEX_NEW_FAMILY_NAME
                    ],
                    target_directory=rows[i][
                        FamilyDirectiveCopy.COPY_DIRECTIVE_LIST_INDEX_NEW_DIRECTORY
                    ],
                )
            else:
                continue

            copy_and_rename_directives.append(data)
    return copy_and_rename_directives


def execute_copy_directives(copy_directives):
    """
    Executes copy directives.

    :param copy_directives: List of copy directives to execute.
    :type copy_directives: [FamilyDirectiveCopy]
    :return: Result object with status and messages.
    :rtype: :class:`.Result`
    """

    # create result object
    return_value = res.Result()

    try:
        for directive in copy_directives:
            # execute copy directive
            if (file_exist(directive.source_file_path) is False):
                return_value.update_sep(
                    False,
                    "File does not exist: {}".format(directive.source_file_path),
                )
                continue


            target_file_path = None
            # attempt to copy the file
            if directive.target_directory is not None:
                target_file_path = os.path.join(
                    directive.target_directory, directive.new_name
                )
            else:
                return_value.update_sep(
                    False,
                    "No target directory path provided for copy directive: {}".format(directive.name))
                continue

            print("copy target file path: {}".format(target_file_path))
            # copy file to target directory
            copy_file_flag = copy_file(
                directive.source_file_path, target_file_path
            )
            
            if copy_file_flag is False:
                return_value.update_sep(
                    False,
                    "Failed to copy file from {} to {}".format(
                        directive.source_file_path, target_file_path
                    ),
                )
            else:
                return_value.append_message(
                    "Copied file from \n{} to \n{}".format(
                        directive.source_file_path, target_file_path
                    )
                )
           
        pass
    except Exception as e:
        return_value.update_sep(
            False,
            "Failed to get family data with exception: {}".format(e),
        )
    
    return return_value


def write_copy_directives_to_file(copy_directives, file_path):
    """
    Writes copy directives to a specified file in CSV format.

    :param swap_directives: List of swap directives to write to file.
    :type swap_directives: list of FamilyDirectiveSwap
    :param file_path: Fully qualified file path where the directives will be written.
    :type file_path: str
    :return: Result object indicating success or failure of the write operation.
    :rtype: Result
    """
    
    return_value = res.Result()


    # loop over directives and convert them to a list of lists
    copy_directives_list = []
    try:
        for directive in copy_directives:

            copy_directives_list.append([
                directive.name,
                directive.source_file_path,
                directive.category,
                directive.new_name,
                directive.target_directory,
            ])

        # write the directives to the file
        return_value = fileCSV.write_report_data_as_csv(
            file_name=file_path,
            header = [],
            data=copy_directives_list,
            quoting=fileCSV.csv.QUOTE_MINIMAL,
        )

    except Exception as e:
        return_value.update_sep(
            False,
            "Failed to write copy directives with exception: {}".format(e),
        )
    
    return return_value