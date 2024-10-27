"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of lists containing loadable family categories. 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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

from Autodesk.Revit.DB import BuiltInCategory
from System.Collections.Generic import List

#: This list contains 3D element categories and is used in obsolete revit family purge function
#: any revit category commented out with note 'purged else where' can be found in list 'catsLoadableThreeDOther'
CATEGORIES_LOADABLE_3D = List[BuiltInCategory](
    [
        # BuiltInCategory.OST_CableTrayFitting,  purged else where
        BuiltInCategory.OST_Casework,
        BuiltInCategory.OST_Columns,
        BuiltInCategory.OST_CommunicationDevices,
        # BuiltInCategory.OST_ConduitFitting,  purged else where
        # BuiltInCategory.OST_CurtainWallPanels, purged else where
        BuiltInCategory.OST_DataDevices,
        # BuiltInCategory.OST_DetailComponents, purged else where
        BuiltInCategory.OST_Doors,
        # BuiltInCategory.OST_DuctAccessory,  purged else where
        # BuiltInCategory.OST_DuctTerminal, purged else where
        # BuiltInCategory.OST_DuctFitting,  purged else where
        BuiltInCategory.OST_ElectricalEquipment,
        BuiltInCategory.OST_ElectricalFixtures,
        BuiltInCategory.OST_Entourage,
        BuiltInCategory.OST_FireAlarmDevices,
        BuiltInCategory.OST_Furniture,
        BuiltInCategory.OST_FurnitureSystems,
        BuiltInCategory.OST_GenericModel,
        BuiltInCategory.OST_LightingFixtures,
        BuiltInCategory.OST_LightingDevices,
        BuiltInCategory.OST_MechanicalEquipment,
        BuiltInCategory.OST_NurseCallDevices,
        BuiltInCategory.OST_Parking,
        # BuiltInCategory.OST_PipeAccessory,  purged else where
        # BuiltInCategory.OST_PipeFitting,  purged else where
        BuiltInCategory.OST_Planting,
        BuiltInCategory.OST_PlumbingFixtures,
        # BuiltInCategory.OST_ProfileFamilies, #purged elsewhere
        BuiltInCategory.OST_SecurityDevices,
        BuiltInCategory.OST_Site,
        BuiltInCategory.OST_SpecialityEquipment,
        BuiltInCategory.OST_Sprinklers,
        # BuiltInCategory.OST_StairsRailingBaluster, #purged else where
        BuiltInCategory.OST_StructuralColumns,
        BuiltInCategory.OST_StructuralFoundation,
        BuiltInCategory.OST_StructuralFraming,
        BuiltInCategory.OST_TitleBlocks,
        BuiltInCategory.OST_TelephoneDevices,
        BuiltInCategory.OST_Windows,
    ]
)

#: Contains 3D family categories which needed specific purge code, rather then checking for unplaced family instances.
#: i.e. built in revit type settings
CATEGORIES_LOADABLE_3D_OTHER = List[BuiltInCategory](
    [
        BuiltInCategory.OST_CableTrayFitting,
        BuiltInCategory.OST_ConduitFitting,
        BuiltInCategory.OST_CurtainWallPanels,
        BuiltInCategory.OST_DetailComponents,
        BuiltInCategory.OST_DuctAccessory,
        BuiltInCategory.OST_DuctTerminal,
        BuiltInCategory.OST_DuctFitting,
        BuiltInCategory.OST_PipeAccessory,
        BuiltInCategory.OST_PipeFitting,
        BuiltInCategory.OST_ProfileFamilies,
        BuiltInCategory.OST_StairsRailingBaluster,
    ]
)

