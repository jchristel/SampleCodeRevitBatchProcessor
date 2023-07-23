"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a custom helper functions for marker files.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- bim 360 folder
- export file name
- copy export files
- read the current file list in docFile objects

"""

#!/usr/bin/python
# -*- coding: utf-8 -*-
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

# import settings
import settings as settings  # sets up all commonly used variables and path locations!

from duHast.Revit.Views.sheets import get_sheet_rev_by_sheet_name
from duHast.Utilities.utility import pad_single_digit_numeric_string
from duHast.Utilities.Objects import result as res
from docFile_io import read_current_file

# --------------- read file -------------------


def build_default_file_list(
    doc,
    revision_data_file_path,
    revit_file_name,
    splash_screen_name,
    revit_file_extension
):
    """
    Reads file data from file and stores it in a global list. 

    This list contains: 

    - the current file name(s) 
    - the file name after the export.
    - document management system number and name

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param revision_data_file_path: _description_
    :type revision_data_file_path: _type_
    :param revit_file_name: _description_
    :type revit_file_name: _type_
    :param splash_screen_name: _description_
    :type splash_screen_name: _type_
    :param revit_file_extension: _description_
    :type revit_file_extension: _type_

    :return:
        Result class instance.

        - Read status returned in result.status. False if an exception occurred, otherwise True.
        - result.message will contain message(s) in format: 'Copied: currentFullFileName to newFileName'
        - result.result will be an empty list.

        On exception:

        - result.status (bool) will be False.
        - result.message will contain the exception message.
        - result.status will be an empty list.

    :rtype: :class:`.Result`
    """

    return_value = res.Result()

    # will contain the old file name and the new file name (with revision data)
    matched_file_data = []
    marker_file_data = None
    # get the revision from title sheet
    rev = get_sheet_rev_by_sheet_name(doc, splash_screen_name)
    match = False
    # read current files
    file_list = read_current_file(revision_data_file_path)
    if file_list is not None and len(file_list) > 0:
        # loop over file data objects and search for match
        return_value.append_message("looking for match:".format(revit_file_name))
        for file_data in file_list:
            return_value.append_message(
                "starts with {}".format(file_data.existing_file_name)
            )
            if (
                revit_file_name.startswith(file_data.existing_file_name)
                and file_data.file_extension == revit_file_extension
            ):
                return_value.append_message("Found match!")
                match = True
                file_data.revision = rev  # update with latest revision from sheet
                # pad revision out to two digits if required
                file_data.revision = pad_single_digit_numeric_string(file_data.revision)
                # store updated file data to be written to marker file
                marker_file_data = file_data.get_data()
                # get new file name for saving as
                new_file_name = file_data.get_new_file_name()
                # build revision file name
                row_default_new = []
                row_default_new.append(file_data.existing_file_name)
                row_default_new.append(new_file_name)
                matched_file_data.append(row_default_new)
        if match == False:
            # check whether we found a match
            return_value.update_sep(False, "No file name match found in file list.")
    else:
        return_value.update_sep(False, "File data list is empty!")
    return return_value, matched_file_data, marker_file_data