"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions to get the IFCExportConfig in varies versions of Revit.
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

import clr
import System
import sys

import Autodesk.Revit.DB as rdb


# -------------------------------------------- IFC EXPORT Revit 2022 -------------------------------------
# need to check for new features in revit 2022


# ifcVersion        which ifc version (2x3 etc...)
def ifc_get_third_party_export_config_by_view_2022(ifc_version, ifc_settings):
    """
    Function returning an IFC export configuration for Revit 2022 using the open source third party IFC exporter plug in supported by AutoDesk

    This configuration allows export by view. If ifc_version is None, IFCVersion.Default will be used.

    :param ifc_version: The ifc version used for the export.
    :type ifc_version: Autodesk.Revit.DB.IFCVersion
    :return: An IFCExportConfig object.
    :rtype: BIM.IFC.Export.UI.IFCExportConfiguration
    """

    # load version specific assemblies
    ifc_third_party_folder_path_ = r"C:\ProgramData\Autodesk\ApplicationPlugins\IFC 2022.bundle\Contents\2022\IFCExporterUIOverride.dll"

    clr.AddReferenceToFileAndPath(ifc_third_party_folder_path_)

    # import the BIM namespace which includes
    # IFCExportConfiguration and IFCExportConfigurationMaps classes
    from BIM.IFC.Export.UI import IFCExportConfiguration

    # set up configuration
    ifc_export_config = IFCExportConfiguration.CreateDefaultConfiguration()

    if ifc_settings == None:
        ifc_export_config = _setup_config_default_values_2022(
            ifc_export_config, ifc_version, True
        )
    else:
        ifc_export_config = _setup_config_from_settings_2022(
            ifc_export_config, ifc_settings
        )

    return ifc_export_config


# ifcVersion        which ifc version (2x3 etc...)
def ifc_get_third_party_export_config_by_model_2022(ifc_version, ifc_settings):
    """
    Function returning an IFC export configuration for Revit 2022 using the open source third party IFC exporter plug in supported by AutoDesk

    This configuration allows export the entire model. If ifc_version is None, IFCVersion.Default will be used.

    :param ifc_version: The ifc version used for the export.
    :type ifc_version: Autodesk.Revit.DB.IFCVersion
    :return: An IFCExportConfig object.
    :rtype: BIM.IFC.Export.UI.IFCExportConfiguration
    """

    # load version specific assemblies
    ifc_third_party_folder_path_ = r"C:\ProgramData\Autodesk\ApplicationPlugins\IFC 2022.bundle\Contents\2022\IFCExporterUIOverride.dll"
    ifc_third_party_folder_path_enums_ = r"C:\ProgramData\Autodesk\ApplicationPlugins\IFC 2022.bundle\Contents\2022\Revit.IFC.Common.dll"
    clr.AddReferenceToFileAndPath(ifc_third_party_folder_path_)
    clr.AddReferenceToFileAndPath(ifc_third_party_folder_path_enums_)

    # import the BIM namespace which includes
    # IFCExportConfiguration and IFCExportConfigurationMaps classes
    from BIM.IFC.Export.UI import IFCExportConfiguration
    from Revit.IFC.Common.Enums import SiteTransformBasis

    # set up configuration
    ifc_export_config = IFCExportConfiguration.CreateDefaultConfiguration()
    if ifc_settings == None:
        ifc_export_config = _setup_config_default_values_2022(
            ifc_export_config, ifc_version, False
        )
    else:
        ifc_export_config = _setup_config_from_settings_2022(
            ifc_export_config, ifc_settings
        )

    return ifc_export_config


