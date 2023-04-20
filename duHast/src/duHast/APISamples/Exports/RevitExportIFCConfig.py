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

def ifc_get_third_party_export_config_by_view_2019(ifc_version, ifc_settings):
    '''
    Function returning an IFC export configuration for Revit 2019 using the open source third party IFC exporter plug in supported by AutoDesk
    
    This configuration allows export by view. If ifc_version is None, IFCVersion.Default will be used.

    :param ifc_version: The ifc version used for the export.
    :type ifc_version: Autodesk.Revit.DB.IFCVersion
    :return: An IFCExportConfig object.
    :rtype: BIM.IFC.Export.UI.IFCExportConfiguration
    '''

    # load version specific assemblies
    ifc_third_party_folder_path_ = r'C:\ProgramData\Autodesk\ApplicationPlugins\IFC 2019.bundle\Contents\2019\IFCExportUIOverride.dll'
    clr.AddReferenceToFileAndPath(ifc_third_party_folder_path_)
    # import the BIM namespace which includes 
    # IFCExportConfiguration and IFCExportConfigurationMaps classes
    from BIM.IFC.Export.UI import IFCExportConfiguration

    ifc_export_config = IFCExportConfiguration.CreateDefaultConfiguration()
    ifc_export_config.Name = 'DefaultIFCByViewSetup'
    # set up IFC version
    if(ifc_version is None or ifc_version == ''):
        ifc_export_config.IFCVersion = rdb.IFCVersion.Default
    else:  
        ifc_export_config.IFCVersion = ifc_version

    ifc_export_config.SpaceBoundaries = 1
    ifc_export_config.ActivePhaseId = rdb.ElementId.InvalidElementId
    ifc_export_config.ExportBaseQuantities = True
    ifc_export_config.SplitWallsAndColumns = True
    ifc_export_config.VisibleElementsOfCurrentView = True # by view
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
    ifc_export_config.ExportUserDefinedPsetsFileName = ''
    ifc_export_config.ExportLinkedFiles = False
    ifc_export_config.IncludeSiteElevation = True
    ifc_export_config.UseActiveViewGeometry = False # setting this value to True will slow down the IFC export considerably (sample: from 8min to 45min!)
    ifc_export_config.ExportSpecificSchedules = False
    ifc_export_config.TessellationLevelOfDetail = 0
    ifc_export_config.StoreIFCGUID = True
    ifc_export_config.ExportRoomsInView = False # might not work in 3D views if volumes are not computed???
    # revit 2019.1
    ifc_export_config.UseOnlyTriangulation = False
    ifc_export_config.IncludeSteelElements = True
    ifc_export_config.COBieCompanyInfo = 'Company Name'
    ifc_export_config.COBieProjectInfo = 'Project Info'
    
    return ifc_export_config

# ifcVersion        which ifc version (2x3 etc...)
def ifc_get_third_party_export_config_by_model_2019(ifc_version, ifc_settings):
    '''
    Function returning an IFC export configuration for Revit 2019 using the open source third party IFC exporter plug in supported by AutoDesk
    
    This configuration allows export the entire model. If ifc_version is None, IFCVersion.Default will be used.

    :param ifc_version: The ifc version used for the export.
    :type ifc_version: Autodesk.Revit.DB.IFCVersion
    :return: An IFCExportConfig object.
    :rtype: BIM.IFC.Export.UI.IFCExportConfiguration
    '''

    # load version specific assemblies
    ifc_third_party_folder_path_ = r'C:\ProgramData\Autodesk\ApplicationPlugins\IFC 2019.bundle\Contents\2019\IFCExportUIOverride.dll'
    clr.AddReferenceToFileAndPath(ifc_third_party_folder_path_)
    # import the BIM namespace which includes 
    # IFCExportConfiguration and IFCExportConfigurationMaps classes
    from BIM.IFC.Export.UI import IFCExportConfiguration

    ifc_export_config = IFCExportConfiguration.CreateDefaultConfiguration()
    ifc_export_config.Name = 'DefaultIFCByModelSetup'
    
    # set up IFC version
    if(ifc_version is None or ifc_version == ''):
        ifc_export_config.IFCVersion = rdb.IFCVersion.Default
    else:  
        ifc_export_config.IFCVersion = ifc_version

    ifc_export_config.SpaceBoundaries = 1
    ifc_export_config.ActivePhaseId = rdb.ElementId.InvalidElementId
    ifc_export_config.ExportBaseQuantities = True
    ifc_export_config.SplitWallsAndColumns = True
    ifc_export_config.VisibleElementsOfCurrentView = False # by model
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
    ifc_export_config.ExportUserDefinedPsetsFileName = ''
    ifc_export_config.ExportLinkedFiles = False
    ifc_export_config.IncludeSiteElevation = True
    ifc_export_config.UseActiveViewGeometry = False # by model
    ifc_export_config.ExportSpecificSchedules = False
    ifc_export_config.TessellationLevelOfDetail = 0
    ifc_export_config.StoreIFCGUID = True
    ifc_export_config.ExportRoomsInView = False # might not work in 3D views if volumes are not computed???
    # revit 2019.1
    ifc_export_config.UseOnlyTriangulation = False
    ifc_export_config.IncludeSteelElements = True
    ifc_export_config.COBieCompanyInfo = 'Company Name'
    ifc_export_config.COBieProjectInfo = 'Project Info'
    
    return ifc_export_config

