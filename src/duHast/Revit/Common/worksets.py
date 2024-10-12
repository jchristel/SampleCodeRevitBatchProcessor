"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A number of helper functions relating to Revit worksets.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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

import clr

clr.AddReference("System.Core")
from System import Linq

clr.ImportExtensions(Linq)

import System

# import common library modules
from duHast.Revit.Common import parameter_get_utils as rParaGet
from duHast.Utilities.Objects import result as res
from duHast.Revit.Common import transaction as rTran
from duHast.Revit.Common.Objects.FailureHandlingConfiguration import (
    FailureHandlingConfig,
)
from duHast.Utilities import utility as util
from duHast.Utilities import files_io as filesIO
from duHast.Utilities import files_tab as filesTab

# import Autodesk
from Autodesk.Revit.DB import (
    BuiltInParameter,
    DeleteWorksetOption,
    DeleteWorksetSettings,
    Element,
    ElementId,
    ElementWorksetFilter,
    FilteredElementCollector,
    FilteredWorksetCollector,
    Transaction,
    Workset,
    WorksetKind,
    WorksetDefaultVisibilitySettings,
    WorksetTable,
)

from Autodesk.Revit.UI import UIDocument

# --------------------------------------------- utility functions ------------------


def get_workset_id_by_name(doc, workset_name):
    """
    Returns the element id of a workset identified by its name, otherwise invalid Id (-1) if no such workset exists

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param workset_name: The name of the workset of which to retrieve the Element Id
    :type workset_name: str

    :return: The workset element id, otherwise invalid Id (-1) if no such workset exists
    :rtype: Autodesk.Revit.DB.ElementId
    """

    id = ElementId.InvalidElementId
    for p in FilteredWorksetCollector(doc).OfKind(WorksetKind.UserWorkset):
        if p.Name == workset_name:
            id = p.Id
            break
    return id


def get_workset_name_by_id(doc, id_integer):
    """
    Returns the name of the workset identified by its Element Id, otherwise 'unknown' if no such workset exists

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param id_integer: The element id as integer value.
    :type id_integer: int

    :return: The name of the workset identified by its Id, otherwise 'unknown'
    :rtype: str
    """

    name = "unknown"
    for p in FilteredWorksetCollector(doc).OfKind(WorksetKind.UserWorkset):
        if p.Id.IntegerValue == id_integer:
            name = p.Name
            break
    return name


def get_workset_ids(doc):
    """
    Gets all ids of all user defined worksets in a model

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of all user defined workset element ids
    :rtype: list Autodesk.Revit.DB.ElementId
    """

    id = []
    for p in FilteredWorksetCollector(doc).OfKind(WorksetKind.UserWorkset):
        id.append(p.Id)
    return id


def get_worksets(doc):
    """
    Returns all user defined worksets in the model as list.

    Will return a list of zero length if no worksets in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of worksets
    :rtype: list of Autodesk.Revit.DB.Workset
    """

    worksets = FilteredWorksetCollector(doc).OfKind(WorksetKind.UserWorkset).ToList()
    return worksets


def get_worksets_from_collector(doc):
    """
    Returns all user defined worksets in the model as collector.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered elements collector of user defined worksets
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    """

    collector = FilteredWorksetCollector(doc).OfKind(WorksetKind.UserWorkset)
    return collector


def open_worksets_with_elements_hack(doc, ui_doc):
    """
    This is based on a hack from the AutoDesk forum and an article from the building coder:

    - https://forums.autodesk.com/t5/revit-api-forum/open-closed-worksets-in-open-document/td-p/6238121
    - https://thebuildingcoder.typepad.com/blog/2018/03/switch-view-or-document-by-showing-elements.html

    this method will open worksets in a model containing elements only

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    """

    if isinstance(ui_doc, UIDocument) == False:
        raise TypeError(
            "ui_doc needs to be of type UIDocument but is: {}".format(type(ui_doc))
        )

    # get worksets in model
    workset_ids = get_workset_ids(doc)
    # loop over workset and open if anything is on them
    for w_id in workset_ids:
        workset = ElementWorksetFilter(w_id)
        elem_ids = FilteredElementCollector(doc).WherePasses(workset).ToElementIds()
        if len(elem_ids) > 0:
            # this will force Revit to open the workset containing this element
            ui_doc.ShowElements(elem_ids.First())


