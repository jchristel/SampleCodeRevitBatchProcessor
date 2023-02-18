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
import System
import sys

import Autodesk.Revit.DB as rdb

#-------------------------------------------- IFC EXPORT Revit 2019 -------------------------------------

def IFCGetThirdPartyExportConfigByView2019(ifcVersion, ifcSettings):
    '''
    Function returning an IFC export configuration for Revit 2019 using the open source third party IFC exporter plug in supported by AutoDesk
    
    This configuration allows export by view. If ifcVersion is None, IFCVersion.Default will be used.

    :param ifcVersion: The ifc version used for the export.
    :type ifcVersion: Autodesk.Revit.DB.IFCVersion
    :return: An IFCExportConfig object.
    :rtype: BIM.IFC.Export.UI.IFCExportConfiguration
    '''

    # load version specific assemblies
    ifcThirdPartyFolderPath_ = r'C:\ProgramData\Autodesk\ApplicationPlugins\IFC 2019.bundle\Contents\2019\IFCExportUIOverride.dll'
    clr.AddReferenceToFileAndPath(ifcThirdPartyFolderPath_)
    # import the BIM namespace which includes 
    # IFCExportConfiguration and IFCExportConfigurationMaps classes
    from BIM.IFC.Export.UI import IFCExportConfiguration

    ifcExportConfig = IFCExportConfiguration.CreateDefaultConfiguration()
    ifcExportConfig.Name = 'DefaultIFCByViewSetup'
    # set up IFC version
    if(ifcVersion is None or ifcVersion == ''):
        ifcExportConfig.IFCVersion = rdb.IFCVersion.Default
    else:  
        ifcExportConfig.IFCVersion = ifcVersion

    ifcExportConfig.SpaceBoundaries = 1
    ifcExportConfig.ActivePhaseId = rdb.ElementId.InvalidElementId
    ifcExportConfig.ExportBaseQuantities = True
    ifcExportConfig.SplitWallsAndColumns = True
    ifcExportConfig.VisibleElementsOfCurrentView = True # by view
    ifcExportConfig.Use2DRoomBoundaryForVolume = False
    ifcExportConfig.UseFamilyAndTypeNameForReference = True
    ifcExportConfig.ExportInternalRevitPropertySets = True
    ifcExportConfig.ExportIFCCommonPropertySets = True
    ifcExportConfig.Export2DElements = False
    ifcExportConfig.ExportPartsAsBuildingElements = True
    ifcExportConfig.ExportBoundingBox = False
    ifcExportConfig.ExportSolidModelRep = False
    ifcExportConfig.ExportSchedulesAsPsets = False
    ifcExportConfig.ExportUserDefinedPsets = False
    ifcExportConfig.ExportUserDefinedPsetsFileName = ''
    ifcExportConfig.ExportLinkedFiles = False
    ifcExportConfig.IncludeSiteElevation = True
    ifcExportConfig.UseActiveViewGeometry = False # setting this value to True will slow down the IFC export considerably (sample: from 8min to 45min!)
    ifcExportConfig.ExportSpecificSchedules = False
    ifcExportConfig.TessellationLevelOfDetail = 0
    ifcExportConfig.StoreIFCGUID = True
    ifcExportConfig.ExportRoomsInView = False # might not work in 3D views if volumes are not computed???
    # revit 2019.1
    ifcExportConfig.UseOnlyTriangulation = False
    ifcExportConfig.IncludeSteelElements = True
    ifcExportConfig.COBieCompanyInfo = 'Company Name'
    ifcExportConfig.COBieProjectInfo = 'Project Info'
    
    return ifcExportConfig

