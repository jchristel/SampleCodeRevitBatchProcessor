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

from duHast.Revit.Common import transaction as rTran
from duHast.Revit.Common.revit_version import get_revit_version_number
from duHast.Utilities.Objects import result as res
from duHast.Revit.Views import views as rView
from duHast.Revit.Exports.export import build_export_file_name_from_view
from duHast.Revit.Exports.Utility.ifc_export_coordinates import IFCCoords
from duHast.Revit.Exports.Utility.ifc_export_space_boundaries import IFCSpaceBoundaries

from duHast.Revit.Exports.Utility.export_ifc_config_2019 import (
    ifc_get_third_party_export_config_by_model_2019,
    ifc_get_third_party_export_config_by_view_2019,
)
from duHast.Revit.Exports.Utility.export_ifc_config_2020 import (
    ifc_get_third_party_export_config_by_model_2020,
    ifc_get_third_party_export_config_by_view_2020,
)
from duHast.Revit.Exports.Utility.export_ifc_config_2021 import (
    ifc_get_third_party_export_config_by_model_2021,
    ifc_get_third_party_export_config_by_view_2021,
)
from duHast.Revit.Exports.Utility.export_ifc_config_2022 import (
    ifc_get_third_party_export_config_by_model_2022,
    ifc_get_third_party_export_config_by_view_2022,
)
from duHast.Revit.Exports.Utility.export_ifc_config_2023 import (
    ifc_get_third_party_export_config_by_model_2023,
    ifc_get_third_party_export_config_by_view_2023,
)


def ifc_get_export_config_by_view(
    ifc_version, ifc_space_bounds=IFCSpaceBoundaries.no_boundaries
):
    """
    Returns an IFC export configuration for the built in IFC exporter.
    :param ifc_version: The ifc version used for the export.
    :type ifc_version: Autodesk.Revit.DB.IFCVersion
    :param ifc_space_bounds: IFC space boundary setting, defaults to IFCSpaceBoundaries.noBoundaries
    :type ifc_space_bounds: SampleCodeBatchProcessor.RevitExport.IFCSpaceBoundaries, optional
    :return: an IFC export option
    :rtype: Autodesk.Revit.DB.IFCExportOptions
    """

    ex_ifc = rdb.IFCExportOptions()
    ex_ifc.ExportBaseQuantities = True
    ex_ifc.FileVersion = ifc_version
    ex_ifc.SpaceBoundaryLevel = ifc_space_bounds
    ex_ifc.WallAndColumnSplitting = True
    return ex_ifc


def export_to_ifc(doc, ifc_export_option, directory_path, file_name):
    """
    Exports to IFC either the entire model or a view only using 3rd party exporter.
    What gets exported is defined in the ifc_export_option.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param ifc_export_option: The settings for the IFC export.
    :type ifc_export_option: Autodesk.Revit.DB IFCExportOptions
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

    # ifc export needs to run in a transaction
    return_value = res.Result()

    def action():
        action_return_value = res.Result()
        try:
            # export to IFC
            doc.Export(directory_path, file_name, ifc_export_option)
            action_return_value.update_sep(
                True, "Exported: {}".format(directory_path + "\\" + str(file_name))
            )
            # needs to be a list in a list to stay together when combined with previous results in the update status result code
            action_return_value.result = [[directory_path, file_name]]
        except Exception as e:
            action_return_value.update_sep(
                False,
                "Script Exception: Failed to export to IFC with exception: {}".format(
                    e
                ),
            )
        return action_return_value

    transaction = rdb.Transaction(doc, "Export to IFC")
    return_value = rTran.in_transaction(transaction, action)
    return return_value


def export_3d_views_to_ifc_default(doc, view_filter, ifc_export_option, directory_path):
    """
    Exports 3D views matching a filter (view starts with) to IFC using the default built in exporter.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param view_filter: String the view name is to start with if it is to be exported. (Both view name and string are set to lower at comparison)
    :type view_filter: str
    :param ifc_export_option: The IFC export option.
    :type ifc_export_option: Autodesk.Revit.DB.IFCExportOptions
    :param directory_path: The directory path to where the export is being saved.
    :type directory_path: str
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
            ifc_export_option.FilterViewId = export_view.Id
            file_name = build_export_file_name_from_view(
                export_view.Name, view_filter, ".ifc"
            )
            return_value_by_view = export_to_ifc(
                doc, ifc_export_option, directory_path, file_name
            )
            return_value.update(return_value_by_view)
    else:
        return_value.update_sep(
            True, "No 3D views found matching filter...nothing was exported"
        )
    return return_value


