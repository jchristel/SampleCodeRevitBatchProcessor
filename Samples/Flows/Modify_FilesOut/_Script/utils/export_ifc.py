"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Module containing IFC export functions.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# License:
#
#
# Revit Batch Processor Sample Code
#
# Copyright (c) 2020  Jan Christel
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

# --------------------------
# Imports
# --------------------------

from duHast.Utilities.Objects import result as res
from duHast.Utilities.files_io import file_exist
from duHast.Utilities.solibri_ifc_optimizer import optimize_ifc_files_in_list
from duHast.Revit.Exports.export_ifc import (
    export_3d_views_to_ifc,
)
from duHast.Revit.Exports.Utility.ifc_export_coordinates import IFCCoords
from utils.RevitExportIFCConfigSpecific import (
    ifc_get_third_party_export_config_by_view_2022,
)
import os


# optimizes ifc files after export
def optimize_ifc_files(export_status, ifc_file_directory):
    """
    _summary_

    :param export_status: Result class instance created by the export process.
    :type export_status: :class:`.Result`
    :param ifc_file_directory: Directory containing ifc files.
    :type ifc_file_directory: str

    :return:
        Result class instance.

        - optimize ifc file status returned in result.status. False if an exception occurred, otherwise True.
        - result.message will contain message marker text and status as string.
        - result.result will be an empty list

        On exception:

        - result.status (bool) will be False.
        - result.message will contain the exception message.
        - result.result will be an empty list.

    :rtype: :class:`.Result`
    """

    return_value = res.Result()
    ifcFiles = []
    if export_status.status == True:
        if export_status.result is not None and len(export_status.result) > 0:
            for export_name in export_status.result:
                # check if file exists...
                current_full_file_name = os.path.join(export_name[0], export_name[1])
                if file_exist(current_full_file_name):
                    ifcFiles.append(current_full_file_name)
                else:
                    return_value.append_message(
                        "File not found: {}".format(current_full_file_name)
                    )
            # start the optimization, save files in same directory
            ifc_optimize_status = optimize_ifc_files_in_list(
                ifcFiles, ifc_file_directory
            )
            return_value.update(ifc_optimize_status)
        else:
            return_value.update_sep(
                True, "No IFC files optimized since nothing was exported"
            )
    else:
        return_value.update_sep(
            True, "No IFC files optimized since nothing was exported"
        )
    return return_value


def check_name(view, view_filter_list):
    """
    Checks whether view name starts with a value provided in view filter list.

    :param view: The view to be checked
    :type view: Autodesk.Revit.DB.View
    :param view_filter_list: List of view filter strings. Functions checks whether view name to lower case starts with any of the filter strings provided.
    :type view_filter_list: [str]
    :return: True if none of the view filter strings matches, otherwise False
    :rtype: bool
    """

    value = True
    for prefix in view_filter_list:
        if view.Name.lower().startswith(prefix.lower()):
            value = False
            break
    return value


# ----------------------------------export----------------------------------


def get_ifc_third_party_export_config(doc):
    """
    Get's a custom IFC export config defined in module RevitExportIFCConfigSpecific

    :param doc: The current model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: An IFCExportconfig object.
    :rtype: BIM.IFC.Export.UI.IFCExportConfiguration
    """

    return ifc_get_third_party_export_config_by_view_2022(doc=doc)


def export_views_to_ifc(doc, export_view_prefix, export_directory):
    """
    Exports 3D views to ifc where the view name has a particular prefix.

    :param doc: The current model document.
    :type doc: Autodesk.Revit.DB.Document
    :param export_view_prefix: View filter: only 3D views which start with provided string will be exported
    :type export_view_prefix: str
    :param export_directory: The fully qualified directory path to save the export to.
    :type export_directory: str

    :return:
        Result class instance.

        - Export status returned in result.status. False if an exception occurred, otherwise True.
        - result.message will contain export message as string.
        - result.result will be a list of fully qualified file path with one entry per exported view

        On exception:

        - result.status (bool) will be False.
        - result.message will contain the exception message.
        - result.result will be an empty list.

    :rtype: :class:`.Result`
    """

    return_value = res.Result()
    ifc_export_config = get_ifc_third_party_export_config(doc)
    return_value = export_3d_views_to_ifc(
        doc=doc,
        view_filter=export_view_prefix,
        ifc_export_config=ifc_export_config,
        directory_path=export_directory,
        ifc_coordinates_system=IFCCoords.SharedCoordinates,
        do_something_with_view_name=build_export_file_name_from_view_ifc,
    )
    return return_value


def build_export_file_name_from_view_ifc(
    view_name,
    export_view_prefix,
    file_data,
    ifc_file_extension,
    use_revit_file_revision,
    current_revit_file_revision,
):
    """
    Creates the ifc file name based on the view the file gets exported from.

    - Includes revision information
    - If view starts with predefined Prefix, that prefix will be removed from the name

    :param view_name: The view name.
    :type view_name: str

    :return: The file name based on the view name.
    :rtype: str
    """

    # return newFileName
    if view_name.startswith(
        export_view_prefix,
    ):
        lenPrefix = len(
            export_view_prefix,
        )
        view_name = view_name[lenPrefix:]

        # this is required since the view name does not match the file name required at end of export
        for fd in file_data:
            if (
                fd.existingFileName == view_name
                and fd.fileExtension == ifc_file_extension
            ):
                # may need to update the revision info!
                if use_revit_file_revision:
                    # update the revision to the current revit file revision
                    fd.revision = current_revit_file_revision
                else:
                    # increase rev counter for this file
                    fd.upDateNumericalRev()
                view_name = fd.getNewFileName()
                break

    return view_name + ifc_file_extension
