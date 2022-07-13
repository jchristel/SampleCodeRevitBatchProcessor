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

clr.AddReference('System.Core')
clr.ImportExtensions(System.Linq)

import Autodesk.Revit.DB as rdb

#-------------------------------------------- IFC EXPORT Revit 2019 -------------------------------------

def IFCGetThirdPartyExportConfigByView2019(ifcVersion):
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
def IFCGetThirdPartyExportConfigByModel2019(ifcVersion):
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

def IFCGetThirdPartyExportConfigByView2020(ifcVersion):
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
def IFCGetThirdPartyExportConfigByModel2020(ifcVersion):
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
def IFCGetThirdPartyExportConfigByView2021(ifcVersion):
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
def IFCGetThirdPartyExportConfigByModel2021(ifcVersion):
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
def IFCGetThirdPartyExportConfigByView2022(ifcVersion):
    '''
    Function returning an IFC export configuration for Revit 2022 using the open source third party IFC exporter plug in supported by AutoDesk
    
    This configuration allows export by view. If ifcVersion is None, IFCVersion.Default will be used.

    :param ifcVersion: The ifc version used for the export.
    :type ifcVersion: Autodesk.Revit.DB.IFCVersion
    :return: An IFCExportConfig object.
    :rtype: BIM.IFC.Export.UI.IFCExportConfiguration
    '''

    # load version specific assemblies
    ifcThirdPartyFolderPath_ = r'C:\ProgramData\Autodesk\ApplicationPlugins\IFC 2022.bundle\Contents\2022\IFCExportUIOverride.dll'
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
    ifcExportConfig.ActivePhaseId = rdb.ElementId.InvalidElementId.IntegerValue
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
def IFCGetThirdPartyExportConfigByModel2022(ifcVersion):
    '''
    Function returning an IFC export configuration for Revit 2022 using the open source third party IFC exporter plug in supported by AutoDesk
    
    This configuration allows export the entire model. If ifcVersion is None, IFCVersion.Default will be used.

    :param ifcVersion: The ifc version used for the export.
    :type ifcVersion: Autodesk.Revit.DB.IFCVersion
    :return: An IFCExportConfig object.
    :rtype: BIM.IFC.Export.UI.IFCExportConfiguration
    '''

    # load version specific assemblies
    ifcThirdPartyFolderPath_ = r'C:\ProgramData\Autodesk\ApplicationPlugins\IFC 2022.bundle\Contents\2022\IFCExportUIOverride.dll'
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