#-------------------------------------------- IFC EXPORT Revit 2020 -------------------------------------
# need to check for new features in revit 2020

def ifc_get_third_party_export_config_by_view_2020(ifc_version, ifc_settings):
    '''
    Function returning an IFC export configuration for Revit 2020 using the open source third party IFC exporter plug in supported by AutoDesk
    
    This configuration allows export by view. If ifc_version is None, IFCVersion.Default will be used.

    :param ifc_version: The ifc version used for the export (2x3 etc...).
    :type ifc_version: Autodesk.Revit.DB.IFCVersion
    :return: An IFCExportConfig object.
    :rtype: BIM.IFC.Export.UI.IFCExportConfiguration
    '''

    # load version specific assemblies
    ifc_third_party_folder_path_ = r'C:\ProgramData\Autodesk\ApplicationPlugins\IFC 2020.bundle\Contents\2020\IFCExportUIOverride.dll'
    clr.AddReferenceToFileAndPath(ifc_third_party_folder_path_)
    # import the BIM namespace which includes 
    # IFCExportConfiguration and IFCExportConfigurationMaps classes
    from BIM.IFC.Export.UI import IFCExportConfiguration

    # set up configuration
    ifc_export_config = IFCExportConfiguration.CreateDefaultConfiguration()
    ifc_export_config.Name = 'DefaultIFCByViewSetup'
    # set up IFC version
    if(ifc_version is None or ifc_version == ''):
        ifc_export_config.IFCVersion = rdb.IFCVersion.Default
    else:  
        ifc_export_config.IFCVersion = ifc_version

    ifc_export_config.SpaceBoundaries = 1
    ifc_export_config.ActivePhaseId = rdb.ElementId.InvalidElementId
    ifc_export_config.ExportBaseQuantities = True
    ifc_export_config.SplitWallsAndColumns = True
    ifc_export_config.VisibleElementsOfCurrentView = True # by view
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
    ifc_export_config.ExportUserDefinedPsetsFileName = ''
    ifc_export_config.ExportLinkedFiles = False
    ifc_export_config.IncludeSiteElevation = True
    ifc_export_config.UseActiveViewGeometry = False # setting this value to True will slow down the IFC export considerably (sample: from 8min to 45min!)
    ifc_export_config.ExportSpecificSchedules = False
    ifc_export_config.TessellationLevelOfDetail = 0
    ifc_export_config.StoreIFCGUID = True
    ifc_export_config.ExportRoomsInView = False # might not work in 3D views if volumes are not computed???
    # revit 2019.1
    ifc_export_config.UseOnlyTriangulation = False
    ifc_export_config.IncludeSteelElements = True
    ifc_export_config.COBieCompanyInfo = 'Company Name'
    ifc_export_config.COBieProjectInfo = 'Project Info'
    
    return ifc_export_config

