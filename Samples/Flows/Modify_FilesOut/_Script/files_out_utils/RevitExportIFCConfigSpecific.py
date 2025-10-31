"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a custom helper functions to get the IFCExportConfig for Revit 2022.
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

import Autodesk.Revit.DB as rdb
from duHast.Revit.Exports.export_ifc import ifc_get_third_party_export_config_by_view
from duHast.Revit.Exports.Utility.ifc_export_settings import IFCSettings


# -------------------------------------------- IFC EXPORT Revit 2022 -------------------------------------
# need to check for new features in revit 2022


def ifc_get_third_party_export_config_by_view_2022(doc):
    """
    Function returning an IFC export configuration for Revit 2022 using the open source third party IFC exporter plug in supported by AutoDesk

    This configuration allows custom setup export by view.

    :param doc: The current model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: An IFCExportconfig object.
    :rtype: BIM.IFC.Export.UI.IFCExportConfiguration
    """

    name = "BVN New Bundaberg Hospital"
    ifcVersion = "IFC4DTV"
    spaceBoundaries = 1
    activePhaseId = -1
    activeViewId = -1
    exportBaseQuantities = True  # as per BIM exec plan
    splitWallsAndColumns = True  # as per BIM exec plan
    visibleElementsOfCurrentView = True  # by view
    use2DRoomBoundaryForVolume = True  # test if required if no volumes are computed?
    useFamilyAndTypeNameForReference = False  # as per BIM exec plan
    exportInternalRevitPropertySets = True  # as per BIM exec plan
    exportIFCCommonPropertySets = True  # as per BIM exec plan
    export2DElements = True  # as per BIM exec plan
    exportPartsAsBuildingElements = True
    exportBoundingBox = False  # as per BIM exec plan
    exportSolidModelRep = False  # as per BIM exec plan
    exportSchedulesAsPsets = False  # as per BIM exec plan
    exportUserDefinedPsets = False  # as per BIM exec plan
    exportUserDefinedPsetsFileName = ""  # as per BIM exec plan
    exportLinkedFiles = False  # as per BIM exec plan
    includeSiteElevation = True  # not defined in BIM exec plan
    useActiveViewGeometry = False  # setting this value to True will slow down the IFC export considerably (sample: from 8min to 45min!)
    exportSpecificSchedules = False  # as per BIM exec plan
    tessellationLevelOfDetail = 0
    storeIFCGUID = True  # as per BIM exec plan
    exportRoomsInView = (
        True  # might not work in 3D views if volumes are not computed???
    )
    useOnlyTriangulation = False  # as per BIM exec plan
    includeSteelElements = True  # not defined in BIM exec
    cOBieCompanyInfo = "BVN"
    cOBieProjectInfo = "New Bundaberg Hospital"
    useTypeNameOnlyForIfcType = True
    useVisibleRevitNameAsEntityName = True
    sitePlacement = "SiteTransformBasis.Shared"
    selectedSite = "sample site"
    geoRefCRSName = "geoRefCRSName"
    geoRefCRSDesc = "geoRefCRSDesc"
    geoRefEPSGCode = "geoRefEPSGCode"
    geoRefGeodeticDatum = "geoRefGeodeticDatum"
    geoRefMapUnit = "geoRefMapUnit"
    excludeFilter = ""

    # set up settings class
    ifcSettingsTest = IFCSettings(
        name,
        ifcVersion,
        spaceBoundaries,
        activePhaseId,
        activeViewId,
        exportBaseQuantities,
        splitWallsAndColumns,
        visibleElementsOfCurrentView,
        use2DRoomBoundaryForVolume,
        useFamilyAndTypeNameForReference,
        exportInternalRevitPropertySets,
        exportIFCCommonPropertySets,
        export2DElements,
        exportPartsAsBuildingElements,
        exportBoundingBox,
        exportSolidModelRep,
        exportSchedulesAsPsets,
        exportUserDefinedPsets,
        exportUserDefinedPsetsFileName,
        exportLinkedFiles,
        includeSiteElevation,
        useActiveViewGeometry,
        exportSpecificSchedules,
        tessellationLevelOfDetail,
        storeIFCGUID,
        exportRoomsInView,
        useOnlyTriangulation,
        includeSteelElements,
        cOBieCompanyInfo,
        cOBieProjectInfo,
        useTypeNameOnlyForIfcType,
        useVisibleRevitNameAsEntityName,
        sitePlacement,
        selectedSite,
        geoRefCRSName,
        geoRefCRSDesc,
        geoRefEPSGCode,
        geoRefGeodeticDatum,
        geoRefMapUnit,
        excludeFilter,
    )

    ifcExportConfig = ifc_get_third_party_export_config_by_view(doc, None, ifcSettingsTest)

    return ifcExportConfig


