"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module is used to make changes to families.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The changes made to families do not require any further input (from another script / text file):

- modify shared parameter:
    - change shared parameter to family parameter
    - delete shared parameter
    - swap shared parameter


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
import System

import settings as settings  # sets up all commonly used variables and path locations!

# import common library
from duHast.Utilities.Objects.result import Result

from duHast.Revit.SharedParameters.shared_parameter_add import (
    add_shared_parameter_to_family,
    load_shared_parameter_file,
)
from duHast.Revit.SharedParameters.shared_parameters_delete import (
    delete_shared_parameters,
)
from duHast.Revit.SharedParameters.shared_parameters import (
    get_all_shared_parameters,
    check_whether_shared_parameters_by_name_is_family_parameter,
)
from duHast.Revit.SharedParameters.shared_parameter_swap import swap_shared_parameters
from duHast.Revit.Family.family_parameter_utils import set_family_parameter_value
from duHast.Revit.Common.transaction import in_transaction
from duHast.Revit.Common.delete import delete_by_element_ids
from duHast.Utilities.files_csv import read_csv_file
from duHast.Utilities.date_stamps import get_file_date_stamp
from duHast.Utilities.files_io import file_exist

from duHast.Revit.SharedParameters.shared_parameters_tuple import PARAMETER_DATA


# import Revit API
from Autodesk.Revit.DB import BuiltInParameterGroup, Transaction


# ----------------------------------------------------- default family actions ------------------------------------------
def get_family_parameters(doc):
    """
    Gets all family parameters.

    :param doc: Current Revit family document.
    :type doc: Autodesk.Revit.DB.Document
    :raises Exception: "Document is not a family document." when a non family document is passt in.

    :return: A list of family parameters
    :rtype: [Autodesk.Revit.DB.FamilyParameter]
    """

    if doc.IsFamilyDocument:
        family_manager = doc.FamilyManager
        shared_family_paras = []
        for family_para in family_manager.GetParameters():
            shared_family_paras.append(family_para)
    else:
        raise Exception("Document is not a family document.")
    return shared_family_paras


def change_parameter_to_family_parameter(doc):
    """
    Changes shared parameters to family parameters based on text file in \_Input folder

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return:
        Result class instance.

        - result.status. True if change of shared parameters to family parameters was successful, otherwise False.
        - result.message be generic success message.
        - result.result empty list

        On exception:

        - result.status (bool) will be False.
        - result.message will contain an exception message.
        - result.result will be empty

    :rtype: :class:`.Result`
    """

    return_value = Result()
    #  dictionary used to change shard parameters to family parameters
    parameter_mapper = {}
    return_value.append_message(
        "Changing shared parameters to family parameters...start"
    )
    # parameter change directives
    try:
        # check if file exists
        if (
            file_exist(settings.CHANGE_SHARED_PARAMETER_TO_FAMILY_PARAMETER_PATH)
            == False
        ):
            return_value.update_sep(
                False,
                "No shared parameter change directives file found: {}".format(
                    settings.CHANGE_SHARED_PARAMETER_TO_FAMILY_PARAMETER_PATH
                ),
            )
            return return_value

        fileData = read_csv_file(
            settings.CHANGE_SHARED_PARAMETER_TO_FAMILY_PARAMETER_PATH
        )
        if len(fileData) > 0:
            for row in fileData:
                if len(row) > 1:
                    parameter_mapper[row[0]] = row[1]  # get the family manager
        else:
            # time to get out...
            return_value.update_sep(
                False,
                "No shared parameter change directives file found or file is empty.",
            )
            return return_value
    except Exception as e:
        # time to get out...
        return_value.update_sep(
            False, "No shared parameter change directives file found.{}".format(e)
        )
        return return_value

    # a match was found
    match_found = False
    # check if any change directives where found
    if len(parameter_mapper) > 0:
        manager = doc.FamilyManager
        # get family parameters
        paras = get_family_parameters(doc)
        # check whether any parameter in family requires changing
        for p in paras:
            if p.Definition.Name in parameter_mapper:
                # update flag
                match_found = True
                # save the old name
                parameter_old_name = p.Definition.Name

                # define action to change shared parameter to family parameter
                def action():
                    return_value_transaction = Result()
                    try:
                        manager.ReplaceParameter(
                            p,
                            parameter_mapper[p.Definition.Name],
                            p.Definition.ParameterGroup,
                            p.IsInstance,
                        )
                        return_value_transaction.update_sep(
                            True,
                            "Successfully changed parameter {} to a family parameter: {}".format(
                                parameter_old_name, parameter_mapper[parameter_old_name]
                            ),
                        )
                    except Exception as e:
                        return_value_transaction.update_sep(
                            False,
                            "Failed to change parameter {} to a family parameter with exception: {}".format(
                                parameter_old_name, e
                            ),
                        )
                    return return_value_transaction

                # put everything in a transaction
                transaction = Transaction(
                    doc, "change to family parameter {}".format(parameter_old_name)
                )
                result = in_transaction(transaction, action)
                return_value.update(result)
                if result.status:
                    # delete shared parameter definition:
                    shared_parameters = get_all_shared_parameters(doc)
                    for shared_parameter in shared_parameters:
                        if shared_parameter.Name == parameter_old_name:
                            result_delete = delete_by_element_ids(
                                doc,
                                [shared_parameter.Id],
                                "deleting: {}".format(parameter_old_name),
                                "shared parameter",
                            )
                            return_value.update(result_delete)
                            break
    else:
        return_value.update_sep(
            False, "No shared parameter change directives where found."
        )
    if match_found == False:
        return_value.update_sep(
            False, "No matching shared parameter(s) where found in family."
        )
    return return_value