def setup_ifc_export_option(
    export_config,
    view_id=rdb.ElementId.InvalidElementId,
    coord_option=IFCCoords.shared_coordinates,
):
    """
    Function assigning a view Id to export ifc config if it is exporting by view.
    By model export will assign Autodesk.Revit.DB.ElementId.InvalidElementId instead.
    :param export_config: The ifc export configuration used.
    :type export_config: BIM.IFC.Export.UI.IFCExportConfiguration
    :param view_id: The id of the view to be exported, defaults to ElementId.InvalidElementId
    :type view_id: Autodesk.Revit.DB.ElementId, optional
    :param coord_option: Describes the coordinate options used for the export, defaults to IFCCoords.SharedCoordinates
    :type coord_option: SampleCodeBatchProcessor.RevitExport.IFCCoords, optional
    :return: An updated ifc export option instance.
    :rtype: Autodesk.Revit.DB.IFCExportOptions
    """

    if export_config.UseActiveViewGeometry == True:
        export_config.ActiveViewId = view_id.IntegerValue
    else:
        export_config.ActiveViewId = -1
    # set up the ifc export options object
    ex_ifc = rdb.IFCExportOptions()
    export_config.UpdateOptions(ex_ifc, view_id)

    # set the coordinate system to use
    ex_ifc.AddOption("SitePlacement", coord_option)

    return ex_ifc


def export_3d_views_to_ifc(
    doc,
    view_filter,
    ifc_export_config,
    directory_path,
    ifc_coordinates_system=IFCCoords.shared_coordinates,
    do_something_with_view_name=None,
):
    """
    Function exporting 3D views matching a filter (view starts with) to IFC using 3rd party exporter.
    By default the file name of the export will be same as the name of the view exported.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param view_filter: String the view name is to start with if it is to be exported. (Both view name and string are set to lower at comparison)
    :type view_filter: str
    :param ifc_export_config: The IFC export configuration.
    :type ifc_export_config: BIM.IFC.Export.UI.IFCExportConfiguration
    :param directory_path: The directory path to where the export is being saved.
    :type directory_path: str
    :param ifc_coordinates_system: Describes the coordinate options used for the export, defaults to IFCCoords.SharedCoordinates
    :type ifc_coordinates_system: SampleCodeBatchProcessor.RevitExport.IFCCoords, optional
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
            updated_export_option = setup_ifc_export_option(
                ifc_export_config, export_view.Id, ifc_coordinates_system
            )
            file_name = (
                build_export_file_name_from_view(export_view.Name, view_filter, ".ifc")
                if do_something_with_view_name == None
                else do_something_with_view_name(export_view.Name)
            )
            return_value_by_view = export_to_ifc(
                doc, updated_export_option, directory_path, file_name
            )
            return_value.update(return_value_by_view)
    else:
        return_value.update_sep(
            True, "No 3D views found matching filter...nothing was exported"
        )
    return return_value


def export_model_to_ifc(
    doc,
    ifc_export_config,
    directory_path,
    file_name,
    coord_option=IFCCoords.shared_coordinates,
):
    """
    Function exporting the entire model to IFC using 3rd party exporter.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param ifc_export_config: The IFC export configuration.
    :type ifc_export_config: BIM.IFC.Export.UI.IFCExportConfiguration
    :param directory_path: The directory path to where the export is being saved.
    :type directory_path: str
    :param file_name: The file name under which the export is being saved.
    :type file_name: str
    :param coord_option: Describes the coordinate options used for the export, defaults to IFCCoords.SharedCoordinates
    :type coord_option: SampleCodeBatchProcessor.RevitExport.IFCCoords, optional

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
    # need to create an export option from the export config
    ifc_export_option = setup_ifc_export_option(
        export_config=ifc_export_config,
        view_id=rdb.ElementId.InvalidElementId,
        coord_option=coord_option,
    )

    return_value_by_model = export_to_ifc(
        doc, ifc_export_option, directory_path, file_name
    )
    return_value.update(return_value_by_model)
    return return_value