def modify_element_workset(doc, default_workset_name, collector, element_type_name):
    """
    Attempts to change the worksets of elements provided through an element collector.

    Will return false if target workset does not exist in file.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param default_workset_name: The name of the workset the elements are to be moved to.
    :type default_workset_name: str
    :param collector: The element collector containing the elements.
    :type collector: Autodesk.Revit.DB.FilteredElementCollector
    :param element_type_name: A description used in the status message returned.
    :type element_type_name: str

    :return:
        Result class instance.

        - .status = True if successfully moved all elements to new workset. Otherwise False.
        - .message will contain stats in format [success :: failure]

    :rtype: :class:`.Result`
    """

    return_value = res.Result()
    return_value.message = "Changing: {} workset to: {} ".format(
        element_type_name, default_workset_name
    )
    # get the ID of the default grids workset
    default_id = get_workset_id_by_name(doc, default_workset_name)
    counter_success = 0
    counter_failure = 0
    # check if invalid id came back..workset no longer exists..
    if default_id != ElementId.InvalidElementId:
        # get all elements in collector and check their workset
        for p in collector:
            if p.WorksetId != default_id:
                # get the element name
                element_name = "Unknown Element Name"
                try:
                    element_name = Element.Name.GetValue(p)
                except Exception:
                    pass
                # move element to new workset
                transaction = Transaction(
                    doc, "Changing workset: ".format(element_name)
                )
                tranny_status = rTran.in_transaction(
                    transaction, get_action_change_element_workset(p, default_id)
                )
                if tranny_status.status == True:
                    counter_success += 1
                else:
                    counter_failure += 1
                return_value.status = return_value.status & tranny_status.status
            else:
                counter_success += 1
                return_value.status = return_value.status & True
    else:
        return_value.update_sep(
            False,
            "Default workset: {} does no longer exists in file!".format(
                default_workset_name
            ),
        )
    return_value.append_message(
        "Moved: {} to workset: {} [ {} :: {}]".format(
            element_type_name, default_workset_name, counter_success, counter_failure
        )
    )
    return return_value


def get_action_change_element_workset(el, default_id):
    """
    Contains the required action to change a single elements workset

    :param el: The element
    :type el: Autodesk.Revit.DB.Element
    :param default_id: The workset element Id
    :type default_id: Autodesk.Revit.DB.ElementId
    """

    def action():
        action_return_value = res.Result()
        try:
            ws_param = el.get_Parameter(BuiltInParameter.ELEM_PARTITION_PARAM)
            ws_param.Set(default_id.IntegerValue)
            action_return_value.message = "Changed element workset."
        except Exception as e:
            action_return_value.update_sep(False, "Failed with exception: {}".format(e))
        return action_return_value

    return action


def is_element_on_workset_by_id(doc, el, workset_id):
    """
    Checks whether an element is on a given workset

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param el: The element.
    :type el: Autodesk.Revit.DB.Element
    :param workset_id: The workset element Id
    :type workset_id: Autodesk.Revit.DB.ElementId

    :return: True if element is on given workset, otherwise False
    :rtype: bool
    """

    flag = True
    try:
        ws_param = el.get_Parameter(BuiltInParameter.ELEM_PARTITION_PARAM)
        current_workset_name = rParaGet.get_parameter_value(ws_param)
        compare_to_workset_name = get_workset_name_by_id(doc, workset_id.IntegerValue)
        if compare_to_workset_name != current_workset_name:
            flag = False
    except Exception as e:
        print("is_element_on_workset_by_id: {}".format(e))
        flag = False
    return flag


def is_element_on_workset_by_name(el, workset_name):
    """
    Checks whether an element is on a workset identified by name

    :param el: The element
    :type el: Autodesk.Revit.DB.Element
    :param workset_name: The name of the workset
    :type workset_name: str

    :return: True if element is on given workset, otherwise False
    :rtype: bool
    """

    flag = True
    try:
        ws_param = el.get_Parameter(BuiltInParameter.ELEM_PARTITION_PARAM)
        current_workset_name = rParaGet.get_parameter_value(ws_param)
        if workset_name != current_workset_name:
            flag = False
    except Exception as e:
        print("IsElementOnWorksetByName: {}".format(e))
        flag = False
    return flag