def delete_unwanted_shared_parameters(doc):
    """
    Deletes all shared paras in a project file flagged as unwanted

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return:
        Result class instance.

        - result.status. True if deleting unwanted shared parameters was successful, otherwise False.
        - result.message be generic success message.
        - result.result empty list

        On exception:

        - result.status (bool) will be False.
        - result.message will contain an exception message.
        - result.result will be empty

    :rtype: :class:`.Result`
    """

    return_value = Result()
    return_value.append_message("Deleting unwanted shared parameters...start")
    try:
        # check if file exists
        if file_exist(settings.DELETE_SHARED_PARAMETER_LIST_FILE_PATH) == False:
            return_value.update_sep(
                False,
                "No shared parameter delete file found: {}".format(
                    settings.DELETE_SHARED_PARAMETER_LIST_FILE_PATH
                ),
            )
            return return_value

        # read data file
        fileData = read_csv_file(settings.DELETE_SHARED_PARAMETER_LIST_FILE_PATH)
        guid_s_to_delete = []
        for row in fileData:
            if len(row) > 1:
                # check if entry is a guid
                if len(row[1]) == 36:
                    guid_s_to_delete.append(row[1])
                    return_value.append_message(
                        "Found shared parameter to delete: {} with guid: {}".format(
                            row[0], row[1]
                        )
                    )
                else:
                    return_value.update_sep(
                        False,
                        "Shared parameter file contains malformed GUID: {} for parameter: {}".format(
                            row[1], row[0]
                        ),
                    )
            else:
                return_value.update_sep(
                    False,
                    "Shared parameter file contains malformed row: {}".format(row),
                )
    except Exception as e:
        return_value.update_sep(
            False,
            "Failed to read shared parameter file: {} with exception: {}".format(
                settings.DELETE_SHARED_PARAMETER_LIST_FILE_PATH, e
            ),
        )
        return return_value
    # go ahead and delete...
    if len(guid_s_to_delete) > 0:
        result_delete = delete_shared_parameters(doc, guid_s_to_delete)
        return_value.update(result_delete)
    else:
        return_value.update_sep(
            False,
            "No valid GUID's found in guid data file: {}".format(
                settings.DELETE_SHARED_PARAMETER_LIST_FILE_PATH
            ),
        )
    return return_value


def swap_shared_parameters_in_family(doc):
    """
    Swaps out shared parameters as per directive

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return:
        Result class instance.

        - result.status. True if swapping shared parameters was successful, otherwise False.
        - result.message be generic success message.
        - result.result  list of new shared parameters

        On exception:

        - result.status (bool) will be False.
        - result.message will contain an exception message.
        - result.result will be empty

    :rtype: :class:`.Result`
    """

    return_value = Result()
    return_value.append_message("Swap shared parameters...start")
    if file_exist(settings.SWAP_SHARED_PARAMETER_DIRECTIVE_PATH) == False:
        return_value.update_sep(
            False,
            "No shared parameter swap file found: {}".format(
                settings.SWAP_SHARED_PARAMETER_DIRECTIVE_PATH
            ),
        )
        return return_value

    # attempt to swap shared parameters
    return_value.update(
        swap_shared_parameters(doc, settings.SWAP_SHARED_PARAMETER_DIRECTIVE_PATH)
    )
    return return_value