# ifcVersion        which ifc version (2x3 etc...)
def IFCGetThirdPartyExportConfigByModel2019(ifcVersion, ifcSettings):
    '''
    Function returning an IFC export configuration for Revit 2019 using the open source third party IFC exporter plug in supported by AutoDesk
    
    This configuration allows export the entire model. If ifcVersion is None, IFCVersion.Default will be used.

    :param ifcVersion: The ifc version used for the export.
    :type ifcVersion: Autodesk.Revit.DB.IFCVersion
    :return: An IFCExportConfig object.
    :rtype: BIM.IFC.Export.UI.IFCExportConfiguration
    '''

    # load version specific assemblies
    ifcThirdPartyFolderPath_ = r'C:\ProgramData\Autodesk\ApplicationPlugins\IFC 2019.bundle\Contents\2019\IFCExportUIOverride.dll'
    clr.AddReferenceToFileAndPath(ifcThirdPartyFolderPath_)
    # import the BIM namespace which includes 
    # IFCExportConfiguration and IFCExportConfigurationMaps classes
    from BIM.IFC.Export.UI import IFCExportConfiguration

    ifcExportConfig = IFCExportConfiguration.CreateDefaultConfiguration()
    ifcExportConfig.Name = 'DefaultIFCByModelSetup'
    
    # set up IFC version
    if(ifcVersion is None or ifcVersion == ''):
        ifcExportConfig.IFCVersion = rdb.IFCVersion.Default
    else:  
        ifcExportConfig.IFCVersion = ifcVersion

    ifcExportConfig.SpaceBoundaries = 1
    ifcExportConfig.ActivePhaseId = rdb.ElementId.InvalidElementId
    ifcExportConfig.ExportBaseQuantities = True
    ifcExportConfig.SplitWallsAndColumns = True
    ifcExportConfig.VisibleElementsOfCurrentView = False # by model
    ifcExportConfig.Use2DRoomBoundaryForVolume = False
    ifcExportConfig.UseFamilyAndTypeNameForReference = True
    ifcExportConfig.ExportInternalRevitPropertySets = True
    ifcExportConfig.ExportIFCCommonPropertySets = True
    ifcExportConfig.Export2DElements = False
    ifcExportConfig.ExportPartsAsBuildingElements = True
    ifcExportConfig.ExportBoundingBox = False
    ifcExportConfig.ExportSolidModelRep = False
    ifcExportConfig.ExportSchedulesAsPsets = False
    ifcExportConfig.ExportUserDefinedPsets = False
    ifcExportConfig.ExportUserDefinedPsetsFileName = ''
    ifcExportConfig.ExportLinkedFiles = False
    ifcExportConfig.IncludeSiteElevation = True
    ifcExportConfig.UseActiveViewGeometry = False # by model
    ifcExportConfig.ExportSpecificSchedules = False
    ifcExportConfig.TessellationLevelOfDetail = 0
    ifcExportConfig.StoreIFCGUID = True
    ifcExportConfig.ExportRoomsInView = False # might not work in 3D views if volumes are not computed???
    # revit 2019.1
    ifcExportConfig.UseOnlyTriangulation = False
    ifcExportConfig.IncludeSteelElements = True
    ifcExportConfig.COBieCompanyInfo = 'Company Name'
    ifcExportConfig.COBieProjectInfo = 'Project Info'
    
    return ifcExportConfig

#-------------------------------------------- IFC EXPORT Revit 2020 -------------------------------------
# need to check for new features in revit 2020