# ifcVersion        which ifc version (2x3 etc...)
def ifc_get_third_party_export_config_by_model_2022(ifc_version):
    """
    Function returning an IFC export configuration for Revit 2022 using the open source third party IFC exporter plug in supported by AutoDesk

    This configuration allows export the entire model. If ifcversion is None, IFCVersion.Default will be used.

    :param ifc_version: The ifc version used for the export.
    :type ifc_version: Autodesk.Revit.DB.IFCVersion
    :return: An IFCExportconfig object.
    :rtype: BIM.IFC.Export.UI.IFCExportConfiguration
    """

    # load version specific assemblies
    ifcThirdPartyFolderPath_ = r"C:\ProgramData\Autodesk\ApplicationPlugins\IFC 2022.bundle\Contents\2022\IFCExporterUIOverride.dll"
    clr.AddReferenceToFileAndPath(ifcThirdPartyFolderPath_)
    # import the BIM namespace which includes
    # IFCExportConfiguration and IFCExportConfigurationMaps classes
    from BIM.IFC.Export.UI import IFCExportConfiguration

    # set up configuration
    ifcExportConfig = IFCExportConfiguration.CreateDefaultConfiguration()
    ifcExportConfig.Name = "DefaultIFCByModelSetup"

    # set up IFC version
    if ifc_version is None or ifc_version == "":
        ifcExportConfig.IFCVersion = rdb.IFCVersion.Default
    else:
        ifcExportConfig.IFCVersion = ifc_version

    ifcExportConfig.SpaceBoundaries = (
        1  # double check this value...built wants that to be None
    )
    ifcExportConfig.ActivePhaseId = rdb.ElementId.InvalidElementId.IntegerValue
    ifcExportConfig.ExportBaseQuantities = True  # as per BIM exec plan
    ifcExportConfig.SplitWallsAndColumns = False  # as per BIM exec plan
    ifcExportConfig.VisibleElementsOfCurrentView = False  # export entire model
    ifcExportConfig.Use2DRoomBoundaryForVolume = (
        True  # test if required if no volumes are computed
    )
    ifcExportConfig.UseFamilyAndTypeNameForReference = False  # as per BI exec plan
    ifcExportConfig.ExportInternalRevitPropertySets = True  # as per BIM exec plan
    ifcExportConfig.ExportIFCCommonPropertySets = True  # as per BIM exec plan
    ifcExportConfig.Export2DElements = True  # as per BIM exec plan
    ifcExportConfig.ExportPartsAsBuildingElements = False  # as per BIM exec plan
    ifcExportConfig.ExportBoundingBox = False  # as per BIM exec plan
    ifcExportConfig.ExportSolidModelRep = False  # as per BIM exec plan
    ifcExportConfig.ExportSchedulesAsPsets = False  # as per BIM exec plan
    ifcExportConfig.ExportUserDefinedPsets = False  # as per BIM exec plan
    ifcExportConfig.ExportUserDefinedPsetsFileName = ""  # as per BIM exec plan
    ifcExportConfig.ExportLinkedFiles = False  # as per BIM exec plan
    ifcExportConfig.IncludeSiteElevation = True  # not defined in BIM exec plan
    ifcExportConfig.UseActiveViewGeometry = False  # setting this value to True will slow down the IFC epxort considerably (sample: from 8min to 45min!)
    ifcExportConfig.ExportSpecificSchedules = False  # as per BIM exec plan
    ifcExportConfig.TessellationLevelOfDetail = 0
    ifcExportConfig.StoreIFCGUID = True  # as per BIM exec plan
    ifcExportConfig.ExportRoomsInView = (
        True  # might not work in 3D views if volumnes are not computated???
    )
    # revit 2019.1
    ifcExportConfig.UseOnlyTriangulation = False  # as per BIM exec plan
    ifcExportConfig.IncludeSteelElements = True  # not defined in BIM exec
    ifcExportConfig.COBieCompanyInfo = "Your Company"
    ifcExportConfig.COBieProjectInfo = "Your Project Name"

    return ifcExportConfig