# ifcVersion        which ifc version (2x3 etc...)
def ifc_get_third_party_export_config_by_model_2020(ifc_version, ifc_settings):
    '''
    Function returning an IFC export configuration for Revit 2020 using the open source third party IFC exporter plug in supported by AutoDesk
    
    This configuration allows export the entire model. If ifc_version is None, IFCVersion.Default will be used.

    :param ifc_version: The ifc version used for the export.
    :type ifc_version: Autodesk.Revit.DB.IFCVersion
    :return: An IFCExportConfig object.
    :rtype: BIM.IFC.Export.UI.IFCExportConfiguration
    '''

    # load version specific assemblies
    ifc_third_party_folder_path_ = r'C:\ProgramData\Autodesk\ApplicationPlugins\IFC 2020.bundle\Contents\2020\IFCExportUIOverride.dll'
    clr.AddReferenceToFileAndPath(ifc_third_party_folder_path_)
    # import the BIM namespace which includes 
    # IFCExportConfiguration and IFCExportConfigurationMaps classes
    from BIM.IFC.Export.UI import IFCExportConfiguration

    # set up configuration
    ifc_export_config = IFCExportConfiguration.CreateDefaultConfiguration()
    ifc_export_config.Name = 'DefaultIFCByModelSetup'
    
    # set up IFC version
    if(ifc_version is None or ifc_version == ''):
        ifc_export_config.IFCVersion = rdb.IFCVersion.Default
    else:  
        ifc_export_config.IFCVersion = ifc_version

    ifc_export_config.SpaceBoundaries = 1
    ifc_export_config.ActivePhaseId = rdb.ElementId.InvalidElementId
    ifc_export_config.ExportBaseQuantities = True
    ifc_export_config.SplitWallsAndColumns = True
    ifc_export_config.VisibleElementsOfCurrentView = False # by model
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
    ifc_export_config.ExportUserDefinedPsetsFileName = ''
    ifc_export_config.ExportLinkedFiles = False
    ifc_export_config.IncludeSiteElevation = True
    ifc_export_config.UseActiveViewGeometry = False # by model
    ifc_export_config.ExportSpecificSchedules = False
    ifc_export_config.TessellationLevelOfDetail = 0
    ifc_export_config.StoreIFCGUID = True
    ifc_export_config.ExportRoomsInView = False # might not work in 3D views if volumes are not computed???
    # revit 2019.1
    ifc_export_config.UseOnlyTriangulation = False
    ifc_export_config.IncludeSteelElements = True
    ifc_export_config.COBieCompanyInfo = 'Company Name'
    ifc_export_config.COBieProjectInfo = 'Project Info'
    
    return ifc_export_config

#-------------------------------------------- IFC EXPORT Revit 2021 -------------------------------------
# need to check for new features in revit 2021

# ifcVersion        which ifc version (2x3 etc...)
def ifc_get_third_party_export_config_by_view_2021(ifc_version, ifc_settings):
    '''
    Function returning an IFC export configuration for Revit 2021 using the open source third party IFC exporter plug in supported by AutoDesk
    
    This configuration allows export by view. If ifc_version is None, IFCVersion.Default will be used.

    :param ifc_version: The ifc version used for the export.
    :type ifc_version: Autodesk.Revit.DB.IFCVersion
    :return: An IFCExportConfig object.
    :rtype: BIM.IFC.Export.UI.IFCExportConfiguration
    '''

    # load version specific assemblies
    ifc_third_party_folder_path_ = r'C:\ProgramData\Autodesk\ApplicationPlugins\IFC 2021.bundle\Contents\2021\IFCExportUIOverride.dll'
    clr.AddReferenceToFileAndPath(ifc_third_party_folder_path_)
    # import the BIM namespace which includes 
    # IFCExportConfiguration and IFCExportConfigurationMaps classes
    from BIM.IFC.Export.UI import IFCExportConfiguration

    # set up configuration
    ifc_export_config = IFCExportConfiguration.CreateDefaultConfiguration()
    ifc_export_config.Name = 'DefaultIFCByViewSetup'
    # set up IFC version
    if(ifc_version is None or ifc_version == ''):
        ifc_export_config.IFCVersion = rdb.IFCVersion.Default
    else:  
        ifc_export_config.IFCVersion = ifc_version

    ifc_export_config.SpaceBoundaries = 1
    ifc_export_config.ActivePhaseId = rdb.ElementId.InvalidElementId
    ifc_export_config.ExportBaseQuantities = True
    ifc_export_config.SplitWallsAndColumns = True
    ifc_export_config.VisibleElementsOfCurrentView = True # by view
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
    ifc_export_config.ExportUserDefinedPsetsFileName = ''
    ifc_export_config.ExportLinkedFiles = False
    ifc_export_config.IncludeSiteElevation = True
    ifc_export_config.UseActiveViewGeometry = False # setting this value to True will slow down the IFC export considerably (sample: from 8min to 45min!)
    ifc_export_config.ExportSpecificSchedules = False
    ifc_export_config.TessellationLevelOfDetail = 0
    ifc_export_config.StoreIFCGUID = True
    ifc_export_config.ExportRoomsInView = False # might not work in 3D views if volumes are not computed???
    # revit 2019.1
    ifc_export_config.UseOnlyTriangulation = False
    ifc_export_config.IncludeSteelElements = True
    ifc_export_config.COBieCompanyInfo = 'Company Name'
    ifc_export_config.COBieProjectInfo = 'Project Info'
    
    return ifc_export_config

