"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module is used to make changes to families.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The changes made to families do not require any further input (from another script / text file):

- Purge unused (requires Autodesk eTransmit)
- Purge unused sub categories
- purge unused line patterns

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
from duHast.Revit.Family.family_utils import is_any_nested_family_instance_label_driven
from duHast.Revit.Family.family_reference_elements import (
    set_ref_planes_to_not_a_reference,
    set_symbolic_and_model_lines_to_not_a_reference,
)
from duHast.Revit.Family.Data.Objects.family_data_collector import (
    RevitFamilyDataCollector,
)
from duHast.Revit.Purge.purge_unused_e_transmit import purge_unused_e_transmit
from duHast.Revit.Categories.Data.Objects.category_data_processor import (
    CategoryProcessor,
)
from duHast.Revit.Categories.Data.category_data_purge_unused import (
    purge_unused_sub_categories,
)
from duHast.Revit.LinePattern.Data.Objects.line_pattern_data_processor import (
    LinePatternProcessor,
)
from duHast.Revit.LinePattern.Data.line_pattern_data_purge_unused import (
    purge_unused as purge_unused_line_patterns,
)
from duHast.Revit.SharedParameters.Data.Objects.shared_parameter_data_processor import (
    SharedParameterProcessor,
)
from duHast.Revit.SharedParameters.Data.shared_parameter_data_purge_Unused import (
    purge_unused as purge_unused_shared_parameters,
)

import ModifyLibraryFamilyDefaultParameters as rParameterDefaultActions

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


def process_family(doc, processor):
    # get the family category
    family_category_name = doc.OwnerFamily.FamilyCategory.Name
    collector = RevitFamilyDataCollector([processor])
    family_name = doc.Title
    # strip .rfa of name
    if family_name.lower().endswith(".rfa"):
        family_name = family_name[:-4]
    # process family
    flag_data_collection_ = collector.process_family(
        doc, family_name, family_category_name
    )
    return processor, flag_data_collection_


# ----------------------------------------------------- default family actions ------------------------------------------


def purge_unused(doc):
    """
    Purges family unless a nested family which is label driven is present.

    :param doc: Current family document.
    :type doc: AutoDesk.Revit.DB.Document

    :return:
        Result class instance.

        - result.status. True if purge unused was undertaken and successful, otherwise False.
        - result.message be generic success message.
        - result.result empty list

        On exception:

        - result.status (bool) will be False.
        - result.message will contain an exception message.
        - result.result will be empty

    :rtype: :class:`.Result`
    """

    return_value = Result()
    # check if any nested family instance placed is label driven...if True do not purge!
    is_instance_label_driven = is_any_nested_family_instance_label_driven(doc)

    if is_instance_label_driven == False:
        # purge unused
        return_value = purge_unused_e_transmit(doc)
    else:
        return_value.update_sep(
            False, "Nested family which is Label driven found. Nothing was purged."
        )

    return return_value


def update_purge_status(return_value, action_status):
    """
    Check if both purge actions succeeded...if only one do not change the status to false since the
    family still requires to be saved!

    :param return_value: The overall action to be updated with new action status.
    :type return_value: :class:`.Result`
    :param action_status: The new action status.
    :type action_status: :class:`.Result`

    :return: The updated overall action status.
    :rtype: :class:`.Result`
    """
    try:
        if return_value.status and action_status.status:
            return_value.update(action_status)
        elif return_value.status == False and action_status.status == True:
            return_value.status = True
            return_value.append_message(action_status.message)
        else:
            return_value.append_message(action_status.message)
    except Exception as e:
        output(
            "Exception in update_purge_status: ".format(e),
            revit_script_util.Output,
        )
    return return_value