def get_element_workset_name(el):
    """
    Returns the name of the workset an element is on, or 'invalid workset'.

    :param el: The element.
    :type el: Autodesk.Revit.DB.Element
    :return: The name of the workset. If an exception occurred it wil return 'invalid workset'.
    :rtype: str
    """

    work_setname = "invalid workset"
    try:
        ws_param = el.get_Parameter(BuiltInParameter.ELEM_PARTITION_PARAM)
        work_setname = rParaGet.get_parameter_value(ws_param)
    except Exception as e:
        print("GetElementWorksetName: " + str(e))
    return work_setname


def update_workset_default_visibility_from_report(doc, report_path, revit_file_path):
    """
    Updates the default visibility of worksets based on a workset report file.

    The data for the report files is generated by GetWorksetReportData() function in this module

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param report_path: The fully qualified file path to tab separated report text file containing workset data.
    :type report_path: str
    :param revit_file_path: The fully qualified file path of the Revit file. Will be used to identify the file in the report data.
    :type revit_file_path: str

    :return:
        Result class instance.

        - .status = True if:

            - successfully updated all workset default visibility where different to report
            - or none needed updating.

        - Otherwise False:

            - An exception occurred.
            - A workset has no matching data in the report.

        - Common:

            - .message will contain each workset and whether it needed updating or not

    :rtype: :class:`.Result`
    """

    return_value = res.Result()
    # read report
    workset_data = filesTab.read_tab_separated_file(report_path)
    file_name = filesIO.get_file_name_without_ext(revit_file_path)
    workset_data_for_file = {}
    for row in workset_data:
        if (
            filesIO.get_file_name_without_ext(row[0]).startswith(file_name)
            and len(row) > 3
        ):
            workset_data_for_file[row[1]] = util.parse_string_to_bool(row[3])
    if len(workset_data_for_file) > 0:
        # updates worksets
        worksets = get_worksets(doc)
        for workset in worksets:
            if str(workset.Id) in workset_data_for_file:
                if workset.IsVisibleByDefault != workset_data_for_file[str(workset.Id)]:

                    def action():
                        action_return_value = res.Result()
                        default_visibility = WorksetDefaultVisibilitySettings.GetWorksetDefaultVisibilitySettings(
                            doc
                        )
                        try:
                            default_visibility.SetWorksetVisibility(
                                workset.Id, workset_data_for_file[str(workset.Id)]
                            )
                            action_return_value.update_sep(
                                True,
                                "{}: default visibility settings changed to: \t[{}]".format(
                                    workset.Name, workset_data_for_file[str(workset.Id)]
                                ),
                            )
                        except Exception as e:
                            action_return_value.update_sep(
                                False, "Failed with exception: {}".format(e)
                            )
                        return action_return_value

                    # move element to new workset
                    transaction = Transaction(
                        doc,
                        "{}: Changing default workset visibility".format(workset.Name),
                    )
                    tranny_status = rTran.in_transaction(transaction, action)
                    return_value.update(tranny_status)
                else:
                    return_value.update_sep(
                        True,
                        "{}: default visibility settings unchanged.".format(
                            util.encode_ascii(workset.Name)
                        ),
                    )
            else:
                return_value.update_sep(
                    False,
                    "{}: has no corresponding setting in settings file.".format(
                        util.encode_ascii(workset.Name)
                    ),
                )
    else:
        return_value.update_sep(
            True, "No settings found for file: {}".format(file_name)
        )
    return return_value


def create_workset(doc, workset_name):
    """
    Creates a workset with a given name in a document.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param workset_name: The name of the workset to be created
    :type workset_name: str

    :return:
        Result class instance.

        - .status = True if:

            - successfully created the workset

        - Otherwise False:

            - An exception occurred.
            - A workset with that name already exists.
            - Document is not workshared

        - Common:

            - .message will contain each workset

        .result will contain the workset element in a list if successfully created, otherwise an empty list.

    :rtype: :class:`.Result`
    """

    return_value = res.Result()
    if doc.IsWorkshared:
        if WorksetTable.IsWorksetNameUnique(doc, workset_name):

            def action():
                action_return_value = res.Result()
                try:
                    new_workset = Workset.Create(doc, workset_name)
                    action_return_value.update_sep(
                        True, "Workset {} created.".format(workset_name)
                    )
                    action_return_value.result.append(new_workset)
                except Exception as e:
                    action_return_value.update_sep(
                        False,
                        "Failed to create workset {} with exception: {}".format(
                            workset_name, e
                        ),
                    )
                return action_return_value

            transaction = Transaction(doc, "Adding workset {}".format(workset_name))
            tranny_status = rTran.in_transaction(transaction, action)
            return_value.update(tranny_status)
        else:
            return_value.update_sep(
                False, "Workset name already exists: {}".format(workset_name)
            )
    else:
        return_value.update_sep(
            False, "Cant create a workset in a non workshared file."
        )
    return return_value