# ifcVersion        which ifc version (2x3 etc...)
def ifc_get_third_party_export_config_by_model_2021(ifc_version, ifc_settings):
    '''
    Function returning an IFC export configuration for Revit 2021 using the open source third party IFC exporter plug in supported by AutoDesk
    
    This configuration allows export the entire model. If ifc_version is None, IFCVersion.Default will be used.

    :param ifc_version: The ifc version used for the export.
    :type ifc_version: Autodesk.Revit.DB.IFCVersion
    :return: An IFCExportConfig object.
    :rtype: BIM.IFC.Export.UI.IFCExportConfiguration
    '''

    # load version specific assemblies
    ifc_third_party_folder_path_ = r'C:\ProgramData\Autodesk\ApplicationPlugins\IFC 2021.bundle\Contents\2021\IFCExportUIOverride.dll'
    clr.AddReferenceToFileAndPath(ifc_third_party_folder_path_)
    # import the BIM namespace which includes 
    # IFCExportConfiguration and IFCExportConfigurationMaps classes
    from BIM.IFC.Export.UI import IFCExportConfiguration

    # set up configuration
    ifc_export_config = IFCExportConfiguration.CreateDefaultConfiguration()
    ifc_export_config.Name = 'DefaultIFCByModelSetup'
    
    # set up IFC version
    if(ifc_version is None or ifc_version == ''):
        ifc_export_config.IFCVersion = rdb.IFCVersion.Default
    else:  
        ifc_export_config.IFCVersion = ifc_version

    ifc_export_config.SpaceBoundaries = 1
    ifc_export_config.ActivePhaseId = rdb.ElementId.InvalidElementId
    ifc_export_config.ExportBaseQuantities = True
    ifc_export_config.SplitWallsAndColumns = True
    ifc_export_config.VisibleElementsOfCurrentView = False # by model
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
    ifc_export_config.ExportUserDefinedPsetsFileName = ''
    ifc_export_config.ExportLinkedFiles = False
    ifc_export_config.IncludeSiteElevation = True
    ifc_export_config.UseActiveViewGeometry = False # by model
    ifc_export_config.ExportSpecificSchedules = False
    ifc_export_config.TessellationLevelOfDetail = 0
    ifc_export_config.StoreIFCGUID = True
    ifc_export_config.ExportRoomsInView = False # might not work in 3D views if volumes are not computed???
    # revit 2019.1
    ifc_export_config.UseOnlyTriangulation = False
    ifc_export_config.IncludeSteelElements = True
    ifc_export_config.COBieCompanyInfo = 'Company Name'
    ifc_export_config.COBieProjectInfo = 'Project Info'
    
    return ifc_export_config


#-------------------------------------------- IFC EXPORT Revit 2022 -------------------------------------
# need to check for new features in revit 2022

