"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module builds the list of families to be processed for sub category name changes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- it reads 

    - the categroy report and 
    - change sub category directive files

- builds a file list and saves it into the task file directory

- returns a 0 if everything went ok otherwise a 2 ( an exception occurred or no files required changing)

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
# default file path locations1
# --------------------------

import sys, os

import settings as settings  # sets up all commonly used variables and path locations!

from duHast.Utilities.console_out import output
from duHast.Revit.Family.Data.family_category_data_utils_deprecated import (
    read_overall_family_category_data_from_directory,
    read_overall_family_sub_category_change_directives_from_directory,
    get_families_requiring_sub_category_change,
)

from duHast.Utilities.files_csv import write_report_data_as_csv

# -------------
# my code here:
# -------------


# -------------
# main:
# -------------
output("Python pre process script: Task list builder start ...")
output("Using path: {}".format(settings.INPUT_DIRECTORY))

try:
    root_families, nested_Families = read_overall_family_category_data_from_directory(
        settings.INPUT_DIRECTORY
    )
    # check if any root families where found
    if len(root_families) > 0:
        sub_category_change_directives = (
            read_overall_family_sub_category_change_directives_from_directory(
                settings.INPUT_DIRECTORY
            )
        )
        root_families_needing_change = get_families_requiring_sub_category_change(
            root_families, sub_category_change_directives
        )
        output("matches found: {}".format(len(root_families_needing_change)))
        if len(root_families_needing_change) > 0:

            # writer expects a list of lists...
            root_families_to_file = []
            for root_family_needing_change in root_families_needing_change:
                root_families_to_file.append([root_family_needing_change])
            try:
                task_file_name = os.path.join(
                    settings.TASK_FILE_DIRECTORY,
                    settings.PREDEFINED_TASK_FILE_NAME_PREFIX
                    + settings.PREDEFINED_TASK_FILE_EXTENSION,
                )
                # write out task file list into task folder
                write_report_data_as_csv(task_file_name, [], root_families_to_file)
                # user feed back
                output("Successfully wrote task file: {}".format(task_file_name))
                sys.exit(0)
            except Exception as e:
                output("failed to write task file name with exception: {}".format(e))
                sys.exit(2)
        else:
            # do nothing...
            output(
                "No root families requiring a sub category renamed found. Terminating without proceeding..."
            )
            sys.exit(2)
    else:
        # do nothing...
        output("No root families in report found. Terminating without proceeding...")
        sys.exit(2)
except Exception as e:
    output("An exception occurred when building task list: {}".format(e))
    output("Terminating without proceeding...")
    sys.exit(2)
