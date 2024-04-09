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

# --------------------------
# Imports
# --------------------------

import settings as settings  # sets up all commonly used variables and path locations!
from duHast.Utilities.Objects import result as res
from duHast.Utilities.files_io import file_exist
from duHast.Utilities.solibri_ifc_optimizer import optimize_ifc_files_in_list
from duHast.Revit.Exports.export_ifc import (
    export_3d_views_to_ifc,
)
from duHast.Revit.Exports.Utility.ifc_export_coordinates import IFCCoords
from RevitExportIFCConfigSpecific import (
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
        if any(export_status.result):
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


def check_view_name(
    view,
    view_filter_list=[settings.EXPORT_NWC_VIEW_PREFIX, settings.EXPORT_IFC_VIEW_PREFIX],
):
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


def export_views_to_ifc(doc, export_view_prefix, export_directory, view_name_modifier):
    """
    Exports 3D views to ifc where the view name has a particular prefix.

    :param doc: The current model document.
    :type doc: Autodesk.Revit.DB.Document
    :param export_view_prefix: View filter: only 3D views which start with provided string will be exported
    :type export_view_prefix: str
    :param export_directory: The fully qualified directory path to save the export to.
    :type export_directory: str
    :param view_name_modifier: A function taking the view name, making some modifications to it and returning it (i.e. as the file name to be used)
    :type view_name_modifier: func(view_name)

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
    try:
        ifc_export_config = get_ifc_third_party_export_config(doc)
        return_value = export_3d_views_to_ifc(
            doc=doc,
            view_filter=export_view_prefix,
            ifc_export_config=ifc_export_config,
            directory_path=export_directory,
            ifc_coordinates_system=IFCCoords.shared_coordinates,
            do_something_with_view_name=view_name_modifier,
        )
    except Exception as e:
        return_value.update_sep(False, "Error exporting views to IFC: {}".format(e))
    return return_value
