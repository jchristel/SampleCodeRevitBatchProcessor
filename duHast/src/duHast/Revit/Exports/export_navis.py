"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of functions around exporting from Revit to nwc file format.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright © 2023, Jan Christel
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

import Autodesk.Revit.DB as rdb

from duHast.Revit.Views import views as rView
from duHast.Utilities.Objects import result as res
from duHast.Revit.Exports.export import build_export_file_name_from_view


def setup_nwc_custom_export_option(
    using_shared_coordinates,
    export_entire_model,
    export_links,
    split_model_by_level,
    export_parts,
    export_room_as_attributes,
    export_room_geometry,
    find_missing_materials,
    navis_parameters=rdb.NavisworksParameters.All,
    convert_element_properties=False,
):
    """
    Return an NWC Export Options object as per values past oin.
    :param using_shared_coordinates: True shared coordinates will be used, otherwise project internal
    :type using_shared_coordinates: bool
    :param export_entire_model: True entire model will be exported, otherwise specific view.
    :type export_entire_model: bool
    :param export_links: True: Revit links will also be exported, otherwise not.
    :type export_links: bool
    :param split_model_by_level: True: model elements will be split by level, otherwise not.
    :type split_model_by_level: bool
    :param export_parts: True parts will be exported, otherwise not.
    :type export_parts: bool
    :param export_room_as_attributes: True room properties will be exported (can be slow!), otherwise not.
    :type export_room_as_attributes: bool
    :param export_room_geometry: True room geometry will be exported, otherwise not.
    :type export_room_geometry: bool
    :param find_missing_materials: True exporter will attempt to find missing materials, otherwise not
    :type find_missing_materials: bool

    :param navis_parameters: Options which specifies the parameter conversion of Navisworks Exporter. Default value is All.
    :type navis_parameters: Autodesk.Revit.DB.NavisworksParameters

    :param convert_element_properties: True to convert element properties, false otherwise. Default value is false.
    :type convert_element_properties: bool

    :return: A Navisworks .nwc export option.
    :rtype: Autodesk.Revit.DB.NavisworksExportOptions
    """

    ex_nwc = rdb.NavisworksExportOptions()
    ex_nwc.Coordinates = (
        rdb.NavisworksCoordinates.Shared
        if using_shared_coordinates == True
        else rdb.NavisworksCoordinates.Internal
    )
    ex_nwc.ExportScope = (
        rdb.NavisworksExportScope.Model
        if export_entire_model == True
        else rdb.NavisworksExportScope.View
    )
    ex_nwc.ExportLinks = export_links
    ex_nwc.DivideFileIntoLevels = split_model_by_level
    ex_nwc.ExportParts = export_parts
    ex_nwc.ExportRoomAsAttribute = export_room_as_attributes
    ex_nwc.ExportRoomGeometry = export_room_geometry
    ex_nwc.FindMissingMaterials = find_missing_materials
    ex_nwc.ConvertElementProperties = convert_element_properties
    ex_nwc.Parameters = navis_parameters

    return ex_nwc


def setup_nwc_default_export_option_shared_by_view():
    """
    Return an NWC Export Options object with shared coordinates, export by View.
    :return: A Navisworks .nwc export option.
    :rtype: Autodesk.Revit.DB.NavisworksExportOptions
    """

    return setup_nwc_custom_export_option(
        using_shared_coordinates=True,
        export_entire_model=False,
        export_links=False,
        split_model_by_level=True,
        export_parts=True,
        export_room_as_attributes=False,
        export_room_geometry=False,
        find_missing_materials=False,
    )