# categories which got added in Revit 2022
CATEGORIES_LOADABLE_3D_REVIT_2022 = List[BuiltInCategory]([
    BuiltInCategory.OST_FoodServiceEquipment,
    BuiltInCategory.OST_MedicalEquipment,
    BuiltInCategory.OST_FireProtection,
    BuiltInCategory.OST_VerticalCirculation,
    BuiltInCategory.OST_AudioVisualDevices,
    BuiltInCategory.OST_Signage,
    BuiltInCategory.OST_Hardscape,
    BuiltInCategory.OST_TemporaryStructure,
    BuiltInCategory.OST_Roads,
    BuiltInCategory.OST_BridgeAbutments,
    BuiltInCategory.OST_BridgeBearings,
    BuiltInCategory.OST_BridgePiers,
    BuiltInCategory.OST_BridgeCables,
    BuiltInCategory.OST_BridgeDecks,
    BuiltInCategory.OST_ExpansionJoints,
    BuiltInCategory.OST_StairsRailing,
    BuiltInCategory.OST_RailingTermination,
    BuiltInCategory.OST_RailingSupport,
])


#: This list contains 2D element categories and is used in obsolete revit family purge function.\
#: any revit category commented out with note 'purged else where' can be found in list 'catsLoadableTagsOther'
CATEGORIES_LOADABLE_TAGS = List[BuiltInCategory](
    [
        BuiltInCategory.OST_CurtainWallPanelTags,
        BuiltInCategory.OST_AreaTags,
        BuiltInCategory.OST_CaseworkTags,
        # BuiltInCategory.OST_CalloutHeads, #purged separately
        BuiltInCategory.OST_CeilingTags,
        BuiltInCategory.OST_DataDeviceTags,
        BuiltInCategory.OST_DetailComponentTags,
        BuiltInCategory.OST_DoorTags,
        BuiltInCategory.OST_DuctAccessoryTags,
        BuiltInCategory.OST_DuctFittingTags,
        BuiltInCategory.OST_DuctInsulationsTags,
        BuiltInCategory.OST_DuctLiningsTags,
        BuiltInCategory.OST_DuctTags,
        BuiltInCategory.OST_DuctTerminalTags,
        BuiltInCategory.OST_ElectricalCircuitTags,
        BuiltInCategory.OST_ElectricalEquipmentTags,
        BuiltInCategory.OST_ElectricalFixtureTags,
        # BuiltInCategory.OST_ElevationMarks, #purged separately
        BuiltInCategory.OST_FabricAreaTags,
        BuiltInCategory.OST_FabricReinforcementTags,
        BuiltInCategory.OST_FireAlarmDeviceTags,
        BuiltInCategory.OST_FlexDuctTags,
        BuiltInCategory.OST_FlexPipeTags,
        BuiltInCategory.OST_FloorTags,
        BuiltInCategory.OST_FoundationSlabAnalyticalTags,
        BuiltInCategory.OST_FurnitureTags,
        BuiltInCategory.OST_FurnitureSystemTags,
        BuiltInCategory.OST_GenericModelTags,
        # BuiltInCategory.OST_GenericAnnotation, # purged separately tricky one...some of these might be used in dimensions for instance...
        # BuiltInCategory.OST_GridHeads, # purged separately
        BuiltInCategory.OST_InternalAreaLoadTags,
        BuiltInCategory.OST_InternalLineLoadTags,
        BuiltInCategory.OST_InternalPointLoadTags,
        BuiltInCategory.OST_IsolatedFoundationAnalyticalTags,
        BuiltInCategory.OST_KeynoteTags,
        # BuiltInCategory.OST_LevelHeads, #purged separately
        BuiltInCategory.OST_LightingDeviceTags,
        BuiltInCategory.OST_LightingFixtureTags,
        BuiltInCategory.OST_LineLoadTags,
        BuiltInCategory.OST_LinkAnalyticalTags,
        BuiltInCategory.OST_MassTags,
        BuiltInCategory.OST_MaterialTags,
        BuiltInCategory.OST_MechanicalEquipmentTags,
        BuiltInCategory.OST_MEPSpaceTags,
        BuiltInCategory.OST_MultiCategoryTags,
        BuiltInCategory.OST_NodeAnalyticalTags,
        BuiltInCategory.OST_NurseCallDeviceTags,
        BuiltInCategory.OST_ParkingTags,
        BuiltInCategory.OST_PartTags,
        BuiltInCategory.OST_PathReinTags,
        BuiltInCategory.OST_PipeAccessoryTags,
        BuiltInCategory.OST_PipeFittingTags,
        BuiltInCategory.OST_PipeInsulationsTags,
        BuiltInCategory.OST_PipeTags,
        BuiltInCategory.OST_PlantingTags,
        BuiltInCategory.OST_PlumbingFixtureTags,
        BuiltInCategory.OST_RailingSystemTags,
        BuiltInCategory.OST_RebarTags,
        # BuiltInCategory.OST_ReferenceViewerSymbol, #purged separately
        BuiltInCategory.OST_RevisionCloudTags,
        BuiltInCategory.OST_RoofTags,
        BuiltInCategory.OST_RoomTags,
        # BuiltInCategory.OST_SectionHeads, #purged separately
        BuiltInCategory.OST_SecurityDeviceTags,
        BuiltInCategory.OST_SitePropertyLineSegmentTags,
        BuiltInCategory.OST_SitePropertyTags,
        BuiltInCategory.OST_SpecialityEquipmentTags,
        # BuiltInCategory.OST_SpotElevSymbols, #purged elsewhere
        BuiltInCategory.OST_SprinklerTags,
        BuiltInCategory.OST_StairsLandingTags,
        BuiltInCategory.OST_StairsRailingTags,
        BuiltInCategory.OST_StairsRunTags,
        BuiltInCategory.OST_StairsSupportTags,
        BuiltInCategory.OST_StairsTags,
        BuiltInCategory.OST_StairsTriserTags,
        BuiltInCategory.OST_StructConnectionTags,
        BuiltInCategory.OST_StructuralColumnTags,
        BuiltInCategory.OST_StructuralFoundationTags,
        BuiltInCategory.OST_StructuralFramingTags,
        BuiltInCategory.OST_StructuralStiffenerTags,
        BuiltInCategory.OST_TelephoneDeviceTags,
        BuiltInCategory.OST_TrussTags,
        # BuiltInCategory.OST_ViewportLabel, #purged elsewhere
        BuiltInCategory.OST_WallTags,
        BuiltInCategory.OST_WindowTags,
    ]
)

