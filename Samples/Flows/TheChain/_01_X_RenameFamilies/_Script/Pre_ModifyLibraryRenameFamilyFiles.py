"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module is a pre - processing module renaming family files on a (network) drive
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module:

- Renames family files and associated catalogue files as per directives found in a given folder.
- Sets up a task list file containing all host families which have nested families requiring a rename.
- File format:

    - comma separated, file extension .task

"""

#!/usr/bin/python
# -*- coding: utf-8 -*-

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


# --------------------------
# default file path locations
# --------------------------

import sys, os

import settings as settings  # sets up all commonly used variables and path locations!

from duHast.Utilities.console_out import output
from duHast.Utilities.files_csv import write_report_data_as_csv
from duHast.Utilities.Objects.result import Result

from duHast.Revit.Family.family_rename_files_utils import get_rename_directives
from duHast.Revit.Family.Data.family_rename_files import rename_family_files
from duHast.Revit.Family.Data.family_rename_find_host_families import (
    find_host_families_with_nested_families_requiring_rename,
)


# -------------
# my code here:
# -------------


def _get_new_path(rename_directives, current_file_path):
    """
    Checks wether the current file path exists in one of the rename directives. If so it will return the file path of the renamed file,
    otherwise it will return the past in file path.

    :param rename_directives: list of tuples representing rename directives
    :type rename_directives: [named tuple]
    :param current_file_path: The fully qualified file path to a revit family file.
    :type current_file_path: str

    :return: _description_
    :rtype: str
    """

    for rename_directive in rename_directives:
        # check if the rename directive got a file path, if not ignore it!
        if (
            len(rename_directive.filePath) > 0
            and rename_directive.filePath == current_file_path
        ):
            new_file_path = (
                rename_directive.filePath[
                    : len(rename_directive.filePath)
                    - len(rename_directive.name + ".rfa")
                ]
                + rename_directive.newName
                + ".rfa"
            )
            return new_file_path
    return current_file_path


def _write_overall_task_file(result_get_host_families):
    """
    Writes a task file to disk. Task file comprises of fully qualified file path of every family containing a family which requires renaming.

    :param result_get_host_families:  Result class instance containing host families in .result.
    :type result_get_host_families: :class:`.Result`

    :return:
        Result class instance.

        - result.status. True if task file was written successfully, otherwise False.
        - result.message will contain message in format: 'Writing to: ' + taskFileName
        - result.result empty list

        On exception:

        - result.status (bool) will be False.
        - result.message will contain the exception message in format: 'Failed to write family rename task file with exception: exception'
        - result.result will be empty

    :rtype: :class:`.Result`
    """

    result = Result()
    # overall task file
    full_task_file_name = os.path.join(
        settings.INPUT_DIRECTORY,
        settings.PREDEFINED_TASK_FILE_NAME_PREFIX
        + "_FamilyRename"
        + settings.PREDEFINED_TASK_FILE_EXTENSION,
    )
    # data to be written to task file
    data = []
    # write out the actual task file
    if result_get_host_families and len(result_get_host_families.result) > 0:
        # get rename directives just in case a host family containing families to be renamed got renamed itself
        # and the path must therefore be adjusted
        rename_directives_result = get_rename_directives(rename_directives_directory_)

        for host_family in result_get_host_families.result:
            # check whether fam got renamed
            filePath = _get_new_path(
                rename_directives_result.result, host_family.filePath
            )
            if filePath != host_family.filePath:
                result.append_message(
                    "Changed path from: {} to: {}".format(
                        host_family.filePath, filePath
                    )
                )
            else:
                result.append_message("Path unchanged: {}".format(host_family.filePath))
            row = [filePath]
            data.append(row)

        result.append_message("Writing data to: {}".format(full_task_file_name))
        try:
            write_report_data_as_csv(full_task_file_name, [], data)
            result.update_sep(True, "Created task files.")
        except Exception as e:
            result.update_sep(
                False,
                "Failed to write family rename task file with exception: {}".format(e),
            )
    else:
        # write out empty task list since no host files where found
        try:
            write_report_data_as_csv(full_task_file_name, [], data)
            result.update_sep(True, "Created empty task files.")
        except Exception as e:
            result.update_sep(
                False,
                "Failed to write family rename task file with exception: {}".format(e),
            )
    return result


# -------------
# main:
# -------------

_result = Result()
output("Python pre process script Rename Files ...")
# check if a folder path was past in...otherwise go with default and exit
if len(sys.argv) == 2:
    rename_directives_directory_ = sys.argv[1]
    output(
        "Renaming files as per directives saved here: {}".format(
            rename_directives_directory_
        )
    )
    _result = rename_family_files(rename_directives_directory_)
    output(_result.message)
    output("Renamed files .... status: [{}]".format(_result.status))

    # create task file for family reload action
    output("Creating task files for rename action of nested families ...")
    _result_get_host_families = (
        find_host_families_with_nested_families_requiring_rename(
            rename_directives_directory_
        )
    )
    output(_result_get_host_families.message)
    output(
        "Got host families with nested families requiring a rename .... status: [{}]".format(
            _result_get_host_families.status
        )
    )
    # update overall status
    _result.update(_result_get_host_families)

    # write task file
    _result_write_task_file = _write_overall_task_file(_result_get_host_families)
    output(_result_write_task_file.message)
    output(
        "Writing overall rename task file .... status: [{}]".format(
            _result_write_task_file.status
        )
    )

    # update overall status
    _result.update(_result_write_task_file)

    # check how to exit
    if _result.status:
        sys.exit(0)
    else:
        sys.exit(2)
else:
    rename_directives_directory_ = settings.DEFAULT_NO_GO_DIRECTORY
    output(
        "Exiting with error. Using default file path: {} for rename directives".format(
            rename_directives_directory_
        )
    )
    sys.exit(2)
