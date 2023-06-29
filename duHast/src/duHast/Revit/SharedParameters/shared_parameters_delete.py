"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to deleting Revit shared parameters.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
#
# License:
#
#
# Revit Batch Processor Sample Code
#
# Copyright (c) 2023  Jan Christel
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#

import Autodesk.Revit.DB as rdb

from duHast.Utilities.Objects import result as res
from duHast.Utilities import utility as util
from duHast.Revit.SharedParameters.shared_parameters import (
    check_whether_shared_parameters_are_in_file,
    get_all_shared_parameters,
)
from duHast.Revit.Common import delete as rDel


def delete_shared_parameter_by_name(doc, shared_parameter_name):
    """
    Deletes a single shared parameter based on a name provided.
    param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param shared_parameter_name: The name of the shared parameter.
    :type shared_parameter_name: str
    :return:
        Result class instance.
        - Parameter delete status returned in result.status. False if an exception occurred, otherwise True.
        - result.message will contain the name of the shared parameter.
        - result.status will be an empty list.
        On exception (handled by optimizer itself!):
        - result.status (bool) will be False.
        - result.message will contain generic exception message.
        - result.status will be an empty list
    :rtype: :class:`.Result`
    """

    return_value = res.Result()
    paras = get_all_shared_parameters(doc)
    delete_ids = []
    parameter_name = "Unknown"
    for p in paras:
        if p.Name == shared_parameter_name:
            delete_ids.append(p.Id)
            # there should just be one match
            parameter_name = util.encode_ascii(rdb.Element.Name.GetValue(p))
            break
    if len(delete_ids) > 0:
        return_value = rDel.delete_by_element_ids(
            doc, delete_ids, "Delete Shared Parameter", parameter_name
        )
    else:
        return_value.update_sep(
            False,
            "parameter with guid: "
            + shared_parameter_name
            + " does not exist in file.",
        )
    return return_value


def delete_shared_parameter_by_guid(doc, guid):
    """
    Deletes a single shared parameter based on a guid provided.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param guid: A shared parameter GUID as string.
    :type guid: str
    :return:
        Result class instance.
        - Parameter delete status returned in result.status. False if an exception occurred, otherwise True.
        - result.message will contain the name of the shared parameter.
        - result.status will be an empty list.
        On exception (handled by optimizer itself!):
        - result.status (bool) will be False.
        - result.message will contain generic exception message.
        - result.status will be an empty list
    :rtype: :class:`.Result`
    """

    return_value = res.Result()
    paras = get_all_shared_parameters(doc)
    delete_ids = []
    parameter_name = "Unknown"
    for p in paras:
        if p.GuidValue.ToString() == guid:
            delete_ids.append(p.Id)
            # there should just be one match
            parameter_name = util.encode_ascii(rdb.Element.Name.GetValue(p))
            break
    if len(delete_ids) > 0:
        return_value = rDel.delete_by_element_ids(
            doc, delete_ids, "Delete Shared Parameter", parameter_name
        )
    else:
        return_value.update_sep(
            False, "parameter with guid: " + guid + " does not exist in file."
        )
    return return_value


def delete_shared_parameters(doc, parameter_gui_ds):
    """
    Deletes shared parameters by GUID from document.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param parameter_gui_ds: List of shared parameter GUIDs as string.
    :type parameter_gui_ds: list str
    :return:
        Result class instance.
        - Parameter deletion status returned in result.status. False if an exception occurred, otherwise True.
        - result.message will contain the name of the shared parameter deleted.
        On exception (handled by optimizer itself!):
        - result.status (bool) will be False.
        - result.message will contain generic exception message.
    :rtype: :class:`.Result`
    """

    return_value = res.Result()
    one_got_deleted = False
    delete_gui_ds = check_whether_shared_parameters_are_in_file(doc, parameter_gui_ds)
    if len(delete_gui_ds) > 0:
        for delete_guid in delete_gui_ds:
            delete_status = delete_shared_parameter_by_guid(doc, delete_guid)
            # preserve TRUE value!
            if delete_status.status == True:
                one_got_deleted = True
            return_value.update(delete_status)
        return_value.update_sep(one_got_deleted, "Finished deleting parameters!")
    else:
        return_value.update_sep(True, "No matching shared parameters in file!")

    return return_value
