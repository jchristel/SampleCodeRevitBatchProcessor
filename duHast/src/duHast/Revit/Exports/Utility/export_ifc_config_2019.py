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

# -------------------------------------------- IFC EXPORT Revit 2019 -------------------------------------


def ifc_get_third_party_export_config_by_view_2019(ifc_version, ifc_settings):
    """
    Function returning an IFC export configuration for Revit 2019 using the open source third party IFC exporter plug in supported by AutoDesk

    This configuration allows export by view. If ifc_version is None, IFCVersion.Default will be used.

    :param ifc_version: The ifc version used for the export.
    :type ifc_version: Autodesk.Revit.DB.IFCVersion
    :return: An IFCExportConfig object.
    :rtype: BIM.IFC.Export.UI.IFCExportConfiguration
    """

    # load version specific assemblies
    ifc_third_party_folder_path_ = r"C:\ProgramData\Autodesk\ApplicationPlugins\IFC 2019.bundle\Contents\2019\IFCExportUIOverride.dll"
    clr.AddReferenceToFileAndPath(ifc_third_party_folder_path_)
    # import the BIM namespace which includes
    # IFCExportConfiguration and IFCExportConfigurationMaps classes
    from BIM.IFC.Export.UI import IFCExportConfiguration

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
def ifc_get_third_party_export_config_by_model_2019(ifc_version, ifc_settings):
    """
    Function returning an IFC export configuration for Revit 2019 using the open source third party IFC exporter plug in supported by AutoDesk

    This configuration allows export the entire model. If ifc_version is None, IFCVersion.Default will be used.

    :param ifc_version: The ifc version used for the export.
    :type ifc_version: Autodesk.Revit.DB.IFCVersion
    :return: An IFCExportConfig object.
    :rtype: BIM.IFC.Export.UI.IFCExportConfiguration
    """

    # load version specific assemblies
    ifc_third_party_folder_path_ = r"C:\ProgramData\Autodesk\ApplicationPlugins\IFC 2019.bundle\Contents\2019\IFCExportUIOverride.dll"
    clr.AddReferenceToFileAndPath(ifc_third_party_folder_path_)
    # import the BIM namespace which includes
    # IFCExportConfiguration and IFCExportConfigurationMaps classes
    from BIM.IFC.Export.UI import IFCExportConfiguration

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