def IFCGetThirdPartyExportConfigByView2020(ifcVersion, ifcSettings):
    '''
    Function returning an IFC export configuration for Revit 2020 using the open source third party IFC exporter plug in supported by AutoDesk
    
    This configuration allows export by view. If ifcVersion is None, IFCVersion.Default will be used.

    :param ifcVersion: The ifc version used for the export (2x3 etc...).
    :type ifcVersion: Autodesk.Revit.DB.IFCVersion
    :return: An IFCExportConfig object.
    :rtype: BIM.IFC.Export.UI.IFCExportConfiguration
    '''

    # load version specific assemblies
    ifcThirdPartyFolderPath_ = r'C:\ProgramData\Autodesk\ApplicationPlugins\IFC 2020.bundle\Contents\2020\IFCExportUIOverride.dll'
    clr.AddReferenceToFileAndPath(ifcThirdPartyFolderPath_)
    # import the BIM namespace which includes 
    # IFCExportConfiguration and IFCExportConfigurationMaps classes
    from BIM.IFC.Export.UI import IFCExportConfiguration

    # set up configuration
    ifcExportConfig = IFCExportConfiguration.CreateDefaultConfiguration()
    ifcExportConfig.Name = 'DefaultIFCByViewSetup'
    # set up IFC version
    if(ifcVersion is None or ifcVersion == ''):
        ifcExportConfig.IFCVersion = rdb.IFCVersion.Default
    else:  
        ifcExportConfig.IFCVersion = ifcVersion

    ifcExportConfig.SpaceBoundaries = 1
    ifcExportConfig.ActivePhaseId = rdb.ElementId.InvalidElementId
    ifcExportConfig.ExportBaseQuantities = True
    ifcExportConfig.SplitWallsAndColumns = True
    ifcExportConfig.VisibleElementsOfCurrentView = True # by view
    ifcExportConfig.Use2DRoomBoundaryForVolume = False
    ifcExportConfig.UseFamilyAndTypeNameForReference = True
    ifcExportConfig.ExportInternalRevitPropertySets = True
    ifcExportConfig.ExportIFCCommonPropertySets = True
    ifcExportConfig.Export2DElements = False
    ifcExportConfig.ExportPartsAsBuildingElements = True
    ifcExportConfig.ExportBoundingBox = False
    ifcExportConfig.ExportSolidModelRep = False
    ifcExportConfig.ExportSchedulesAsPsets = False
    ifcExportConfig.ExportUserDefinedPsets = False
    ifcExportConfig.ExportUserDefinedPsetsFileName = ''
    ifcExportConfig.ExportLinkedFiles = False
    ifcExportConfig.IncludeSiteElevation = True
    ifcExportConfig.UseActiveViewGeometry = False # setting this value to True will slow down the IFC export considerably (sample: from 8min to 45min!)
    ifcExportConfig.ExportSpecificSchedules = False
    ifcExportConfig.TessellationLevelOfDetail = 0
    ifcExportConfig.StoreIFCGUID = True
    ifcExportConfig.ExportRoomsInView = False # might not work in 3D views if volumes are not computed???
    # revit 2019.1
    ifcExportConfig.UseOnlyTriangulation = False
    ifcExportConfig.IncludeSteelElements = True
    ifcExportConfig.COBieCompanyInfo = 'Company Name'
    ifcExportConfig.COBieProjectInfo = 'Project Info'
    
    return ifcExportConfig

# ifcVersion        which ifc version (2x3 etc...)
def IFCGetThirdPartyExportConfigByModel2020(ifcVersion, ifcSettings):
    '''
    Function returning an IFC export configuration for Revit 2020 using the open source third party IFC exporter plug in supported by AutoDesk
    
    This configuration allows export the entire model. If ifcVersion is None, IFCVersion.Default will be used.

    :param ifcVersion: The ifc version used for the export.
    :type ifcVersion: Autodesk.Revit.DB.IFCVersion
    :return: An IFCExportConfig object.
    :rtype: BIM.IFC.Export.UI.IFCExportConfiguration
    '''

    # load version specific assemblies
    ifcThirdPartyFolderPath_ = r'C:\ProgramData\Autodesk\ApplicationPlugins\IFC 2020.bundle\Contents\2020\IFCExportUIOverride.dll'
    clr.AddReferenceToFileAndPath(ifcThirdPartyFolderPath_)
    # import the BIM namespace which includes 
    # IFCExportConfiguration and IFCExportConfigurationMaps classes
    from BIM.IFC.Export.UI import IFCExportConfiguration

    # set up configuration
    ifcExportConfig = IFCExportConfiguration.CreateDefaultConfiguration()
    ifcExportConfig.Name = 'DefaultIFCByModelSetup'
    
    # set up IFC version
    if(ifcVersion is None or ifcVersion == ''):
        ifcExportConfig.IFCVersion = rdb.IFCVersion.Default
    else:  
        ifcExportConfig.IFCVersion = ifcVersion

    ifcExportConfig.SpaceBoundaries = 1
    ifcExportConfig.ActivePhaseId = rdb.ElementId.InvalidElementId
    ifcExportConfig.ExportBaseQuantities = True
    ifcExportConfig.SplitWallsAndColumns = True
    ifcExportConfig.VisibleElementsOfCurrentView = False # by model
    ifcExportConfig.Use2DRoomBoundaryForVolume = False
    ifcExportConfig.UseFamilyAndTypeNameForReference = True
    ifcExportConfig.ExportInternalRevitPropertySets = True
    ifcExportConfig.ExportIFCCommonPropertySets = True
    ifcExportConfig.Export2DElements = False
    ifcExportConfig.ExportPartsAsBuildingElements = True
    ifcExportConfig.ExportBoundingBox = False
    ifcExportConfig.ExportSolidModelRep = False
    ifcExportConfig.ExportSchedulesAsPsets = False
    ifcExportConfig.ExportUserDefinedPsets = False
    ifcExportConfig.ExportUserDefinedPsetsFileName = ''
    ifcExportConfig.ExportLinkedFiles = False
    ifcExportConfig.IncludeSiteElevation = True
    ifcExportConfig.UseActiveViewGeometry = False # by model
    ifcExportConfig.ExportSpecificSchedules = False
    ifcExportConfig.TessellationLevelOfDetail = 0
    ifcExportConfig.StoreIFCGUID = True
    ifcExportConfig.ExportRoomsInView = False # might not work in 3D views if volumes are not computed???
    # revit 2019.1
    ifcExportConfig.UseOnlyTriangulation = False
    ifcExportConfig.IncludeSteelElements = True
    ifcExportConfig.COBieCompanyInfo = 'Company Name'
    ifcExportConfig.COBieProjectInfo = 'Project Info'
    
    return ifcExportConfig