def _setup_config_from_settings_2022(ifc_export_config, ifc_settings):
    """
    Sets up an ifc config object for Revit 2022 based on settings passt in.

    :param ifc_export_config: An ifc export config object
    :type ifc_export_config: BIM.IFC.Export.UI.IFCExportConfiguration
    :param ifc_settings: The settings to be applied to the ifc export config
    :type ifc_settings: :class:`.IFCSettings`

    :return: An ifc export config
    :rtype: BIM.IFC.Export.UI.IFCExportConfiguration
    """

    ifc_third_party_folder_path_enums_ = r"C:\ProgramData\Autodesk\ApplicationPlugins\IFC 2022.bundle\Contents\2022\Revit.IFC.Common.dll"
    clr.AddReferenceToFileAndPath(ifc_third_party_folder_path_enums_)
    from Revit.IFC.Common.Enums import SiteTransformBasis

    ifc_export_config.Name = ifc_settings.name
    # set up IFC version
    if ifc_settings.ifc_version == "IFCBCA":
        ifc_export_config.IFCVersion = rdb.IFCVersion.IFCBCA
    elif ifc_settings.ifc_version == "IFC2x2":
        ifc_export_config.IFCVersion = rdb.IFCVersion.IFC2x2
    elif ifc_settings.ifc_version == "IFC2x3":
        ifc_export_config.IFCVersion = rdb.IFCVersion.IFC2x3
    elif ifc_settings.ifc_version == "IFCCOBIE":
        ifc_export_config.IFCVersion = rdb.IFCVersion.IFCCOBIE
    elif ifc_settings.ifc_version == "IFC2x3CV2":
        ifc_export_config.IFCVersion = rdb.IFCVersion.IFC2x3CV2
    elif ifc_settings.ifc_version == "IFC4":
        ifc_export_config.IFCVersion = rdb.IFCVersion.IFC4
    elif ifc_settings.ifc_version == "IFC2x3FM":
        ifc_export_config.IFCVersion = rdb.IFCVersion.IFC2x3FM
    elif ifc_settings.ifc_version == "IFC4RV":
        ifc_export_config.IFCVersion = rdb.IFCVersion.IFC4RV
    elif ifc_settings.ifc_version == "IFC4DTV":
        ifc_export_config.IFCVersion = rdb.IFCVersion.IFC4DTV
    elif ifc_settings.ifc_version == "IFC2x3BFM":
        ifc_export_config.IFCVersion = rdb.IFCVersion.IFC2x3BFM
    else:
        ifc_export_config.IFCVersion = rdb.IFCVersion.Default

    ifc_export_config.SpaceBoundaries = ifc_settings.space_boundaries
    ifc_export_config.ActivePhaseId = ifc_settings.active_phase_id
    ifc_export_config.ActiveViewId = ifc_settings.active_view_id
    ifc_export_config.ExportBaseQuantities = ifc_settings.export_base_quantities
    ifc_export_config.SplitWallsAndColumns = ifc_settings.split_walls_and_columns
    ifc_export_config.VisibleElementsOfCurrentView = (
        ifc_settings.visible_elements_of_current_view
    )
    ifc_export_config.Use2DRoomBoundaryForVolume = (
        ifc_settings.use2_d_room_boundary_for_volume
    )
    ifc_export_config.UseFamilyAndTypeNameForReference = (
        ifc_settings.use_family_and_type_name_for_reference
    )
    ifc_export_config.ExportInternalRevitPropertySets = (
        ifc_settings.export_internal_revit_property_sets
    )
    ifc_export_config.ExportIFCCommonPropertySets = (
        ifc_settings.export_ifc_common_property_sets
    )
    ifc_export_config.Export2DElements = ifc_settings.export_2d_elements
    ifc_export_config.ExportPartsAsBuildingElements = (
        ifc_settings.export_parts_as_building_elements
    )
    ifc_export_config.ExportBoundingBox = ifc_settings.export_bounding_box
    ifc_export_config.ExportSolidModelRep = ifc_settings.export_solid_model_rep
    ifc_export_config.ExportSchedulesAsPsets = ifc_settings.export_schedules_as_psets
    ifc_export_config.ExportUserDefinedPsets = ifc_settings.export_user_defined_psets
    ifc_export_config.ExportUserDefinedPsetsFileName = (
        ifc_settings.export_user_defined_psets_file_name
    )
    ifc_export_config.ExportLinkedFiles = ifc_settings.export_linked_files
    ifc_export_config.IncludeSiteElevation = ifc_settings.include_site_elevation
    ifc_export_config.UseActiveViewGeometry = ifc_settings.use_active_view_geometry
    ifc_export_config.ExportSpecificSchedules = ifc_settings.export_specific_schedules
    ifc_export_config.TessellationLevelOfDetail = (
        ifc_settings.tessellation_level_of_detail
    )
    ifc_export_config.StoreIFCGUID = ifc_settings.store_ifc_guid
    ifc_export_config.ExportRoomsInView = ifc_settings.export_rooms_in_view
    ifc_export_config.UseOnlyTriangulation = ifc_settings.use_only_triangulation
    ifc_export_config.IncludeSteelElements = ifc_settings.include_steel_elements
    ifc_export_config.COBieCompanyInfo = ifc_settings.cobie_company_info
    ifc_export_config.COBieProjectInfo = ifc_settings.cobie_project_info
    ifc_export_config.UseTypeNameOnlyForIfcType = (
        ifc_settings.use_type_name_only_for_ifc_type
    )
    ifc_export_config.UseVisibleRevitNameAsEntityName = (
        ifc_settings.use_visible_revit_name_as_entity_name
    )

    # set up site placement
    if ifc_settings.site_placement == "shared":
        ifc_export_config.SitePlacement = SiteTransformBasis.Shared
    elif ifc_settings.site_placement == "site":
        ifc_export_config.SitePlacement = SiteTransformBasis.Site
    elif ifc_settings.site_placement == "project":
        ifc_export_config.SitePlacement = SiteTransformBasis.Project
    elif ifc_settings.site_placement == "internal":
        ifc_export_config.SitePlacement = SiteTransformBasis.Internal
    elif ifc_settings.site_placement == "projectInTN":
        ifc_export_config.SitePlacement = SiteTransformBasis.ProjectInTN
    else:
        ifc_export_config.SitePlacement = SiteTransformBasis.InternalInTN

    ifc_export_config.GeoRefCRSName = ifc_settings.geo_ref_crs_name
    ifc_export_config.GeoRefCRSDesc = ifc_settings.geo_ref_crs_desc
    ifc_export_config.GeoRefEPSGCode = ifc_settings.geo_ref_epsg_code
    ifc_export_config.GeoRefGeodeticDatum = ifc_settings.geo_ref_geodetic_datum
    ifc_export_config.GeoRefMapUnit = ifc_settings.geo_ref_map_unit
    ifc_export_config.ExcludeFilter = ifc_settings.exclude_filter

    return ifc_export_config


