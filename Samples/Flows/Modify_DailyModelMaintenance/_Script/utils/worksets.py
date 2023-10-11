"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Module containing workset related functions.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- move elements to worksets
- enforce default workset visibility settings

"""

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

# import Autodesk
import Autodesk.Revit.DB as rdb
from System.Collections.Generic import List

# import common library
import settings as settings  # sets up all commonly used variables and path locations!
from cleanup_actions import WORKSET_ACTIONS_BY_FILE

import duHast.Utilities.Objects.result as res
from duHast.Revit.Common.worksets import (
    update_workset_default_visibility_from_report,
    get_workset_id_by_name,
    is_element_on_workset_by_id,
    get_action_change_element_workset,
)
from duHast.Revit.Common.transaction import in_transaction
from duHast.Utilities.files_io import get_file_name_without_ext


def modify_element_worksets_with_filters(doc, revit_file_path, output):
    """
    Loops over workset action list and attempts to move objects accordingly.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param revit_file_path: Fully qualified file of the model.
    :type revit_file_path: str

    :return:
        Result class instance.

        - result.status False if an exception occurred, otherwise True.
        - result.message will contain processing messages.
        - result.result empty list

        On exception:

        - result.status (bool) will be False.
        - result.message will contain the exception message.
        - result.result will be an empty list

    :rtype: :class:`.Result`
    """

    return_value = res.Result()
    revit_file_name = get_file_name_without_ext(revit_file_path)
    output("Updating elements workset...start")
    # match actions to file name
    found_file_match = False
    for file_name in WORKSET_ACTIONS_BY_FILE:
        if revit_file_name.startswith(file_name):
            found_file_match = True
            workset_actions = WORKSET_ACTIONS_BY_FILE[file_name]
            for workset_action in workset_actions:
                default_id = get_workset_id_by_name(
                    doc, workset_action.target_workset_name
                )
                if default_id != rdb.ElementId.InvalidElementId:
                    elements = workset_action.get_elements(doc)
                    # stats
                    element_moved_counter_success = 0
                    element_moved_counter_fail = 0
                    try:
                        for el in elements:
                            if workset_action.filter.check_element(doc, el.Id) == True:
                                # check if work set actually needs changing
                                if (
                                    is_element_on_workset_by_id(doc, el, default_id)
                                    == False
                                ):
                                    # move element to target workset:
                                    transaction = rdb.Transaction(
                                        doc, "Changing workset: " + str(el.Id)
                                    )
                                    tranny_status = in_transaction(
                                        transaction,
                                        get_action_change_element_workset(
                                            el, default_id
                                        ),
                                    )
                                    # update stats
                                    if tranny_status:
                                        element_moved_counter_success = (
                                            element_moved_counter_success + 1
                                        )
                                    else:
                                        element_moved_counter_fail = (
                                            element_moved_counter_fail + 1
                                        )
                                else:
                                    pass
                                    # print ('Correct workset for: ' + str(Element.Name.GetValue(el.Symbol.Family))+ ' ' + currentWorksetName)
                    except Exception as e:
                        return_value.update_sep(
                            False,
                            "An exception occurred when attempting to change an elements workset: {}".format(
                                e
                            ),
                        )
                    return_value.update_sep(
                        True,
                        "{} :: Moved elements to workset: {}  [success: {} :: fail: {} ]".format(
                            workset_action.action_name,
                            workset_action.target_workset_name,
                            element_moved_counter_success,
                            element_moved_counter_fail,
                        ),
                    )
                else:
                    return_value.update_sep(
                        False,
                        "{} :: Default workset {} does no longer exists in file!".format(
                            workset_action.action_name,
                            workset_action.target_workset_name,
                        ),
                    )
    # check if any rules for file where present
    if found_file_match == False:
        return_value.update_sep(
            False, "No workset rules for file {} found".format(revit_file_name)
        )
    return return_value


def update_workset_default_visibility(doc, revit_file_path, output):
    """
    Updates the workset default visibility to settings stored in file

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param revit_file_path: Fully qualified file of the model.
    :type revit_file_path: str

    :return:
        Result class instance.

        - result.status False if an exception occurred, otherwise True.
        - result.message will contain processing messages.
        - result.result empty list

        On exception:

        - result.status (bool) will be False.
        - result.message will contain the exception message.
        - result.result will be an empty list

    :rtype: :class:`.Result`
    """

    return_value = res.Result()
    output("Updating workset default visibility settings...start")
    task_value = update_workset_default_visibility_from_report(
        doc, settings.WORKSET_DEFAULT_VISIBILITY_SETTINGS, revit_file_path
    )
    return_value.update(task_value)
    return return_value