def delete_workset(doc, delete_workset_name, move_elements_to_workset_name=None):
    """
    deletes a workset given by name

    if a move elements to workset name is provided, delete workset settings will be set accordingly

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param delete_workset_name: The name of the workset to be deleted
    :type delete_workset_name: str
    :param move_elements_to_workset_name: The name of the workset elements to be moved to. If None all elements on the workset will be deleted.
    :type move_elements_to_workset_name: str (default is None)

    :return:
        Result class instance.

        - .status = True if:

            - successfully deleted the workset

        - Otherwise False:

            - An exception occurred.
            - Revit cant delete the workset with the settings provided.
            - Document is not workshared

        .result will contain an empty list.

    :rtype: :class:`.Result`
    """

    return_value = res.Result()
    try:
        if doc.IsWorkshared:
            # get the id of the workset to be deleted
            workset_id_delete = get_workset_id_by_name(doc, delete_workset_name)
            # check if workset name is valid
            if workset_id_delete == ElementId.InvalidElementId:
                raise ValueError(
                    "To be deleted workset {} does not exist in file.".format(
                        delete_workset_name
                    )
                )
            else:
                return_value.append_message(
                    "workset {} found in model.".format(delete_workset_name)
                )

            # set up delete setting
            delete_workset_settings = None

            if move_elements_to_workset_name is not None:
                return_value.append_message(
                    "Attempting to move elements to workset: {}".format(
                        move_elements_to_workset_name
                    )
                )
                # get the target workset id
                workset_id_target = get_workset_id_by_name(
                    doc, move_elements_to_workset_name
                )
                # check if workset name is valid
                if workset_id_target == ElementId.InvalidElementId:
                    raise ValueError(
                        "Target workset {} does not exist in file.".format(
                            move_elements_to_workset_name
                        )
                    )
                # set up delete settings
                delete_workset_settings = DeleteWorksetSettings(
                    DeleteWorksetOption.MoveElementsToWorkset, workset_id_target
                )
            else:
                return_value.append_message(
                    "Deleting all elements on workset: {}".format(delete_workset_name)
                )
                # delete all elements on the workset provided
                delete_workset_settings = DeleteWorksetSettings()

            # check if workset can be deleted
            if WorksetTable.CanDeleteWorkset(
                doc, workset_id_delete, delete_workset_settings
            ):
                return_value.append_message(
                    "Revit allows to delete workset: {}".format(delete_workset_name)
                )
                # set up the delete action
                def action():
                    action_return_value = res.Result()
                    try:
                        WorksetTable.DeleteWorkset(
                            doc, workset_id_delete, delete_workset_settings
                        )
                        action_return_value.update_sep(
                            True, "Workset {} deleted.".format(delete_workset_name)
                        )
                    except Exception as e:
                        action_return_value.update_sep(
                            False,
                            "Failed to delete workset {} with exception: {}".format(
                                delete_workset_name, e
                            ),
                        )
                    return action_return_value

                # execute the delete action
                transaction = Transaction(
                    doc, "Deleting workset {}".format(delete_workset_name)
                )
                # delete the workset at all costs. (attempt to swallow up any warnings / errors revit may produce)
                tranny_status = rTran.in_transaction_with_failure_handling(
                    transaction, action
                )
                return_value.update(tranny_status)

            else:
                return_value.update_sep(
                    False,
                    "Can't delete workset {} with settings: {}. (Revit says NO!)".format(
                        delete_workset_name, delete_workset_settings
                    ),
                )
        else:
            return_value.update_sep(
                False, "Cant delete a workset in a non workshared file."
            )
    except Exception as e:
        return_value.update_sep(
            False,
            "An exception {} occurred when attempting to delete workset: {}".format(
                delete_workset_name, e
            ),
        )
    return return_value