# ifcVersion        which ifc version (2x3 etc...)
def ifc_get_third_party_export_config_by_view_2022(ifc_version, ifc_settings):
    '''
    Function returning an IFC export configuration for Revit 2022 using the open source third party IFC exporter plug in supported by AutoDesk
    
    This configuration allows export by view. If ifc_version is None, IFCVersion.Default will be used.

    :param ifc_version: The ifc version used for the export.
    :type ifc_version: Autodesk.Revit.DB.IFCVersion
    :return: An IFCExportConfig object.
    :rtype: BIM.IFC.Export.UI.IFCExportConfiguration
    '''

    # load version specific assemblies
    ifc_third_party_folder_path_ = r'C:\ProgramData\Autodesk\ApplicationPlugins\IFC 2022.bundle\Contents\2022\IFCExporterUIOverride.dll'
    
    clr.AddReferenceToFileAndPath(ifc_third_party_folder_path_)
    
    # import the BIM namespace which includes 
    # IFCExportConfiguration and IFCExportConfigurationMaps classes
    from BIM.IFC.Export.UI import IFCExportConfiguration
    

    # set up configuration
    ifc_export_config = IFCExportConfiguration.CreateDefaultConfiguration()

    if(ifc_settings == None):
        ifc_export_config = _setup_config_default_values_2022(ifc_export_config, ifc_version, True)
    else:
        ifc_export_config = _setup_config_from_settings_2022(ifc_export_config, ifc_settings)
        
    return ifc_export_config

# ifcVersion        which ifc version (2x3 etc...)
def ifc_get_third_party_export_config_by_model_2022(ifc_version, ifc_settings):
    '''
    Function returning an IFC export configuration for Revit 2022 using the open source third party IFC exporter plug in supported by AutoDesk
    
    This configuration allows export the entire model. If ifc_version is None, IFCVersion.Default will be used.

    :param ifc_version: The ifc version used for the export.
    :type ifc_version: Autodesk.Revit.DB.IFCVersion
    :return: An IFCExportConfig object.
    :rtype: BIM.IFC.Export.UI.IFCExportConfiguration
    '''

    # load version specific assemblies
    ifc_third_party_folder_path_ = r'C:\ProgramData\Autodesk\ApplicationPlugins\IFC 2022.bundle\Contents\2022\IFCExporterUIOverride.dll'
    ifc_third_party_folder_path_enums_ = r'C:\ProgramData\Autodesk\ApplicationPlugins\IFC 2022.bundle\Contents\2022\Revit.IFC.Common.dll'
    clr.AddReferenceToFileAndPath(ifc_third_party_folder_path_)
    clr.AddReferenceToFileAndPath(ifc_third_party_folder_path_enums_)

    # import the BIM namespace which includes 
    # IFCExportConfiguration and IFCExportConfigurationMaps classes
    from BIM.IFC.Export.UI import IFCExportConfiguration
    from Revit.IFC.Common.Enums import SiteTransformBasis

    # set up configuration
    ifc_export_config = IFCExportConfiguration.CreateDefaultConfiguration()
    if(ifc_settings == None):
        ifc_export_config = _setup_config_default_values_2022(ifc_export_config, ifc_version, False)
    else:
        ifc_export_config = _setup_config_from_settings_2022(ifc_export_config, ifc_settings)
        
    return ifc_export_config

