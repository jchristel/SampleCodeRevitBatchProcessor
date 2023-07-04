'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions to get the IFCExportConfig in varies versions of Revit.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

#
#License:
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

import Autodesk.Revit.DB as rdb
from duHast.APISamples import RevitExport as rex
from duHast.APISamples.RevitExportIFCSettings import IFCSettings


#-------------------------------------------- IFC EXPORT Revit 2022 -------------------------------------
# need to check for new features in revit 2022

def ifc_get_third_party_export_config_by_view_2022(doc):
    '''
    Function returning an IFC export configuration for Revit 2022 using the open source third party IFC exporter plug in supported by AutoDesk
    
    This configuration allows custom setup export by view.

    :param doc: The current model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: An IFCExportconfig object.
    :rtype: BIM.IFC.Export.UI.IFCExportConfiguration
    '''

    name  = 'BVN New Bundaberg Hospital'
    ifcVersion  = 'IFC4DTV'
    spaceBoundaries = 1
    activePhaseId = -1
    activeViewId = -1
    exportBaseQuantities = True # as per BIM exec plan
    splitWallsAndColumns = True # as per BIM exec plan
    visibleElementsOfCurrentView = True # by view
    use2DRoomBoundaryForVolume = True # test if required if no volumes are computed?
    useFamilyAndTypeNameForReference = False # as per BIM exec plan
    exportInternalRevitPropertySets = True # as per BIM exec plan
    exportIFCCommonPropertySets = True # as per BIM exec plan
    export2DElements = True # as per BIM exec plan
    exportPartsAsBuildingElements = True
    exportBoundingBox = False # as per BIM exec plan
    exportSolidModelRep = False # as per BIM exec plan
    exportSchedulesAsPsets = False # as per BIM exec plan
    exportUserDefinedPsets = False # as per BIM exec plan
    exportUserDefinedPsetsFileName = '' # as per BIM exec plan
    exportLinkedFiles = False # as per BIM exec plan
    includeSiteElevation = True  # not defined in BIM exec plan
    useActiveViewGeometry = False # setting this value to True will slow down the IFC export considerably (sample: from 8min to 45min!)
    exportSpecificSchedules = False # as per BIM exec plan
    tessellationLevelOfDetail = 0
    storeIFCGUID = True # as per BIM exec plan
    exportRoomsInView = True # might not work in 3D views if volumes are not computed???
    useOnlyTriangulation = False # as per BIM exec plan
    includeSteelElements = True # not defined in BIM exec
    cOBieCompanyInfo = 'BVN'
    cOBieProjectInfo = 'New Bundaberg Hospital'
    useTypeNameOnlyForIfcType = True
    useVisibleRevitNameAsEntityName = True
    sitePlacement = 'SiteTransformBasis.Shared'
    selectedSite = 'sample site'
    geoRefCRSName = 'geoRefCRSName'
    geoRefCRSDesc ='geoRefCRSDesc'
    geoRefEPSGCode ='geoRefEPSGCode'
    geoRefGeodeticDatum ='geoRefGeodeticDatum'
    geoRefMapUnit ='geoRefMapUnit'
    excludeFilter = ''
    
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
        excludeFilter
    )

    ifcExportConfig = rex.IFCGetThirdPartyExportConfigByView(doc, None, ifcSettingsTest)

    return ifcExportConfig

# ifcVersion        which ifc version (2x3 etc...)
def ifc_get_third_party_export_config_by_model_2022(ifc_version):
    '''
    Function returning an IFC export configuration for Revit 2022 using the open source third party IFC exporter plug in supported by AutoDesk
    
    This configuration allows export the entire model. If ifcversion is None, IFCVersion.Default will be used.

    :param ifc_version: The ifc version used for the export.
    :type ifc_version: Autodesk.Revit.DB.IFCVersion
    :return: An IFCExportconfig object.
    :rtype: BIM.IFC.Export.UI.IFCExportConfiguration
    '''

    # load version specific assemblies
    ifcThirdPartyFolderPath_ = r'C:\ProgramData\Autodesk\ApplicationPlugins\IFC 2022.bundle\Contents\2022\IFCExporterUIOverride.dll'
    clr.AddReferenceToFileAndPath(ifcThirdPartyFolderPath_)
    # import the BIM namespace which includes 
    # IFCExportConfiguration and IFCExportConfigurationMaps classes
    from BIM.IFC.Export.UI import IFCExportConfiguration

    # set up configuration
    ifcExportConfig = IFCExportConfiguration.CreateDefaultConfiguration()
    ifcExportConfig.Name = 'DefaultIFCByModelSetup'
    
    # set up IFC version
    if(ifc_version is None or ifc_version == ''):
        ifcExportConfig.IFCVersion = rdb.IFCVersion.Default
    else:  
        ifcExportConfig.IFCVersion = ifc_version

    ifcExportConfig.SpaceBoundaries = 1 # double check this value...built wants that to be None
    ifcExportConfig.ActivePhaseId = rdb.ElementId.InvalidElementId.IntegerValue
    ifcExportConfig.ExportBaseQuantities = True # as per BIM exec plan
    ifcExportConfig.SplitWallsAndColumns = False #as per BIM exec plan
    ifcExportConfig.VisibleElementsOfCurrentView = False # export entire model
    ifcExportConfig.Use2DRoomBoundaryForVolume = True # test if required if no volumes are computed
    ifcExportConfig.UseFamilyAndTypeNameForReference = False # as per BI exec plan
    ifcExportConfig.ExportInternalRevitPropertySets = True # as per BIM exec plan
    ifcExportConfig.ExportIFCCommonPropertySets = True # as per BIM exec plan
    ifcExportConfig.Export2DElements = True # as per BIM exec plan
    ifcExportConfig.ExportPartsAsBuildingElements = False # as per BIM exec plan
    ifcExportConfig.ExportBoundingBox = False # as per BIM exec plan
    ifcExportConfig.ExportSolidModelRep = False # as per BIM exec plan
    ifcExportConfig.ExportSchedulesAsPsets = False # as per BIM exec plan
    ifcExportConfig.ExportUserDefinedPsets = False # as per BIM exec plan
    ifcExportConfig.ExportUserDefinedPsetsFileName = '' # as per BIM exec plan
    ifcExportConfig.ExportLinkedFiles =  False # as per BIM exec plan
    ifcExportConfig.IncludeSiteElevation = True # not defined in BIM exec plan
    ifcExportConfig.UseActiveViewGeometry = False # setting this value to True will slow down the IFC epxort considerably (sample: from 8min to 45min!)
    ifcExportConfig.ExportSpecificSchedules = False # as per BIM exec plan
    ifcExportConfig.TessellationLevelOfDetail = 0
    ifcExportConfig.StoreIFCGUID = True # as per BIM exec plan
    ifcExportConfig.ExportRoomsInView = True # might not work in 3D views if volumnes are not computated???
    # revit 2019.1
    ifcExportConfig.UseOnlyTriangulation = False # as per BIM exec plan
    ifcExportConfig.IncludeSteelElements = True # not defined in BIM exec
    ifcExportConfig.COBieCompanyInfo = 'BVN'
    ifcExportConfig.COBieProjectInfo = 'New Bundaberg Hospital'
    
    return ifcExportConfig