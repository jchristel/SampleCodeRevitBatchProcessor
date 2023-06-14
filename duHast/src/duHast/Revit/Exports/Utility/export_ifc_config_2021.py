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
# Copyright (c) 2022  Jan Christel
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

import clr
import System
import sys

import Autodesk.Revit.DB as rdb

# -------------------------------------------- IFC EXPORT Revit 2021 -------------------------------------
# need to check for new features in revit 2021


# ifcVersion        which ifc version (2x3 etc...)
def ifc_get_third_party_export_config_by_view_2021(ifc_version, ifc_settings):
    """
    Function returning an IFC export configuration for Revit 2021 using the open source third party IFC exporter plug in supported by AutoDesk

    This configuration allows export by view. If ifc_version is None, IFCVersion.Default will be used.

    :param ifc_version: The ifc version used for the export.
    :type ifc_version: Autodesk.Revit.DB.IFCVersion
    :return: An IFCExportConfig object.
    :rtype: BIM.IFC.Export.UI.IFCExportConfiguration
    """

    # load version specific assemblies
    ifc_third_party_folder_path_ = r"C:\ProgramData\Autodesk\ApplicationPlugins\IFC 2021.bundle\Contents\2021\IFCExportUIOverride.dll"
    clr.AddReferenceToFileAndPath(ifc_third_party_folder_path_)
    # import the BIM namespace which includes
    # IFCExportConfiguration and IFCExportConfigurationMaps classes
    from BIM.IFC.Export.UI import IFCExportConfiguration

    # set up configuration
    ifc_export_config = IFCExportConfiguration.CreateDefaultConfiguration()
    ifc_export_config.Name = "DefaultIFCByViewSetup"
    # set up IFC version
    if ifc_version is None or ifc_version == "":
        ifc_export_config.IFCVersion = rdb.IFCVersion.Default
    else:
        ifc_export_config.IFCVersion = ifc_version

    ifc_export_config.SpaceBoundaries = 1
    ifc_export_config.ActivePhaseId = rdb.ElementId.InvalidElementId
    ifc_export_config.ExportBaseQuantities = True
    ifc_export_config.SplitWallsAndColumns = True
    ifc_export_config.VisibleElementsOfCurrentView = True  # by view
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
    ifc_export_config.UseActiveViewGeometry = False  # setting this value to True will slow down the IFC export considerably (sample: from 8min to 45min!)
    ifc_export_config.ExportSpecificSchedules = False
    ifc_export_config.TessellationLevelOfDetail = 0
    ifc_export_config.StoreIFCGUID = True
    ifc_export_config.ExportRoomsInView = (
        False  # might not work in 3D views if volumes are not computed???
    )
    # revit 2019.1
    ifc_export_config.UseOnlyTriangulation = False
    ifc_export_config.IncludeSteelElements = True
    ifc_export_config.COBieCompanyInfo = "Company Name"
    ifc_export_config.COBieProjectInfo = "Project Info"

    return ifc_export_config


# ifcVersion        which ifc version (2x3 etc...)
def ifc_get_third_party_export_config_by_model_2021(ifc_version, ifc_settings):
    """
    Function returning an IFC export configuration for Revit 2021 using the open source third party IFC exporter plug in supported by AutoDesk

    This configuration allows export the entire model. If ifc_version is None, IFCVersion.Default will be used.

    :param ifc_version: The ifc version used for the export.
    :type ifc_version: Autodesk.Revit.DB.IFCVersion
    :return: An IFCExportConfig object.
    :rtype: BIM.IFC.Export.UI.IFCExportConfiguration
    """

    # load version specific assemblies
    ifc_third_party_folder_path_ = r"C:\ProgramData\Autodesk\ApplicationPlugins\IFC 2021.bundle\Contents\2021\IFCExportUIOverride.dll"
    clr.AddReferenceToFileAndPath(ifc_third_party_folder_path_)
    # import the BIM namespace which includes
    # IFCExportConfiguration and IFCExportConfigurationMaps classes
    from BIM.IFC.Export.UI import IFCExportConfiguration

    # set up configuration
    ifc_export_config = IFCExportConfiguration.CreateDefaultConfiguration()
    ifc_export_config.Name = "DefaultIFCByModelSetup"

    # set up IFC version
    if ifc_version is None or ifc_version == "":
        ifc_export_config.IFCVersion = rdb.IFCVersion.Default
    else:
        ifc_export_config.IFCVersion = ifc_version

    ifc_export_config.SpaceBoundaries = 1
    ifc_export_config.ActivePhaseId = rdb.ElementId.InvalidElementId
    ifc_export_config.ExportBaseQuantities = True
    ifc_export_config.SplitWallsAndColumns = True
    ifc_export_config.VisibleElementsOfCurrentView = False  # by model
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
        False  # might not work in 3D views if volumes are not computed???
    )
    # revit 2019.1
    ifc_export_config.UseOnlyTriangulation = False
    ifc_export_config.IncludeSteelElements = True
    ifc_export_config.COBieCompanyInfo = "Company Name"
    ifc_export_config.COBieProjectInfo = "Project Info"

    return ifc_export_config
