"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module is used to change the category of a family.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Default Revit behaviour, when changing the category of a family, is to drop all custom subcategories and any element which used to be of a specific subcategory to be moved onto the
family category itself.

More often than not this means the custom subcategories need to be re-created and elements need to be re-assigned to them.

This script will:

- record all custom subcategories, their appearance properties and elements using them
- change the existing family category, if permitted
- re-create custom subcategories recorded
- re-assign elements to their respective subcategories


Corner cases:

- change of category is not permitted: e.g. an annotation family is to be changed to a model family (category Furniture): 

    - script will record an exception only and will not save out a new family

- model family category allowed for section views of families but new family category only allows for elevation views of family: 

    - script will place all elements which used the 'cut' property of a subcategory on the 'elevation' property instead


Outcomes:

- Saves marker files:
    - to help copy family back to origin in post process
    - change family log which can be used is reload advanced flows

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

# ---------------------------
# default file path locations
# ---------------------------

import clr
import os

import settings as settings  # sets up all commonly used variables and path locations!

# import common library
from duHast.Utilities.console_out import output
from duHast.Utilities.Objects.result import Result
from duHast.Utilities.files_csv import write_report_data_as_csv
from duHast.Utilities.files_io import get_file_name_without_ext
from duHast.Revit.Common.file_io import save_as_family
from duHast.Revit.Categories.categories import get_family_category
from duHast.Revit.Family.Data.family_category_data_utils_deprecated import (
    read_overall_family_category_change_directives_from_directory,
)
from duHast.Revit.Categories.change_family_category import change_family_category
from duHast.Utilities.Objects.timer import Timer


import revit_script_util
import revit_file_util

clr.AddReference("RevitAPI")
clr.AddReference("RevitAPIUI")
# NOTE: these only make sense for batch Revit file processing mode.
doc = revit_script_util.GetScriptDocument()
REVIT_FILE_PATH = revit_script_util.GetRevitFilePath()

# -------------
# my code here:
# -------------


def write_copy_marker_file(file_name):
    """
    Write marker file containing copy from and copy to path.

    :param file_name: Marker file name.
    :type file_name: str
    """

    file_name_marker = os.path.join(
        settings.WORKING_DIRECTORY, file_name + "_marker_.temp"
    )
    try:
        write_report_data_as_csv(
            file_name_marker,
            ["Copy From", "Copy To"],
            [[REVIT_FILE_PATH_NEW, REVIT_FILE_PATH]],
        )
        output(
            "Wrote marker file: {} :: [{}]".format(file_name_marker, True),
            revit_script_util.Output,
        )
    except Exception as e:
        output(
            "Wrote marker file: {} :: [{}]\nException: {}".format(
                file_name_marker, False, e
            ),
            revit_script_util.Output,
        )


def write_changed_family_marker_file(file_name, revit_category_name):
    """
    Write changed file marker file containing: file name, file path, revit category name

    :param file_name: Marker file name.
    :type file_name: str
    :param revit_category_name: The family revit category.
    :type revit_category_name: str
    """

    file_name_marker = os.path.join(
        settings.WORKING_DIRECTORY, file_name + "_changed_.temp"
    )
    try:
        write_report_data_as_csv(
            file_name_marker,
            ["file Name", "file Path", "revit category"],
            [[file_name, REVIT_FILE_PATH, revit_category_name]],
        )
        output(
            "Wrote changed family file: {} :: [{}]".format(file_name_marker, True),
            revit_script_util.Output,
        )
    except Exception as e:
        output(
            "Wrote changed family file: {} :: [{}]\nException: {}".format(
                file_name_marker, False, e
            )
        )


# ----------------------------------------------------- default family actions ------------------------------------------


def update_family_category(doc):
    """
    Changes family category as per change directive.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return:
        Result class instance.

        - result.status. True if change of family category was successful, otherwise False.
        - result.message be generic success message.
        - result.result empty list

        On exception:

        - result.status (bool) will be False.
        - result.message will contain an exception message.
        - result.result will be empty

    :rtype: :class:`.Result`
    """

    return_value = Result()
    # read change family directives
    categories_change_directives = (
        read_overall_family_category_change_directives_from_directory(
            settings.INPUT_DIRECTORY
        )
    )
    # get the family category ( this is a dictionary where key is the category name )
    family_category = get_family_category(doc)
    family_category_name = list(family_category.keys())[0]
    found_category_match = False
    new_category_name = "no category change directive found."
    # loop over change directives and find the ones applicable to the current family
    for category_change_directive in categories_change_directives:
        # check if family is in list and if the category needs changing
        if category_change_directive.filePath == REVIT_FILE_PATH:
            # save the new category name for later
            new_category_name = category_change_directive.newCategoryName
            if category_change_directive.newCategoryName != family_category_name:
                # store marker for later
                found_category_match = True
                return_value.append_message(
                    "Attempting to change category from: {} to: {}.".format(
                        family_category_name, category_change_directive.newCategoryName
                    )
                )
                try:
                    # attempt to update the family category
                    return_value.update(
                        change_family_category(
                            doc, category_change_directive.newCategoryName
                        )
                    )
                except Exception as e:
                    return_value.update_sep(
                        False,
                        "{}: failed to change family category with exception: {}".format(
                            _file_name_without_ext, e
                        ),
                    )
    # check if a category mismatch was found at all
    if found_category_match == False:
        return_value.update_sep(
            False,
            "{} :No category change required for this family. Current category: {} Category in change directive: {}".format(
                _file_name_without_ext, family_category_name, new_category_name
            ),
        )
    return return_value


# -----------------------------------------------------------------------------------------------------------------------------------------------
# main:
# -------------

# get the file name
_file_name_without_ext = get_file_name_without_ext(REVIT_FILE_PATH)

# setup timer
t = Timer()
t.start()

over_all_status_ = Result()
# assume no change, therefore file needs nod to be saved
over_all_status_.status = False

# actions to be executed per family
family_actions = [update_family_category]  # change family category

output(
    "Modifying Revit File.... start",
    revit_script_util.Output,
)

# loop over all family actions and execute them
# check for each action if family needs to be saved
for famAction in family_actions:
    resultFamAction = famAction(doc)
    if resultFamAction.status:
        # need to save family
        over_all_status_.status = True
    over_all_status_.append_message(resultFamAction.message)
    output(
        resultFamAction.message,
        revit_script_util.Output,
    )
    output(
        resultFamAction.status,
        revit_script_util.Output,
    )

output(
    "Modifying Revit File.... completed: {}".format(t.stop()),
    revit_script_util.Output,
)

# -------------
# Saving file after changes have been made
# -------------

REVIT_FILE_PATH_NEW = os.path.join(
    settings.WORKING_DIRECTORY, _file_name_without_ext + ".rfa"
)

# save file if required
if over_all_status_.status:
    # save family file
    output(
        "Saving family file: start",
        revit_script_util.Output,
    )
    syncing_ = save_as_family(
        doc,
        settings.WORKING_DIRECTORY,
        REVIT_FILE_PATH,
        [[_file_name_without_ext, _file_name_without_ext]],
        ".rfa",
        True,
    )

    output(
        "Saving family file: finished {} :: [{}]".format(
            syncing_.message, syncing_.status
        ),
        revit_script_util.Output,
    )

    # save marker file
    if syncing_.status == False:
        output(
            str(syncing_.message),
            revit_script_util.Output,
        )
    else:
        # write copy marker file
        write_copy_marker_file(_file_name_without_ext)
        # write family has changed marker file
        family_category_name = doc.OwnerFamily.FamilyCategory.Name
        write_changed_family_marker_file(_file_name_without_ext, family_category_name)