#-------------------------------------------- IFC EXPORT Revit 2021 -------------------------------------
# need to check for new features in revit 2021

# ifcVersion        which ifc version (2x3 etc...)
def IFCGetThirdPartyExportConfigByView2021(ifcVersion, ifcSettings):
    '''
    Function returning an IFC export configuration for Revit 2021 using the open source third party IFC exporter plug in supported by AutoDesk
    
    This configuration allows export by view. If ifcVersion is None, IFCVersion.Default will be used.

    :param ifcVersion: The ifc version used for the export.
    :type ifcVersion: Autodesk.Revit.DB.IFCVersion
    :return: An IFCExportConfig object.
    :rtype: BIM.IFC.Export.UI.IFCExportConfiguration
    '''

    # load version specific assemblies
    ifcThirdPartyFolderPath_ = r'C:\ProgramData\Autodesk\ApplicationPlugins\IFC 2021.bundle\Contents\2021\IFCExportUIOverride.dll'
    clr.AddReferenceToFileAndPath(ifcThirdPartyFolderPath_)
    # import the BIM namespace which includes 
    # IFCExportConfiguration and IFCExportConfigurationMaps classes
    from BIM.IFC.Export.UI import IFCExportConfiguration

    # set up configuration
    ifcExportConfig = IFCExportConfiguration.CreateDefaultConfiguration()
    ifcExportConfig.Name = 'DefaultIFCByViewSetup'
    # set up IFC version
    if(ifcVersion is None or ifcVersion == ''):
        ifcExportConfig.IFCVersion = rdb.IFCVersion.Default
    else:  
        ifcExportConfig.IFCVersion = ifcVersion

    ifcExportConfig.SpaceBoundaries = 1
    ifcExportConfig.ActivePhaseId = rdb.ElementId.InvalidElementId
    ifcExportConfig.ExportBaseQuantities = True
    ifcExportConfig.SplitWallsAndColumns = True
    ifcExportConfig.VisibleElementsOfCurrentView = True # by view
    ifcExportConfig.Use2DRoomBoundaryForVolume = False
    ifcExportConfig.UseFamilyAndTypeNameForReference = True
    ifcExportConfig.ExportInternalRevitPropertySets = True
    ifcExportConfig.ExportIFCCommonPropertySets = True
    ifcExportConfig.Export2DElements = False
    ifcExportConfig.ExportPartsAsBuildingElements = True
    ifcExportConfig.ExportBoundingBox = False
    ifcExportConfig.ExportSolidModelRep = False
    ifcExportConfig.ExportSchedulesAsPsets = False
    ifcExportConfig.ExportUserDefinedPsets = False
    ifcExportConfig.ExportUserDefinedPsetsFileName = ''
    ifcExportConfig.ExportLinkedFiles = False
    ifcExportConfig.IncludeSiteElevation = True
    ifcExportConfig.UseActiveViewGeometry = False # setting this value to True will slow down the IFC export considerably (sample: from 8min to 45min!)
    ifcExportConfig.ExportSpecificSchedules = False
    ifcExportConfig.TessellationLevelOfDetail = 0
    ifcExportConfig.StoreIFCGUID = True
    ifcExportConfig.ExportRoomsInView = False # might not work in 3D views if volumes are not computed???
    # revit 2019.1
    ifcExportConfig.UseOnlyTriangulation = False
    ifcExportConfig.IncludeSteelElements = True
    ifcExportConfig.COBieCompanyInfo = 'Company Name'
    ifcExportConfig.COBieProjectInfo = 'Project Info'
    
    return ifcExportConfig