#: Contains 2D family categories which needed specific purge code, rather then checking for unplaced family instances
#: i.e. built in revit type settings
CATEGORIES_LOADABLE_TAGS_OTHER = List[BuiltInCategory](
    [
        BuiltInCategory.OST_CalloutHeads,
        BuiltInCategory.OST_ElevationMarks,
        BuiltInCategory.OST_GenericAnnotation,
        BuiltInCategory.OST_GridHeads,
        BuiltInCategory.OST_LevelHeads,
        BuiltInCategory.OST_ReferenceViewerSymbol,
        BuiltInCategory.OST_SectionHeads,
        BuiltInCategory.OST_SpotElevSymbols,
        BuiltInCategory.OST_ViewportLabel,
    ]
)

# categories which got added in Revit 2022
CATEGORIES_LOADABLE_TAGS_REVIT_2022 = List[BuiltInCategory]([
    BuiltInCategory.OST_FoodServiceEquipmentTags,
    BuiltInCategory.OST_MedicalEquipmentTags,
    BuiltInCategory.OST_FireProtectionTags,
    BuiltInCategory.OST_VerticalCirculationTags,
    BuiltInCategory.OST_AudioVisualDeviceTags,
    BuiltInCategory.OST_SignageTags,
    BuiltInCategory.OST_HardscapeTags,
    BuiltInCategory.OST_TemporaryStructureTags,
    BuiltInCategory.OST_RoadTags,
    BuiltInCategory.OST_BridgeBearingTags,
    BuiltInCategory.OST_BridgePierTags,
    BuiltInCategory.OST_BridgeCableTags,
    BuiltInCategory.OST_BridgeDeckTags,
    BuiltInCategory.OST_AbutmentWallTags,	
    BuiltInCategory.OST_AbutmentPileTags,
    BuiltInCategory.OST_AbutmentFoundationTags,
    BuiltInCategory.OST_ExpansionJointTags,
])