def export_to_nwc(doc, nwc_export_option, directory_path, file_name):
    """
    Function exporting either entire model or view to NWC
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param nwc_export_option: A Navisworks .nwc export option.
    :type nwc_export_option: Autodesk.Revit.DB.NavisworksExportOptions
    :param directory_path: The directory path to where the export is being saved.
    :type directory_path: str
    :param file_name: The file name under which the export is being saved.
    :type file_name: str
    :return:
        Result class instance.
        - Export status returned in result.status. False if an exception occurred, otherwise True.
        - result.message will contain the fully qualified file path of the exported file.
        On exception:
        - result.status (bool) will be False.
        - result.message will contain the exception message.
    :rtype: :class:`.Result`
    """

    # nwc export does not need to run in a transaction
    return_value = res.Result()
    try:
        # export to NWC
        doc.Export(directory_path, file_name, nwc_export_option)
        return_value.update_sep(
            True, "Exported: {}".format(directory_path + "\\" + str(file_name))
        )
        # needs to be a list in a list to stay together when combined with previous results in the update status result code
        return_value.result = [[directory_path, file_name]]
    except Exception as e:
        return_value.update_sep(
            False,
            "Script Exception: Failed to export to NWC with exception: {}".format(e),
        )
    return return_value


def export_model_to_nwc(doc, nwc_export_option, directory_path, file_name):
    """
    Function exporting the entire model to NWC.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param nwc_export_option: A Navisworks .nwc export option.
    :type nwc_export_option: Autodesk.Revit.DB.NavisworksExportOptions
    :param directory_path: The directory path to where the export is being saved.
    :type directory_path: str
    :param file_name: The file name under which the export is being saved.
    :type file_name: str
    :return:
        Result class instance.
        - Export status returned in result.status. False if an exception occurred, otherwise True.
        - result.message will contain the fully qualified file path of the exported file.
        On exception:
        - result.status (bool) will be False.
        - result.message will contain the exception message.
    :rtype: :class:`.Result`
    """

    return_value = res.Result()
    return_value_by_model = export_to_nwc(
        doc, nwc_export_option, directory_path, file_name
    )
    return_value.update(return_value_by_model)
    return return_value


def export_3d_views_to_nwc(
    doc,
    view_filter,
    nwc_export_option,
    directory_path,
    do_something_with_view_name=None,
):
    """
    Function exporting 3D views matching a filter (view starts with) to NWC.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param view_filter: String the view name is to start with if it is to be exported. (Both view name and string are set to lower at comparison)
    :type view_filter: str
    :param nwc_export_option: A Navisworks .nwc export option.
    :type nwc_export_option: Autodesk.Revit.DB.NavisworksExportOptions
    :param directory_path: The directory path to where the export is being saved.
    :type directory_path: str
    :param do_something_with_view_name: A function which takes as an argument the view name and does something with it. The modified view name is afterwards used as the actual file name, defaults to None which uses the view name unchanged as the export file name.
    :type do_something_with_view_name: function , optional
    :return:
        Result class instance.
        - Export status returned in result.status. False if an exception occurred, otherwise True.
        - result.message will contain the fully qualified file path of the exported file.
        On exception:
        - result.status (bool) will be False.
        - result.message will contain the exception message.
    :rtype: :class:`.Result`
    """

    return_value = res.Result()
    views_to_export = []
    # get all 3D views in model and filter out views to be exported
    views = rView.get_views_of_type(doc, rdb.ViewType.ThreeD)
    for v in views:
        if v.Name.lower().startswith(view_filter.lower()):
            views_to_export.append(v)
    # export those views one by one
    if len(views_to_export) > 0:
        for export_view in views_to_export:
            return_value_by_view = res.Result()
            # store view ID in export option
            nwc_export_option.ViewId = export_view.Id
            file_name = (
                build_export_file_name_from_view(export_view.Name, view_filter, ".nwc")
                if do_something_with_view_name == None
                else do_something_with_view_name(export_view.Name)
            )
            return_value_by_view = export_to_nwc(
                doc, nwc_export_option, directory_path, file_name
            )
            return_value.update(return_value_by_view)
    else:
        return_value.update_sep(
            True, "NWC Export: No 3D views found matching filter...nothing was exported"
        )
    return return_value