# ifcVersion        which ifc version (2x3 etc...)
def IFCGetThirdPartyExportConfigByModel2021(ifcVersion, ifcSettings):
    '''
    Function returning an IFC export configuration for Revit 2021 using the open source third party IFC exporter plug in supported by AutoDesk
    
    This configuration allows export the entire model. If ifcVersion is None, IFCVersion.Default will be used.

    :param ifcVersion: The ifc version used for the export.
    :type ifcVersion: Autodesk.Revit.DB.IFCVersion
    :return: An IFCExportConfig object.
    :rtype: BIM.IFC.Export.UI.IFCExportConfiguration
    '''

    # load version specific assemblies
    ifcThirdPartyFolderPath_ = r'C:\ProgramData\Autodesk\ApplicationPlugins\IFC 2021.bundle\Contents\2021\IFCExportUIOverride.dll'
    clr.AddReferenceToFileAndPath(ifcThirdPartyFolderPath_)
    # import the BIM namespace which includes 
    # IFCExportConfiguration and IFCExportConfigurationMaps classes
    from BIM.IFC.Export.UI import IFCExportConfiguration

    # set up configuration
    ifcExportConfig = IFCExportConfiguration.CreateDefaultConfiguration()
    ifcExportConfig.Name = 'DefaultIFCByModelSetup'
    
    # set up IFC version
    if(ifcVersion is None or ifcVersion == ''):
        ifcExportConfig.IFCVersion = rdb.IFCVersion.Default
    else:  
        ifcExportConfig.IFCVersion = ifcVersion

    ifcExportConfig.SpaceBoundaries = 1
    ifcExportConfig.ActivePhaseId = rdb.ElementId.InvalidElementId
    ifcExportConfig.ExportBaseQuantities = True
    ifcExportConfig.SplitWallsAndColumns = True
    ifcExportConfig.VisibleElementsOfCurrentView = False # by model
    ifcExportConfig.Use2DRoomBoundaryForVolume = False
    ifcExportConfig.UseFamilyAndTypeNameForReference = True
    ifcExportConfig.ExportInternalRevitPropertySets = True
    ifcExportConfig.ExportIFCCommonPropertySets = True
    ifcExportConfig.Export2DElements = False
    ifcExportConfig.ExportPartsAsBuildingElements = True
    ifcExportConfig.ExportBoundingBox = False
    ifcExportConfig.ExportSolidModelRep = False
    ifcExportConfig.ExportSchedulesAsPsets = False
    ifcExportConfig.ExportUserDefinedPsets = False
    ifcExportConfig.ExportUserDefinedPsetsFileName = ''
    ifcExportConfig.ExportLinkedFiles = False
    ifcExportConfig.IncludeSiteElevation = True
    ifcExportConfig.UseActiveViewGeometry = False # by model
    ifcExportConfig.ExportSpecificSchedules = False
    ifcExportConfig.TessellationLevelOfDetail = 0
    ifcExportConfig.StoreIFCGUID = True
    ifcExportConfig.ExportRoomsInView = False # might not work in 3D views if volumes are not computed???
    # revit 2019.1
    ifcExportConfig.UseOnlyTriangulation = False
    ifcExportConfig.IncludeSteelElements = True
    ifcExportConfig.COBieCompanyInfo = 'Company Name'
    ifcExportConfig.COBieProjectInfo = 'Project Info'
    
    return ifcExportConfig


#-------------------------------------------- IFC EXPORT Revit 2022 -------------------------------------
# need to check for new features in revit 2022

