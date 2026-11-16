"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Utility functions reading family category and sub category change directives, and finding the families they apply to.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""


#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2026, Jan Christel
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

from duHast.Utilities import files_csv as fileCSV, files_get as fileGet
from duHast.Utilities.Objects import result as res
from duHast.Revit.Family.Data.Objects.family_directive_change_category import (
    FamilyDirectiveChangeCategory,
)
from duHast.Revit.Family.Data.Objects.family_directive_change_sub_category import (
    FamilyDirectiveChangeSubCategory,
)


def _read_directive_rows(directory_path, file_name_prefix, file_extension):
    """
    Reads the rows of all directive files with the given file name prefix in the directory and its sub directories.

    Directive files have no header row. Rows repeated across files are only returned once.

    :return: The fully qualified file paths found, and the rows read from them.
    :rtype: [str], [[str]]
    """

    files = fileGet.get_files_from_directory_walker_with_filters(
        directory_path, file_name_prefix, "", file_extension
    )
    rows = []
    for file_path in files:
        rows_result = fileCSV.read_csv_file(file_path)
        if rows_result.status is False:
            raise ValueError(
                "Failed to read directive file: {} with: {}".format(
                    file_path, rows_result.message
                )
            )
        for row in rows_result.result:
            if row not in rows:
                rows.append(row)
    return files, rows


def get_category_change_directives(directory_path):
    """
    Retrieves family category change directives from a given folder location.

    :param directory_path: Fully qualified folder path to folder containing directives.
    :type directory_path: str

    :return:
        Result class instance.

        - result.status. True if directives where found and loaded successfully, otherwise False.
        - result.message will contain number of directives found.
        - result.result list of :class:`.FamilyDirectiveChangeCategory`

        On exception:

        - result.status (bool) will be False.
        - result.message will contain an exception message.
        - result.result will be empty

    :rtype: :class:`.Result`
    """

    return_value = res.Result()
    try:
        files, rows = _read_directive_rows(
            directory_path,
            FamilyDirectiveChangeCategory.CHANGE_CATEGORY_DIRECTIVE_FILE_NAME_PREFIX,
            FamilyDirectiveChangeCategory.CHANGE_CATEGORY_DIRECTIVE_FILE_EXTENSION,
        )
        if len(files) == 0:
            raise ValueError(
                FamilyDirectiveChangeCategory.EXCEPTION_NO_CHANGE_CATEGORY_DIRECTIVE_FILES
            )
        directives = []
        for row in rows:
            if len(row) >= 2:
                directives.append(
                    FamilyDirectiveChangeCategory(
                        file_path=row[
                            FamilyDirectiveChangeCategory.CHANGE_CATEGORY_DIRECTIVE_INDEX_FAMILY_FILE_PATH
                        ],
                        new_category_name=row[
                            FamilyDirectiveChangeCategory.CHANGE_CATEGORY_DIRECTIVE_INDEX_NEW_CATEGORY_NAME
                        ],
                    )
                )
        if len(directives) == 0:
            raise ValueError(
                FamilyDirectiveChangeCategory.EXCEPTION_EMPTY_CHANGE_CATEGORY_DIRECTIVE_FILES
            )
        return_value.update_sep(
            True, "Found category change directives: {}".format(len(directives))
        )
        return_value.result = directives
    except Exception as e:
        return_value.update_sep(False, "{}".format(e))
    return return_value


def get_sub_category_change_directives(directory_path):
    """
    Retrieves family sub category change directives from a given folder location.

    :param directory_path: Fully qualified folder path to folder containing directives.
    :type directory_path: str

    :return:
        Result class instance.

        - result.status. True if directives where found and loaded successfully, otherwise False.
        - result.message will contain number of directives found.
        - result.result list of :class:`.FamilyDirectiveChangeSubCategory`

        On exception:

        - result.status (bool) will be False.
        - result.message will contain an exception message.
        - result.result will be empty

    :rtype: :class:`.Result`
    """

    return_value = res.Result()
    try:
        files, rows = _read_directive_rows(
            directory_path,
            FamilyDirectiveChangeSubCategory.CHANGE_SUB_CATEGORY_DIRECTIVE_FILE_NAME_PREFIX,
            FamilyDirectiveChangeSubCategory.CHANGE_SUB_CATEGORY_DIRECTIVE_FILE_EXTENSION,
        )
        if len(files) == 0:
            raise ValueError(
                FamilyDirectiveChangeSubCategory.EXCEPTION_NO_CHANGE_SUB_CATEGORY_DIRECTIVE_FILES
            )
        directives = []
        for row in rows:
            if len(row) >= 3:
                directives.append(
                    FamilyDirectiveChangeSubCategory(
                        category=row[
                            FamilyDirectiveChangeSubCategory.CHANGE_SUB_CATEGORY_DIRECTIVE_INDEX_FAMILY_CATEGORY
                        ],
                        old_sub_category_name=row[
                            FamilyDirectiveChangeSubCategory.CHANGE_SUB_CATEGORY_DIRECTIVE_INDEX_OLD_SUB_CATEGORY_NAME
                        ],
                        new_sub_category_name=row[
                            FamilyDirectiveChangeSubCategory.CHANGE_SUB_CATEGORY_DIRECTIVE_INDEX_NEW_SUB_CATEGORY_NAME
                        ],
                    )
                )
        if len(directives) == 0:
            raise ValueError(
                FamilyDirectiveChangeSubCategory.EXCEPTION_EMPTY_CHANGE_SUB_CATEGORY_DIRECTIVE_FILES
            )
        return_value.update_sep(
            True, "Found sub category change directives: {}".format(len(directives))
        )
        return_value.result = directives
    except Exception as e:
        return_value.update_sep(False, "{}".format(e))
    return return_value


def get_families_requiring_sub_category_change(root_families, sub_category_change_directives):
    """
    Returns the file paths of the root families which have a sub category to be renamed as per the directives.

    :param root_families: Root families read from a family category report.
    :type root_families: [:class:`.FamilyDataFamily`]
    :param sub_category_change_directives: Sub category change directives.
    :type sub_category_change_directives: [:class:`.FamilyDirectiveChangeSubCategory`]

    :return: List of unique fully qualified family file paths.
    :rtype: [str]
    """

    file_paths = []
    for root_family in root_families:
        for directive in sub_category_change_directives:
            if root_family.family_category == directive.category and root_family.has_sub_category(
                directive.old_sub_category_name
            ):
                if root_family.family_file_path not in file_paths:
                    file_paths.append(root_family.family_file_path)
                break
    return file_paths