def ifc_get_third_party_export_config_by_model(doc, ifc_version, ifc_settings=None):
    """
    Returns the 3rd party ifc config for export by model depending on revit version.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param ifc_version: The ifc version used for the export.
    :type ifc_version: Autodesk.Revit.DB.IFCVersion
    :raises ValueError: Raises an exception if the revit version in use is not supported by this script.
    :return: An ifc export config instance based on the Revit version.
    :rtype: BIM.IFC.Export.UI.IFCExportConfiguration
    """

    # get the revit version:
    revit_version = get_revit_version_number(doc=doc)
    ifc_config = None
    if revit_version == 2019:
        ifc_config = ifc_get_third_party_export_config_by_model_2019(
            ifc_version, ifc_settings
        )
    elif revit_version == 2020:
        ifc_config = ifc_get_third_party_export_config_by_model_2020(
            ifc_version, ifc_settings
        )
    elif revit_version == 2021:
        ifc_config = ifc_get_third_party_export_config_by_model_2021(
            ifc_version, ifc_settings
        )
    elif revit_version == 2022:
        ifc_config = ifc_get_third_party_export_config_by_model_2022(
            ifc_version, ifc_settings
        )
    elif revit_version == 2023:
        ifc_config = ifc_get_third_party_export_config_by_model_2023(
            ifc_version=ifc_version, ifc_settings=ifc_settings
        )
    else:
        # this is a non supported revit version!
        raise ValueError(
            "Revit version "
            + revit_version
            + " is currently not supported by IFC exporter!"
        )
    return ifc_config


def ifc_get_third_party_export_config_by_view(doc, ifc_version, ifc_settings=None):
    """
    Returns the 3rd party ifc config for export by view depending on revit version.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param ifc_version: The ifc version used for the export.
    :type ifc_version: Autodesk.Revit.DB.IFCVersion
    :raises ValueError: Raises an exception if the revit version in use is not supported by this script.
    :return: An ifc export config instance based on the Revit version.
    :rtype: BIM.IFC.Export.UI.IFCExportConfiguration
    """

    # get the revit version:
    revit_version = get_revit_version_number(doc=doc)
    ifc_config = None
    if revit_version == 2019:
        ifc_config = ifc_get_third_party_export_config_by_view_2019(
            ifc_version, ifc_settings
        )
    elif revit_version == 2020:
        ifc_config = ifc_get_third_party_export_config_by_view_2020(
            ifc_version, ifc_settings
        )
    elif revit_version == 2021:
        ifc_config = ifc_get_third_party_export_config_by_view_2021(
            ifc_version, ifc_settings
        )
    elif revit_version == 2022:
        ifc_config = ifc_get_third_party_export_config_by_view_2022(
            ifc_version, ifc_settings
        )
    elif revit_version == 2023:
        ifc_config = ifc_get_third_party_export_config_by_view_2023(
            ifc_version=ifc_version, ifc_settings=ifc_settings
        )
    else:
        # this is a non supported revit version!
        raise ValueError(
            "Revit version "
            + revit_version
            + " is currently not supported by IFC exporter!"
        )
    return ifc_config