# ifcVersion        which ifc version (2x3 etc...)
def IFCGetThirdPartyExportConfigByView2022(ifcVersion, ifcSettings):
    '''
    Function returning an IFC export configuration for Revit 2022 using the open source third party IFC exporter plug in supported by AutoDesk
    
    This configuration allows export by view. If ifcVersion is None, IFCVersion.Default will be used.

    :param ifcVersion: The ifc version used for the export.
    :type ifcVersion: Autodesk.Revit.DB.IFCVersion
    :return: An IFCExportConfig object.
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

    if(ifcSettings == None):
        ifcExportConfig = _setupConfigDefaultValues2022(ifcExportConfig, ifcVersion, True)
    else:
        ifcExportConfig = _setupConfigFromSettings2022(ifcExportConfig, ifcSettings)
        
    return ifcExportConfig

# ifcVersion        which ifc version (2x3 etc...)
def IFCGetThirdPartyExportConfigByModel2022(ifcVersion, ifcSettings):
    '''
    Function returning an IFC export configuration for Revit 2022 using the open source third party IFC exporter plug in supported by AutoDesk
    
    This configuration allows export the entire model. If ifcVersion is None, IFCVersion.Default will be used.

    :param ifcVersion: The ifc version used for the export.
    :type ifcVersion: Autodesk.Revit.DB.IFCVersion
    :return: An IFCExportConfig object.
    :rtype: BIM.IFC.Export.UI.IFCExportConfiguration
    '''

    # load version specific assemblies
    ifcThirdPartyFolderPath_ = r'C:\ProgramData\Autodesk\ApplicationPlugins\IFC 2022.bundle\Contents\2022\IFCExporterUIOverride.dll'
    ifcThirdPartyFolderPathEnums_ = r'C:\ProgramData\Autodesk\ApplicationPlugins\IFC 2022.bundle\Contents\2022\Revit.IFC.Common.dll'
    clr.AddReferenceToFileAndPath(ifcThirdPartyFolderPath_)
    clr.AddReferenceToFileAndPath(ifcThirdPartyFolderPathEnums_)

    # import the BIM namespace which includes 
    # IFCExportConfiguration and IFCExportConfigurationMaps classes
    from BIM.IFC.Export.UI import IFCExportConfiguration
    from Revit.IFC.Common.Enums import SiteTransformBasis

    # set up configuration
    ifcExportConfig = IFCExportConfiguration.CreateDefaultConfiguration()
    if(ifcSettings == None):
        ifcExportConfig = _setupConfigDefaultValues2022(ifcExportConfig, ifcVersion, False)
    else:
        ifcExportConfig = _setupConfigFromSettings2022(ifcExportConfig, ifcSettings)
        
    return ifcExportConfig

def _setupConfigFromSettings2022(ifcExportConfig, ifcSettings):
    '''
    Sets up an ifc config object for Revit 2022 based on settings passt in.

    :param ifcExportConfig: An ifc export config object
    :type ifcExportConfig: BIM.IFC.Export.UI.IFCExportConfiguration
    :param ifcSettings: The settings to be applied to the ifc export config
    :type ifcSettings: :class:`.IFCSettings`

    :return: An ifc export config
    :rtype: BIM.IFC.Export.UI.IFCExportConfiguration
    '''

    ifcThirdPartyFolderPathEnums_ = r'C:\ProgramData\Autodesk\ApplicationPlugins\IFC 2022.bundle\Contents\2022\Revit.IFC.Common.dll'
    clr.AddReferenceToFileAndPath(ifcThirdPartyFolderPathEnums_)
    from Revit.IFC.Common.Enums import SiteTransformBasis

    ifcExportConfig.Name = ifcSettings.name
    # set up IFC version
    if(ifcSettings.ifcVersion == 'IFCBCA'):
        ifcExportConfig.IFCVersion = rdb.IFCVersion.IFCBCA
    elif(ifcSettings.ifcVersion == 'IFC2x2'):
        ifcExportConfig.IFCVersion = rdb.IFCVersion.IFC2x2
    elif(ifcSettings.ifcVersion == 'IFC2x3'):
        ifcExportConfig.IFCVersion = rdb.IFCVersion.IFC2x3
    elif(ifcSettings.ifcVersion == 'IFCCOBIE'):
        ifcExportConfig.IFCVersion = rdb.IFCVersion.IFCCOBIE
    elif(ifcSettings.ifcVersion == 'IFC2x3CV2'):
        ifcExportConfig.IFCVersion = rdb.IFCVersion.IFC2x3CV2
    elif(ifcSettings.ifcVersion == 'IFC4'):
        ifcExportConfig.IFCVersion = rdb.IFCVersion.IFC4
    elif(ifcSettings.ifcVersion == 'IFC2x3FM'):
        ifcExportConfig.IFCVersion = rdb.IFCVersion.IFC2x3FM
    elif(ifcSettings.ifcVersion == 'IFC4RV'):
        ifcExportConfig.IFCVersion = rdb.IFCVersion.IFC4RV
    elif(ifcSettings.ifcVersion == 'IFC4DTV'):
        ifcExportConfig.IFCVersion = rdb.IFCVersion.IFC4DTV
    elif(ifcSettings.ifcVersion == 'IFC2x3BFM'):
        ifcExportConfig.IFCVersion = rdb.IFCVersion.IFC2x3BFM
    else:
        ifcExportConfig.IFCVersion = rdb.IFCVersion.Default
        
    ifcExportConfig.SpaceBoundaries = ifcSettings.spaceBoundaries
    ifcExportConfig.ActivePhaseId = ifcSettings.activePhaseId
    ifcExportConfig.ActiveViewId = ifcSettings.activeViewId
    ifcExportConfig.ExportBaseQuantities = ifcSettings.exportBaseQuantities
    ifcExportConfig.SplitWallsAndColumns = ifcSettings.splitWallsAndColumns
    ifcExportConfig.VisibleElementsOfCurrentView = ifcSettings.visibleElementsOfCurrentView
    ifcExportConfig.Use2DRoomBoundaryForVolume = ifcSettings.use2DRoomBoundaryForVolume
    ifcExportConfig.UseFamilyAndTypeNameForReference = ifcSettings.useFamilyAndTypeNameForReference
    ifcExportConfig.ExportInternalRevitPropertySets = ifcSettings.exportInternalRevitPropertySets
    ifcExportConfig.ExportIFCCommonPropertySets = ifcSettings.exportIFCCommonPropertySets
    ifcExportConfig.Export2DElements = ifcSettings.export2DElements
    ifcExportConfig.ExportPartsAsBuildingElements = ifcSettings.exportPartsAsBuildingElements
    ifcExportConfig.ExportBoundingBox = ifcSettings.exportBoundingBox
    ifcExportConfig.ExportSolidModelRep = ifcSettings.exportSolidModelRep
    ifcExportConfig.ExportSchedulesAsPsets = ifcSettings.exportSchedulesAsPsets
    ifcExportConfig.ExportUserDefinedPsets = ifcSettings.exportUserDefinedPsets
    ifcExportConfig.ExportUserDefinedPsetsFileName = ifcSettings.exportUserDefinedPsetsFileName
    ifcExportConfig.ExportLinkedFiles = ifcSettings.exportLinkedFiles
    ifcExportConfig.IncludeSiteElevation = ifcSettings.includeSiteElevation
    ifcExportConfig.UseActiveViewGeometry = ifcSettings.useActiveViewGeometry
    ifcExportConfig.ExportSpecificSchedules = ifcSettings.exportSpecificSchedules
    ifcExportConfig.TessellationLevelOfDetail = ifcSettings.tessellationLevelOfDetail
    ifcExportConfig.StoreIFCGUID = ifcSettings.storeIFCGUID
    ifcExportConfig.ExportRoomsInView = ifcSettings.exportRoomsInView
    ifcExportConfig.UseOnlyTriangulation = ifcSettings.useOnlyTriangulation
    ifcExportConfig.IncludeSteelElements = ifcSettings.includeSteelElements
    ifcExportConfig.COBieCompanyInfo = ifcSettings.cOBieCompanyInfo
    ifcExportConfig.COBieProjectInfo = ifcSettings.cOBieProjectInfo
    ifcExportConfig.UseTypeNameOnlyForIfcType = ifcSettings.useTypeNameOnlyForIfcType
    ifcExportConfig.UseVisibleRevitNameAsEntityName = ifcSettings.useVisibleRevitNameAsEntityName
        
    # set up site placement
    if(ifcSettings.sitePlacement == 'shared'):
        ifcExportConfig.SitePlacement = SiteTransformBasis.Shared
    elif(ifcSettings.sitePlacement == 'site'):
        ifcExportConfig.SitePlacement = SiteTransformBasis.Site
    elif(ifcSettings.sitePlacement == 'project'):
        ifcExportConfig.SitePlacement = SiteTransformBasis.Project
    elif(ifcSettings.sitePlacement == 'internal'):
        ifcExportConfig.SitePlacement = SiteTransformBasis.Internal
    elif(ifcSettings.sitePlacement == 'projectInTN'):
        ifcExportConfig.SitePlacement = SiteTransformBasis.ProjectInTN
    else:
        ifcExportConfig.SitePlacement = SiteTransformBasis.InternalInTN
    
    ifcExportConfig.GeoRefCRSName = ifcSettings.geoRefCRSName
    ifcExportConfig.GeoRefCRSDesc = ifcSettings.geoRefCRSDesc
    ifcExportConfig.GeoRefEPSGCode = ifcSettings.geoRefEPSGCode
    ifcExportConfig.GeoRefGeodeticDatum = ifcSettings.geoRefGeodeticDatum
    ifcExportConfig.GeoRefMapUnit = ifcSettings.geoRefMapUnit
    ifcExportConfig.ExcludeFilter = ifcSettings.excludeFilter

    return ifcExportConfig

def _setupConfigDefaultValues2022(ifcExportConfig, ifcVersion, exportByView):
    '''
    Sets up an default ifc config object for Revit 2022.

    :param ifcExportConfig: An ifc export config
    :type ifcExportConfig: BIM.IFC.Export.UI.IFCExportConfiguration
    :param ifcVersion: The Ifc version to be used for the export.
    :type ifcVersion:  Autodesk.Revit.DB.IFCVersion
    :param exportByView: True export by view, False export by model.
    :type exportByView: bool

    :return: An ifc export config
    :rtype: BIM.IFC.Export.UI.IFCExportConfiguration
    '''

    ifcExportConfig.Name = 'DefaultIFCByModelSetup'
    
    # set up IFC version
    if(ifcVersion is None or ifcVersion == ''):
        ifcExportConfig.IFCVersion = rdb.IFCVersion.Default
    else:  
        ifcExportConfig.IFCVersion = ifcVersion

    ifcExportConfig.SpaceBoundaries = 1
    ifcExportConfig.ActivePhaseId = rdb.ElementId.InvalidElementId.IntegerValue
    ifcExportConfig.ExportBaseQuantities = True
    ifcExportConfig.SplitWallsAndColumns = True
    ifcExportConfig.VisibleElementsOfCurrentView = exportByView # by model
    ifcExportConfig.Use2DRoomBoundaryForVolume = False
    ifcExportConfig.UseFamilyAndTypeNameForReference = True
    ifcExportConfig.ExportInternalRevitPropertySets = True
    ifcExportConfig.ExportIFCCommonPropertySets = True
    ifcExportConfig.Export2DElements = False
    ifcExportConfig.ExportPartsAsBuildingElements = True
    ifcExportConfig.ExportBoundingBox = False
    ifcExportConfig.ExportSolidModelRep = False
    ifcExportConfig.ExportSchedulesAsPsets = False
    ifcExportConfig.ExportUserDefinedPsets = False
    ifcExportConfig.ExportUserDefinedPsetsFileName = ''
    ifcExportConfig.ExportLinkedFiles = False
    ifcExportConfig.IncludeSiteElevation = True
    ifcExportConfig.UseActiveViewGeometry = False # by model
    ifcExportConfig.ExportSpecificSchedules = False
    ifcExportConfig.TessellationLevelOfDetail = 0
    ifcExportConfig.StoreIFCGUID = True
    ifcExportConfig.ExportRoomsInView = exportByView # might not work in 3D views if volumes are not computed???
    ifcExportConfig.UseOnlyTriangulation = False
    ifcExportConfig.IncludeSteelElements = True
    ifcExportConfig.COBieCompanyInfo = 'Company Name'
    ifcExportConfig.COBieProjectInfo = 'Project Info'
    return ifcExportConfig
