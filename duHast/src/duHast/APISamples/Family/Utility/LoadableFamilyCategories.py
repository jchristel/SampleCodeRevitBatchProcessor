'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of lists containing loadable family categories. 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''
#
#License:
#
#
# Revit Batch Processor Sample Code
#
# Copyright (c) 2023  Jan Christel
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

import Autodesk.Revit.DB as rdb
from System.Collections.Generic import List

#: This list contains 3D element categories and is used in obsolete revit family purge function
#: any revit category commented out with note 'purged else where' can be found in list 'catsLoadableThreeDOther'
catsLoadableThreeD = List[rdb.BuiltInCategory] ([
    #rdb.BuiltInCategory.OST_CableTrayFitting,  purged else where
    rdb.BuiltInCategory.OST_Casework,
    rdb.BuiltInCategory.OST_Columns,
    rdb.BuiltInCategory.OST_CommunicationDevices,
    # rdb.BuiltInCategory.OST_ConduitFitting,  purged else where
    # rdb.BuiltInCategory.OST_CurtainWallPanels, purged else where
    rdb.BuiltInCategory.OST_DataDevices,
    # rdb.BuiltInCategory.OST_DetailComponents, purged else where
    rdb.BuiltInCategory.OST_Doors,
    #rdb.BuiltInCategory.OST_DuctAccessory,  purged else where
    #rdb.BuiltInCategory.OST_DuctTerminal, purged else where
    #rdb.BuiltInCategory.OST_DuctFitting,  purged else where
    rdb.BuiltInCategory.OST_ElectricalEquipment,
    rdb.BuiltInCategory.OST_ElectricalFixtures,
    rdb.BuiltInCategory.OST_Entourage,
    rdb.BuiltInCategory.OST_FireAlarmDevices,
    rdb.BuiltInCategory.OST_Furniture,
    rdb.BuiltInCategory.OST_FurnitureSystems,
    rdb.BuiltInCategory.OST_GenericModel,
    rdb.BuiltInCategory.OST_LightingFixtures,
    rdb.BuiltInCategory.OST_LightingDevices,
    rdb.BuiltInCategory.OST_MechanicalEquipment,
    rdb.BuiltInCategory.OST_NurseCallDevices,
    rdb.BuiltInCategory.OST_Parking,
    #rdb.BuiltInCategory.OST_PipeAccessory,  purged else where
    #rdb.BuiltInCategory.OST_PipeFitting,  purged else where
    rdb.BuiltInCategory.OST_Planting,
    rdb.BuiltInCategory.OST_PlumbingFixtures,
    #rdb.BuiltInCategory.OST_ProfileFamilies, #purged elsewhere
    rdb.BuiltInCategory.OST_SecurityDevices,
    rdb.BuiltInCategory.OST_Site,
    rdb.BuiltInCategory.OST_SpecialityEquipment,
    rdb.BuiltInCategory.OST_Sprinklers,
    #rdb.BuiltInCategory.OST_StairsRailingBaluster, #purged else where
    rdb.BuiltInCategory.OST_StructuralColumns,
    rdb.BuiltInCategory.OST_StructuralFoundation,
    rdb.BuiltInCategory.OST_StructuralFraming,
    rdb.BuiltInCategory.OST_TitleBlocks,
    rdb.BuiltInCategory.OST_TelephoneDevices,
    rdb.BuiltInCategory.OST_Windows
])

#: Contains 3D family categories which needed specific purge code, rather then checking for unplaced family instances.
#: i.e. built in revit type settings
catsLoadableThreeDOther = List[rdb.BuiltInCategory] ([
    rdb.BuiltInCategory.OST_CableTrayFitting,
    rdb.BuiltInCategory.OST_ConduitFitting,
    rdb.BuiltInCategory.OST_CurtainWallPanels,
    rdb.BuiltInCategory.OST_DetailComponents,
    rdb.BuiltInCategory.OST_DuctAccessory,
    rdb.BuiltInCategory.OST_DuctTerminal,
    rdb.BuiltInCategory.OST_DuctFitting,
    rdb.BuiltInCategory.OST_PipeAccessory,
    rdb.BuiltInCategory.OST_PipeFitting,
    rdb.BuiltInCategory.OST_ProfileFamilies,
    rdb.BuiltInCategory.OST_StairsRailingBaluster
])