def _setup_config_from_settings_2022(ifc_export_config, ifc_settings):
    '''
    Sets up an ifc config object for Revit 2022 based on settings passt in.

    :param ifc_export_config: An ifc export config object
    :type ifc_export_config: BIM.IFC.Export.UI.IFCExportConfiguration
    :param ifc_settings: The settings to be applied to the ifc export config
    :type ifc_settings: :class:`.IFCSettings`

    :return: An ifc export config
    :rtype: BIM.IFC.Export.UI.IFCExportConfiguration
    '''

    ifc_third_party_folder_path_enums_ = r'C:\ProgramData\Autodesk\ApplicationPlugins\IFC 2022.bundle\Contents\2022\Revit.IFC.Common.dll'
    clr.AddReferenceToFileAndPath(ifc_third_party_folder_path_enums_)
    from Revit.IFC.Common.Enums import SiteTransformBasis

    ifc_export_config.Name = ifc_settings.name
    # set up IFC version
    if(ifc_settings.ifcVersion == 'IFCBCA'):
        ifc_export_config.IFCVersion = rdb.IFCVersion.IFCBCA
    elif(ifc_settings.ifcVersion == 'IFC2x2'):
        ifc_export_config.IFCVersion = rdb.IFCVersion.IFC2x2
    elif(ifc_settings.ifcVersion == 'IFC2x3'):
        ifc_export_config.IFCVersion = rdb.IFCVersion.IFC2x3
    elif(ifc_settings.ifcVersion == 'IFCCOBIE'):
        ifc_export_config.IFCVersion = rdb.IFCVersion.IFCCOBIE
    elif(ifc_settings.ifcVersion == 'IFC2x3CV2'):
        ifc_export_config.IFCVersion = rdb.IFCVersion.IFC2x3CV2
    elif(ifc_settings.ifcVersion == 'IFC4'):
        ifc_export_config.IFCVersion = rdb.IFCVersion.IFC4
    elif(ifc_settings.ifcVersion == 'IFC2x3FM'):
        ifc_export_config.IFCVersion = rdb.IFCVersion.IFC2x3FM
    elif(ifc_settings.ifcVersion == 'IFC4RV'):
        ifc_export_config.IFCVersion = rdb.IFCVersion.IFC4RV
    elif(ifc_settings.ifcVersion == 'IFC4DTV'):
        ifc_export_config.IFCVersion = rdb.IFCVersion.IFC4DTV
    elif(ifc_settings.ifcVersion == 'IFC2x3BFM'):
        ifc_export_config.IFCVersion = rdb.IFCVersion.IFC2x3BFM
    else:
        ifc_export_config.IFCVersion = rdb.IFCVersion.Default
        
    ifc_export_config.SpaceBoundaries = ifc_settings.spaceBoundaries
    ifc_export_config.ActivePhaseId = ifc_settings.activePhaseId
    ifc_export_config.ActiveViewId = ifc_settings.activeViewId
    ifc_export_config.ExportBaseQuantities = ifc_settings.exportBaseQuantities
    ifc_export_config.SplitWallsAndColumns = ifc_settings.splitWallsAndColumns
    ifc_export_config.VisibleElementsOfCurrentView = ifc_settings.visibleElementsOfCurrentView
    ifc_export_config.Use2DRoomBoundaryForVolume = ifc_settings.use2DRoomBoundaryForVolume
    ifc_export_config.UseFamilyAndTypeNameForReference = ifc_settings.useFamilyAndTypeNameForReference
    ifc_export_config.ExportInternalRevitPropertySets = ifc_settings.exportInternalRevitPropertySets
    ifc_export_config.ExportIFCCommonPropertySets = ifc_settings.exportIFCCommonPropertySets
    ifc_export_config.Export2DElements = ifc_settings.export2DElements
    ifc_export_config.ExportPartsAsBuildingElements = ifc_settings.exportPartsAsBuildingElements
    ifc_export_config.ExportBoundingBox = ifc_settings.exportBoundingBox
    ifc_export_config.ExportSolidModelRep = ifc_settings.exportSolidModelRep
    ifc_export_config.ExportSchedulesAsPsets = ifc_settings.exportSchedulesAsPsets
    ifc_export_config.ExportUserDefinedPsets = ifc_settings.exportUserDefinedPsets
    ifc_export_config.ExportUserDefinedPsetsFileName = ifc_settings.exportUserDefinedPsetsFileName
    ifc_export_config.ExportLinkedFiles = ifc_settings.exportLinkedFiles
    ifc_export_config.IncludeSiteElevation = ifc_settings.includeSiteElevation
    ifc_export_config.UseActiveViewGeometry = ifc_settings.useActiveViewGeometry
    ifc_export_config.ExportSpecificSchedules = ifc_settings.exportSpecificSchedules
    ifc_export_config.TessellationLevelOfDetail = ifc_settings.tessellationLevelOfDetail
    ifc_export_config.StoreIFCGUID = ifc_settings.storeIFCGUID
    ifc_export_config.ExportRoomsInView = ifc_settings.exportRoomsInView
    ifc_export_config.UseOnlyTriangulation = ifc_settings.useOnlyTriangulation
    ifc_export_config.IncludeSteelElements = ifc_settings.includeSteelElements
    ifc_export_config.COBieCompanyInfo = ifc_settings.cOBieCompanyInfo
    ifc_export_config.COBieProjectInfo = ifc_settings.cOBieProjectInfo
    ifc_export_config.UseTypeNameOnlyForIfcType = ifc_settings.useTypeNameOnlyForIfcType
    ifc_export_config.UseVisibleRevitNameAsEntityName = ifc_settings.useVisibleRevitNameAsEntityName
        
    # set up site placement
    if(ifc_settings.sitePlacement == 'shared'):
        ifc_export_config.SitePlacement = SiteTransformBasis.Shared
    elif(ifc_settings.sitePlacement == 'site'):
        ifc_export_config.SitePlacement = SiteTransformBasis.Site
    elif(ifc_settings.sitePlacement == 'project'):
        ifc_export_config.SitePlacement = SiteTransformBasis.Project
    elif(ifc_settings.sitePlacement == 'internal'):
        ifc_export_config.SitePlacement = SiteTransformBasis.Internal
    elif(ifc_settings.sitePlacement == 'projectInTN'):
        ifc_export_config.SitePlacement = SiteTransformBasis.ProjectInTN
    else:
        ifc_export_config.SitePlacement = SiteTransformBasis.InternalInTN
    
    ifc_export_config.GeoRefCRSName = ifc_settings.geoRefCRSName
    ifc_export_config.GeoRefCRSDesc = ifc_settings.geoRefCRSDesc
    ifc_export_config.GeoRefEPSGCode = ifc_settings.geoRefEPSGCode
    ifc_export_config.GeoRefGeodeticDatum = ifc_settings.geoRefGeodeticDatum
    ifc_export_config.GeoRefMapUnit = ifc_settings.geoRefMapUnit
    ifc_export_config.ExcludeFilter = ifc_settings.excludeFilter

    return ifc_export_config

