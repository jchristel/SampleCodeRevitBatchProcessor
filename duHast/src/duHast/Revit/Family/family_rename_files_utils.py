"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Helper functions to read rename directives file(s) and return them as a tuple to the caller
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

These helper function expect a text file in csv format with 4 columns:

- Current family name: with out the file extension
- File path	: fully qualified file path to the family file.
- Family category: the Revit category of the family.
- New family name: the new family name without the file extension.

Note:

- First row is treated as a header row and its content is ignored.

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

import clr
import System
from collections import namedtuple
from duHast.Utilities.Objects.timer import Timer

from duHast.Utilities import files_csv as fileCSV, files_get as fileGet
from duHast.Utilities.Objects import result as res
from duHast.Revit.Family.Data import family_base_data_utils as rFamBaseDUtils


# tuples containing rename directive read from file
rename_directive = namedtuple("rename_directive", "name filePath category newName")

# row structure of rename directive file

RENAME_DIRECTIVE_LIST_INDEX_CURRENT_FAMILY_NAME = 0
RENAME_DIRECTIVE_INDEX_FAMILY_FILE_PATH = 1
RENAME_DIRECTIVE_INDEX_CATEGORY = 2
RENAME_DIRECTIVE_LIST_INDEX_NEW_FAMILY_NAME = 3

# file name identifiers for rename directives
RENAME_DIRECTIVE_FILE_NAME_PREFIX = "RenameDirective"
RENAME_DIRECTIVE_FILE_EXTENSION = ".csv"

# exceptions
EXCEPTION_NO_RENAME_DIRECTIVE_FILES = "Rename directive file does not exist."
EXCEPTION_EMPTY_RENAME_DIRECTIVE_FILES = "Empty rename directive file!"


def _read_rename_directives(files):
    """
    Reads list of rename directives from file into named tuples.

    :param filePath: Fully qualified file path to rename directives file.
    :type filePath: str
    :return: List of named tuples containing rename directives.
    :rtype: [rename_directive]
    """

    rename_directives = []
    for file in files:
        rows = fileCSV.read_csv_file(file)
        # read rows in tuples ignoring the header row
        for i in range(1, len(rows)):
            if len(rows[i]) >= 4:
                data = rename_directive(
                    rows[i][RENAME_DIRECTIVE_LIST_INDEX_CURRENT_FAMILY_NAME],
                    rows[i][RENAME_DIRECTIVE_INDEX_FAMILY_FILE_PATH],
                    rows[i][RENAME_DIRECTIVE_INDEX_CATEGORY],
                    rows[i][RENAME_DIRECTIVE_LIST_INDEX_NEW_FAMILY_NAME],
                )
            rename_directives.append(data)
    return rename_directives


def get_rename_directives(directory_path):
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
        RENAME_DIRECTIVE_FILE_NAME_PREFIX,
        "",
        RENAME_DIRECTIVE_FILE_EXTENSION,
    )

    # check whether any files where found?
    if len(rename_directive_files) > 0:
        # attempt to re rename directives from files
        rename_directives = _read_rename_directives(rename_directive_files)
        # check whether any rename directives where found in files
        if len(rename_directives) > 0:
            return_value.update_sep(
                True, "Found rename directives: " + str(len(rename_directives))
            )
            # attempt to rename files
            return_value.result = rename_directives
        else:
            return_value.update_sep(False, EXCEPTION_EMPTY_RENAME_DIRECTIVE_FILES)
    else:
        return_value.update_sep(False, EXCEPTION_NO_RENAME_DIRECTIVE_FILES)

    return return_value