TODAYS_DATE = get_file_date_stamp()
# tuple containing the shared parameters to be added
SHARED_PARAMETERS_TO_ADD = {
    "NewTestParameter": [
        PARAMETER_DATA(
            "NewTestParameter", True, BuiltInParameterGroup.PG_IDENTITY_DATA
        ),
        "",
        "sample value",
        settings.SHARED_PARAMETER_FILE_PATH,
    ],
}


def add_default_parameters(doc, shared_parameters_to_add):
    """
    Assigns default parameters to family. Refer to list sharedParametersToAdd_.

    Note: if not type is set up in the family, the parameters will be added without values assigned.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param shared_parameters_to_add: A dictionary where the key is the parameter name and the value is a list in format: tuple, formula value, value. If formula value is an empty string, the value entry will be assigned to the parameter instead.
    :type shared_parameters_to_add: {str:[tuple, str, str]}

    :return:
        Result class instance.

        - result.status. True if shared parameters where added successfully, otherwise False.
        - result.message be generic success message.
        - result.result  empty list

        On exception:

        - result.status (bool) will be False.
        - result.message will contain an exception message.
        - result.result will be empty

    :rtype: :class:`.Result`
    """

    return_value = Result()
    return_value.append_message("Adding default shared parameters...start")
    # get the family manager
    manager = doc.FamilyManager
    # get a current type
    family_types = manager.Types
    # add parameters and values
    for para in shared_parameters_to_add:
        # load shared para file
        shared_parameter_definition_file = load_shared_parameter_file(
            doc, shared_parameters_to_add[para][3]
        )
        if shared_parameter_definition_file != None:
            # check whether parameter already in family
            family_shared_parameter = (
                check_whether_shared_parameters_by_name_is_family_parameter(doc, para)
            )
            # if not add it to family
            if family_shared_parameter == None:
                return_value.append_message(
                    "Parameter: {} not found in family".format(para)
                )
                family_parameter_result = add_shared_parameter_to_family(
                    shared_parameters_to_add[para][0],
                    manager,
                    doc,
                    shared_parameter_definition_file,
                )
                return_value.update(family_parameter_result)
                if family_parameter_result.status:
                    family_shared_parameter = family_parameter_result.result[0]
                else:
                    return_value.update_sep(
                        False, "Failed to add parameter:  {} to family!".format(para)
                    )
            else:
                return_value.append_message(
                    "Parameter:  {} found in family, no need to it add again.".format(
                        para
                    )
                )

            # add parameter value if at least one type exists
            if family_types.Size > 0:
                # check whether a formula or a value needs to be set
                if (
                    SHARED_PARAMETERS_TO_ADD[para][1] != ""
                    and family_shared_parameter != None
                ):
                    # set formula
                    return_value.update(
                        set_family_parameter_value(
                            doc,
                            manager,
                            family_shared_parameter,
                            shared_parameters_to_add[para][1],
                        )
                    )
                elif (
                    SHARED_PARAMETERS_TO_ADD[para][2] != ""
                    and family_shared_parameter != None
                ):
                    # set value
                    return_value.update(
                        set_family_parameter_value(
                            doc,
                            manager,
                            family_shared_parameter,
                            shared_parameters_to_add[para][2],
                        )
                    )
                elif (
                    SHARED_PARAMETERS_TO_ADD[para][1] == ""
                    and SHARED_PARAMETERS_TO_ADD[para][2] == ""
                ):
                    return_value.append_message(
                        "No parameter value provided for parameter:  {}".format(para)
                    )
                else:
                    return_value.append_message(
                        "Failed to add value to parameter:  {}".format(para)
                    )
            else:
                return_value.append_message(
                    "No parameter value set since no type exists in family"
                )
        else:
            return_value.update_sep(False, "Failed to load shared parameter file.")
    return return_value