#: This list contains 2D element categories and is used in obsolete revit family purge function.\
#: any revit category commented out with note 'purged else where' can be found in list 'catsLoadableTagsOther'
catsLoadableTags = List[rdb.BuiltInCategory] ([
    rdb.BuiltInCategory.OST_CurtainWallPanelTags,
    rdb.BuiltInCategory.OST_AreaTags,
    rdb.BuiltInCategory.OST_CaseworkTags,
    #rdb.BuiltInCategory.OST_CalloutHeads, #purged separately
    rdb.BuiltInCategory.OST_CeilingTags,
    rdb.BuiltInCategory.OST_DataDeviceTags,
    rdb.BuiltInCategory.OST_DetailComponentTags,
    rdb.BuiltInCategory.OST_DoorTags,
    rdb.BuiltInCategory.OST_DuctAccessoryTags,
    rdb.BuiltInCategory.OST_DuctFittingTags,
    rdb.BuiltInCategory.OST_DuctInsulationsTags,
    rdb.BuiltInCategory.OST_DuctLiningsTags,
    rdb.BuiltInCategory.OST_DuctTags,
    rdb.BuiltInCategory.OST_DuctTerminalTags,
    rdb.BuiltInCategory.OST_ElectricalCircuitTags,
    rdb.BuiltInCategory.OST_ElectricalEquipmentTags,
    rdb.BuiltInCategory.OST_ElectricalFixtureTags,
    #rdb.BuiltInCategory.OST_ElevationMarks, #purged separately
    rdb.BuiltInCategory.OST_FabricAreaTags,
    rdb.BuiltInCategory.OST_FabricReinforcementTags,
    rdb.BuiltInCategory.OST_FireAlarmDeviceTags,
    rdb.BuiltInCategory.OST_FlexDuctTags,
    rdb.BuiltInCategory.OST_FlexPipeTags,
    rdb.BuiltInCategory.OST_FloorTags,
    rdb.BuiltInCategory.OST_FoundationSlabAnalyticalTags,
    rdb.BuiltInCategory.OST_FurnitureSystemTags,
    rdb.BuiltInCategory.OST_GenericModelTags,
    #rdb.BuiltInCategory.OST_GenericAnnotation, # purged separately tricky one...some of these might be used in dimensions for instance...
    #rdb.BuiltInCategory.OST_GridHeads, # purged separately
    rdb.BuiltInCategory.OST_InternalAreaLoadTags,
    rdb.BuiltInCategory.OST_InternalLineLoadTags,
    rdb.BuiltInCategory.OST_InternalPointLoadTags,
    rdb.BuiltInCategory.OST_IsolatedFoundationAnalyticalTags,
    rdb.BuiltInCategory.OST_KeynoteTags,
    #BuiltInCategory.OST_LevelHeads, #purged separately
    rdb.BuiltInCategory.OST_LightingDeviceTags,
    rdb.BuiltInCategory.OST_LightingFixtureTags,
    rdb.BuiltInCategory.OST_LineLoadTags,
    rdb.BuiltInCategory.OST_LinkAnalyticalTags,
    rdb.BuiltInCategory.OST_MassTags,
    rdb.BuiltInCategory.OST_MaterialTags,
    rdb.BuiltInCategory.OST_MechanicalEquipmentTags,
    rdb.BuiltInCategory.OST_MEPSpaceTags,
    rdb.BuiltInCategory.OST_MultiCategoryTags,
    rdb.BuiltInCategory.OST_NodeAnalyticalTags,
    rdb.BuiltInCategory.OST_NurseCallDeviceTags,
    rdb.BuiltInCategory.OST_ParkingTags,
    rdb.BuiltInCategory.OST_PartTags,
    rdb.BuiltInCategory.OST_PathReinTags,
    rdb.BuiltInCategory.OST_PipeAccessoryTags,
    rdb.BuiltInCategory.OST_PipeFittingTags,
    rdb.BuiltInCategory.OST_PipeInsulationsTags,
    rdb.BuiltInCategory.OST_PipeTags,
    rdb.BuiltInCategory.OST_PlantingTags,
    rdb.BuiltInCategory.OST_PlumbingFixtureTags,
    rdb.BuiltInCategory.OST_RailingSystemTags,
    rdb.BuiltInCategory.OST_RebarTags,
    #rdb.BuiltInCategory.OST_ReferenceViewerSymbol, #purged separately
    rdb.BuiltInCategory.OST_RevisionCloudTags,
    rdb.BuiltInCategory.OST_RoofTags,
    rdb.BuiltInCategory.OST_RoomTags,
    #rdb.BuiltInCategory.OST_SectionHeads, #purged separately
    rdb.BuiltInCategory.OST_SecurityDeviceTags,
    rdb.BuiltInCategory.OST_SitePropertyLineSegmentTags,
    rdb.BuiltInCategory.OST_SitePropertyTags,
    rdb.BuiltInCategory.OST_SpecialityEquipmentTags,
    #rdb.BuiltInCategory.OST_SpotElevSymbols, #purged elsewhere
    rdb.BuiltInCategory.OST_SprinklerTags,
    rdb.BuiltInCategory.OST_StairsLandingTags,
    rdb.BuiltInCategory.OST_StairsRailingTags,
    rdb.BuiltInCategory.OST_StairsRunTags,
    rdb.BuiltInCategory.OST_StairsSupportTags,
    rdb.BuiltInCategory.OST_StairsTags,
    rdb.BuiltInCategory.OST_StairsTriserTags,
    rdb.BuiltInCategory.OST_StructConnectionTags,
    rdb.BuiltInCategory.OST_StructuralColumnTags,
    rdb.BuiltInCategory.OST_StructuralFoundationTags,
    rdb.BuiltInCategory.OST_StructuralFramingTags,
    rdb.BuiltInCategory.OST_StructuralStiffenerTags,
    rdb.BuiltInCategory.OST_TelephoneDeviceTags,
    rdb.BuiltInCategory.OST_TrussTags,
    #rdb.BuiltInCategory.OST_ViewportLabel, #purged elsewhere
    rdb.BuiltInCategory.OST_WallTags,
    rdb.BuiltInCategory.OST_WindowTags
])

#: Contains 2D family categories which needed specific purge code, rather then checking for unplaced family instances
#: i.e. built in revit type settings
catsLoadableTagsOther = List[rdb.BuiltInCategory] ([
    rdb.BuiltInCategory.OST_CalloutHeads,
    rdb.BuiltInCategory.OST_ElevationMarks,
    rdb.BuiltInCategory.OST_GenericAnnotation,
    rdb.BuiltInCategory.OST_GridHeads,
    rdb.BuiltInCategory.OST_LevelHeads,
    rdb.BuiltInCategory.OST_ReferenceViewerSymbol,
    rdb.BuiltInCategory.OST_SectionHeads,
    rdb.BuiltInCategory.OST_SpotElevSymbols,
    rdb.BuiltInCategory.OST_ViewportLabel
])