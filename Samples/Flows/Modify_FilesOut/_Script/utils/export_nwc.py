"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Module containing NWC export functions.
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


from duHast.Revit.Exports.export_navis import (
    setup_nwc_default_export_option_shared_by_view,
    export_3d_views_to_nwc,
)
from duHast.Utilities.Objects import result as res


def set_up_nwc_default_export_option():
    """
    Return an NWC Export Options object with shared coordinates, export by View as provided in the generic library

    :return: _description_
    :rtype: _type_
    """
    return setup_nwc_default_export_option_shared_by_view()


def export_views_to_nwc(doc, export_view_prefix, export_directory):
    """
    Exports 3D views to nwc where the view name has a particular prefix.

    :param doc: The current model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: _description_
    :rtype: _type_
    """

    return_value = res.Result()
    nwc_export_option = set_up_nwc_default_export_option()
    return_value = export_3d_views_to_nwc(
        doc,
        export_view_prefix,
        nwc_export_option,
        export_directory,
        build_export_file_name_from_view_nwc,
    )
    return return_value


def build_export_file_name_from_view_nwc(
    view_name,
    export_view_prefix,
    file_data,
    nwc_file_extension,
    use_revit_file_revision,
    current_revit_file_revision,
):
    """
    Creates the nwc file name based on the view the file gets exported from.

    - Includes revision information
    - If view starts with predefined Prefix, that prefix will be removed from the name

    :param view_name: The view name.
    :type view_name: str

    :return: The file name based on the view name.
    :rtype: str
    """

    len_prefix = len(export_view_prefix)
    # check if view name starts with NWC_
    if view_name.startswith(export_view_prefix):
        view_name = view_name[len_prefix:]
        # this is required since the view name does not match the file name required at end of export
        for fd in file_data:
            if (
                fd.existingFileName == view_name
                and fd.fileExtension == nwc_file_extension
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
    return view_name + nwc_file_extension