def _setup_config_default_values_2022(ifc_export_config, ifc_version, export_by_view):
    '''
    Sets up an default ifc config object for Revit 2022.

    :param ifc_export_config: An ifc export config
    :type ifc_export_config: BIM.IFC.Export.UI.IFCExportConfiguration
    :param ifc_version: The Ifc version to be used for the export.
    :type ifc_version:  Autodesk.Revit.DB.IFCVersion
    :param export_by_view: True export by view, False export by model.
    :type export_by_view: bool

    :return: An ifc export config
    :rtype: BIM.IFC.Export.UI.IFCExportConfiguration
    '''

    ifc_export_config.Name = 'DefaultIFCByModelSetup'
    
    # set up IFC version
    if(ifc_version is None or ifc_version == ''):
        ifc_export_config.IFCVersion = rdb.IFCVersion.Default
    else:  
        ifc_export_config.IFCVersion = ifc_version

    ifc_export_config.SpaceBoundaries = 1
    ifc_export_config.ActivePhaseId = rdb.ElementId.InvalidElementId.IntegerValue
    ifc_export_config.ExportBaseQuantities = True
    ifc_export_config.SplitWallsAndColumns = True
    ifc_export_config.VisibleElementsOfCurrentView = export_by_view # by model
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
    ifc_export_config.ExportUserDefinedPsetsFileName = ''
    ifc_export_config.ExportLinkedFiles = False
    ifc_export_config.IncludeSiteElevation = True
    ifc_export_config.UseActiveViewGeometry = False # by model
    ifc_export_config.ExportSpecificSchedules = False
    ifc_export_config.TessellationLevelOfDetail = 0
    ifc_export_config.StoreIFCGUID = True
    ifc_export_config.ExportRoomsInView = export_by_view # might not work in 3D views if volumes are not computed???
    ifc_export_config.UseOnlyTriangulation = False
    ifc_export_config.IncludeSteelElements = True
    ifc_export_config.COBieCompanyInfo = 'Company Name'
    ifc_export_config.COBieProjectInfo = 'Project Info'
    return ifc_export_config