def purge_unused_others(doc):
    """
    Purges out unused sub categories and line patterns in a family.

    Uses family processor modules to determine which categories or line patterns are not used.

    :param doc: Current family document.
    :type doc: AutoDesk.Revit.DB.Document

    :return:
        Result class instance.

        - result.status. True if purge unused categories and line patterns was undertaken and successful, otherwise False.
        - result.message be generic success message.
        - result.result empty list

        On exception:

        - result.status (bool) will be False.
        - result.message will contain an exception message.
        - result.result will be empty

    :rtype: :class:`.Result`
    """

    return_value = Result()
    try:
        # process categories first
        processor_categories, process_status = process_family(doc, CategoryProcessor())
        if process_status:
            data = processor_categories.get_data()
            return_value.append_message("data length categories: {}".format(len(data)))
            # purge unused categories
            outcome_purge_cats = purge_unused_sub_categories(doc, processor_categories)
            return_value.update(outcome_purge_cats)
        else:
            return_value.update_sep(
                False, "Category processor failed...nothing was purged."
            )
    except Exception as e:
        output(
            "Exception in purge categories: {}".format(e),
            revit_script_util.Output,
        )

    try:
        # process line patterns
        processor_line_patterns, process_status = process_family(
            doc, LinePatternProcessor()
        )
        if process_status:
            data = processor_line_patterns.get_data()
            return_value.append_message(
                "data length line patterns: {}".format(len(data))
            )
            # purge unused categories
            outcome_purge_line_patterns = purge_unused_line_patterns(
                doc, processor_line_patterns
            )
            # check if both purge actions succeeded...if only one do not change the status to false since the
            # family still requires to be saved!
            return_value = update_purge_status(
                return_value, outcome_purge_line_patterns
            )
        else:
            # no need to update the status at this point as if true family needs to be saved even if the line pattern purge failed.
            return_value.append_message(
                "Line pattern processor failed...nothing was purged."
            )
    except Exception as e:
        output(
            "Exception in purge line patterns: {}".format(e),
            revit_script_util.Output,
        )

    try:
        # process shared parameters
        processor_shared_parameters, process_status = process_family(
            doc, SharedParameterProcessor()
        )
        if process_status:
            data = processor_shared_parameters.get_data()
            return_value.append_message(
                "data length shared paras: {}".format(len(data))
            )
            # purge unused shared parameter definitions
            outcome_purge_shared_parameters = purge_unused_shared_parameters(
                doc, processor_shared_parameters
            )
            # check if both purge actions succeeded...if only one do not change the status to false since the
            # family still requires to be saved!
            return_value = update_purge_status(
                return_value, outcome_purge_shared_parameters
            )
        else:
            # no need to update the status at this point as if true family needs to be saved even if the shared parameter purge failed.
            return_value.append_message(
                "Shared parameter processor failed...nothing was purged."
            )
    except Exception as e:
        output(
            "Exception in purge unused shared parameters: {}".format(e),
            revit_script_util.Output,
        )

    try:
        # delete any unwanted shared parameters
        outcome_purge_unwanted_shared_paras = (
            rParameterDefaultActions.delete_unwanted_shared_parameters(doc)
        )
        # check if both purge actions succeeded...if only one do not change the status to false since the
        # family still requires to be saved!
        return_value = update_purge_status(
            return_value, outcome_purge_unwanted_shared_paras
        )
    except Exception as e:
        output(
            "Exception in purge unwanted shared parameters: {}".format(e),
            revit_script_util.Output,
        )

    try:
        # change shared parameter to family parameters
        outcome_change_shared_paras = (
            rParameterDefaultActions.change_parameter_to_family_parameter(doc)
        )
        # check if both purge actions succeeded...if only one do not change the status to false since the
        # family still requires to be saved!
        return_value = update_purge_status(return_value, outcome_change_shared_paras)
    except Exception as e:
        output(
            "Exception in changing shared parameters to family parameters: {}".format(
                e
            ),
            revit_script_util.Output,
        )

    try:
        # swap shared parameters
        outcome_swap_shared_paras = rParameterDefaultActions.swap_shared_parameters_in_family(doc)
        # check if both actions succeeded...if only one do not change the status to false since the
        # family still requires to be saved!
        return_value = update_purge_status(return_value, outcome_swap_shared_paras)
    except Exception as e:
        output(
            "Exception in swap shared parameters:{} ".format(
                e
            ),
            revit_script_util.Output,
        )

    try:
        # add default parameters
        outcome_add_default_paras = rParameterDefaultActions.add_default_parameters(
            doc, rParameterDefaultActions.SHARED_PARAMETERS_TO_ADD
        )
        # check if both actions succeeded...if only one do not change the status to false since the
        # family still requires to be saved!
        return_value = update_purge_status(return_value, outcome_add_default_paras)
    except Exception as e:
        output(
            "Exception in adding default shared parameters: {}".format(e),
            revit_script_util.Output,
        )

    return return_value


def update_reference_status(doc):
    """
    Set the reference status to not a reference for all weak reference planes and any lines.

    :param doc: Current family document.
    :type doc: AutoDesk.Revit.DB.Document

    :return:
        Result class instance.

        - result.status. True if reference status was set successfully, otherwise False.
        - result.message be generic success message.
        - result.result empty list

        On exception:

        - result.status (bool) will be False.
        - result.message will contain an exception message.
        - result.result will be empty

    :rtype: :class:`.Result`
    """

    return_value = Result()
    return_value.update(set_ref_planes_to_not_a_reference(doc))
    return_value.update(set_symbolic_and_model_lines_to_not_a_reference(doc))
    return return_value


# -----------------------------------------------------------------------------------------------------------------------------------------------
# main:
# -------------

# setup timer
t = Timer()
t.start()

over_all_status_ = Result()
# assume no change, therefore file needs nod to be saved
over_all_status_.status = False

# actions to be executed per family
family_actions = [
    purge_unused,  # purge first :)
    purge_unused_others,  # purge other things
    update_reference_status,  # fix up ref planes
]

# debug test
output(
    "Script directory: {}".format(settings.SCRIPT_DIRECTORY),
    revit_script_util.Output,
)

output(
    "Modifying Revit File.... start",
    revit_script_util.Output,
)

# loop over all family actions and execute them
# check for each action if family needs to be saved
for family_action in family_actions:
    result_family_action = family_action(doc)
    if result_family_action.status:
        # need to save family
        over_all_status_.status = True
    over_all_status_.append_message(result_family_action.message)
    output(
        result_family_action.message,
        revit_script_util.Output,
    )
    output(
        str(result_family_action.status),
        revit_script_util.Output,
    )

output(
    str(t.stop()),
    revit_script_util.Output,
)

# -------------
# Saving file after changes have been made
# -------------

# get the file name
fileName = get_file_name_without_ext(REVIT_FILE_PATH)
REVIT_FILE_PATH_NEW = os.path.join(settings.WORKING_DIRECTORY, fileName + ".rfa")

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
        [[fileName, fileName]],
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
        write_copy_marker_file(fileName)
        # write family has changed marker file
        family_category_name = doc.OwnerFamily.FamilyCategory.Name
        write_changed_family_marker_file(fileName, family_category_name)