def _setup_config_default_values_2022(ifc_export_config, ifc_version, export_by_view):
    """
    Sets up an default ifc config object for Revit 2022.

    :param ifc_export_config: An ifc export config
    :type ifc_export_config: BIM.IFC.Export.UI.IFCExportConfiguration
    :param ifc_version: The Ifc version to be used for the export.
    :type ifc_version:  Autodesk.Revit.DB.IFCVersion
    :param export_by_view: True export by view, False export by model.
    :type export_by_view: bool

    :return: An ifc export config
    :rtype: BIM.IFC.Export.UI.IFCExportConfiguration
    """

    ifc_export_config.Name = "DefaultIFCByModelSetup"

    # set up IFC version
    if ifc_version is None or ifc_version == "":
        ifc_export_config.IFCVersion = rdb.IFCVersion.Default
    else:
        ifc_export_config.IFCVersion = ifc_version

    ifc_export_config.SpaceBoundaries = 1
    ifc_export_config.ActivePhaseId = rdb.ElementId.InvalidElementId.IntegerValue
    ifc_export_config.ExportBaseQuantities = True
    ifc_export_config.SplitWallsAndColumns = True
    ifc_export_config.VisibleElementsOfCurrentView = export_by_view  # by model
    ifc_export_config.Use2DRoomBoundaryForVolume = False
    ifc_export_config.UseFamilyAndTypeNameForReference = True
    ifc_export_config.ExportInternalRevitPropertySets = True
    ifc_export_config.ExportIFCCommonPropertySets = True
    ifc_export_config.Export2DElements = False
    ifc_export_config.ExportPartsAsBuildingElements = True
    ifc_export_config.ExportBoundingBox = False
    ifc_export_config.ExportSolidModelRep = False
    ifc_export_config.ExportSchedulesAsPsets = False
    ifc_export_config.ExportUserDefinedPsets = False
    ifc_export_config.ExportUserDefinedPsetsFileName = ""
    ifc_export_config.ExportLinkedFiles = False
    ifc_export_config.IncludeSiteElevation = True
    ifc_export_config.UseActiveViewGeometry = False  # by model
    ifc_export_config.ExportSpecificSchedules = False
    ifc_export_config.TessellationLevelOfDetail = 0
    ifc_export_config.StoreIFCGUID = True
    ifc_export_config.ExportRoomsInView = (
        export_by_view  # might not work in 3D views if volumes are not computed???
    )
    ifc_export_config.UseOnlyTriangulation = False
    ifc_export_config.IncludeSteelElements = True
    ifc_export_config.COBieCompanyInfo = "Company Name"
    ifc_export_config.COBieProjectInfo = "Project Info"
    return ifc_export_config
