#
#License:
#
#
# Revit Batch Processor Sample Code
#
# Copyright (c) 2020  Jan Christel
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

clr.AddReference('System.Core')
clr.ImportExtensions(System.Linq)
clr.AddReference('System')
from System.Collections.Generic import List


# import common library
import RevitCommonAPI as com
import Utility as util
import Result as res
import RevitFamilyLoadOption as famLoadOpt
from RevitFamilyLoadOption import *

from Autodesk.Revit.DB import *

# --------------------------------------------------- Family Loading / inserting -----------------------------------------

def ModifyLoadFamilies(doc, revitFilePath, familyData):
    result = res.Result()
    try:
        for loadFam in familyData:
            # set up return value
            returnFamily = clr.StrongBox[Family]()
            def action():
                actionReturnValue = res.Result()
                try:
                    reloadStatus = doc.LoadFamily(
                        loadFam, 
                        famLoadOpt.FamilyLoadOption(), # overwrite parameter values etc
                        returnFamily)
                    actionReturnValue.UpdateSep(reloadStatus,'Loaded family: ' + loadFam + ' :: ' + str(reloadStatus))
                except Exception as e:
                    actionReturnValue.UpdateSep(False,'Failed to load family ' + loadFam + ' with exception: '+ str(e))
                return actionReturnValue
            transaction = Transaction(doc,'Loading Family')
            dummy = com.InTransaction(transaction, action)
            result.Update(dummy)
    except Exception as e:
        result.UpdateSep(False,'Failed to load families with exception: '+ str(e))
    return result


# ----------------------------------------------- filter family symbols -------------------------------------------------------

# ---------------- preset builtin category lists of categories which represent loadable families used in filtering

catsLoadableThreeD = List[BuiltInCategory] ([
    BuiltInCategory.OST_Casework,
    BuiltInCategory.OST_Columns,
    BuiltInCategory.OST_CommunicationDevices,
    BuiltInCategory.OST_DataDevices,
    BuiltInCategory.OST_DetailComponents,
    BuiltInCategory.OST_Doors,
    BuiltInCategory.OST_DuctAccessory,
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
    BuiltInCategory.OST_Planting,
    BuiltInCategory.OST_PlumbingFixtures,
    BuiltInCategory.OST_SecurityDevices,
    BuiltInCategory.OST_Site,
    BuiltInCategory.OST_SpecialityEquipment,
    BuiltInCategory.OST_Sprinklers,
    BuiltInCategory.OST_StructuralColumns,
    BuiltInCategory.OST_StructuralFoundation,
    BuiltInCategory.OST_StructuralFraming,
    BuiltInCategory.OST_TitleBlocks,
    BuiltInCategory.OST_TelephoneDevices,
    BuiltInCategory.OST_Windows,
])

catsLoadableTags = List[BuiltInCategory] ([
    BuiltInCategory.OST_CurtainWallPanelTags,
    BuiltInCategory.OST_AreaTags,
    BuiltInCategory.OST_CaseworkTags,
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
    BuiltInCategory.OST_FabricAreaTags,
    BuiltInCategory.OST_FabricReinforcementTags,
    BuiltInCategory.OST_FireAlarmDeviceTags,
    BuiltInCategory.OST_FlexDuctTags,
    BuiltInCategory.OST_FlexPipeTags,
    BuiltInCategory.OST_FloorTags,
    BuiltInCategory.OST_FoundationSlabAnalyticalTags,
    BuiltInCategory.OST_FurnitureSystemTags,
    BuiltInCategory.OST_GenericModelTags,
    BuiltInCategory.OST_GenericAnnotation,
    BuiltInCategory.OST_InternalAreaLoadTags,
    BuiltInCategory.OST_InternalLineLoadTags,
    BuiltInCategory.OST_InternalPointLoadTags,
    BuiltInCategory.OST_IsolatedFoundationAnalyticalTags,
    BuiltInCategory.OST_KeynoteTags,
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
    BuiltInCategory.OST_RevisionCloudTags,
    BuiltInCategory.OST_RoofTags,
    BuiltInCategory.OST_RoomTags,
    BuiltInCategory.OST_SecurityDeviceTags,
    BuiltInCategory.OST_SitePropertyLineSegmentTags,
    BuiltInCategory.OST_SitePropertyTags,
    BuiltInCategory.OST_SpecialityEquipmentTags,
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
    BuiltInCategory.OST_WallTags,
    BuiltInCategory.OST_WindowTags
])

# ------------------------ filter functions -------------------------------------------------------------------------------------

# returns all family symbols belonging to a list of built in categories
# cats needs to be an ICollection:
#       cats = List[BuiltInCategory] ([BuiltInCategory.OST_Furniture, BuiltInCategory.OST_Parking])

def GetFamilySymbols(doc, cats):
    elements = []
    try:
        multiCatFilter = ElementMulticategoryFilter(cats)
        elements = FilteredElementCollector(doc).OfClass(FamilySymbol).WherePasses(multiCatFilter).ToElements()
        return elements
    except Exception:
        return elements

# returns a list of in editable and not in place families
# doc   current model document
def GetAllLoadableFamilies(doc):
    collector = FilteredElementCollector(doc)
    families = collector.OfClass(Family).Where(lambda e: (e.IsInPlace == False)).ToList()
    return families

# returns a list of in place families
# doc   current model document
def GetAllInPlaceFamilies(doc):
    collector = FilteredElementCollector(doc)
    families = collector.OfClass(Family).Where(lambda e: (e.IsInPlace == True)).ToList()
    return families

# --------------------------family data ----------------

# doc   current document
# typeIds   in place family type ids available in model
def GetSymbolsFromType(doc, typeIds):
    """returns dictionary where key is the family and value are symbol(family type) ids"""
    fams = {}
    for tId in typeIds:
        # get family element
        typeEl = doc.GetElement(tId)
        famEl = typeEl.Family
        # get all available family types
        sIds = famEl.GetFamilySymbolIds().ToList()
        if(famEl.Id not in fams):
            fams[famEl.Id] = sIds
    return fams

# famTypeIds        symbol(type) ids of a family
# usedTypeIds       symbol(type) ids in use in a project
def FamilyAllTypesInUse(famTypeIds,usedTypeIds):
    """ returns true if all symbols (types) of a family are in use in a model"""
    match = True
    for famTypeId in famTypeIds:
        if (famTypeId not in usedTypeIds):
            match = False
            break
    return match

# doc   current document
def GetAllInPlaceTypeIdsInModelOfCategory(doc, famBuiltInCategory):
    """ returns type ids off all available in place families of category wall """
    filter = ElementCategoryFilter(famBuiltInCategory)
    col = FilteredElementCollector(doc).OfClass(FamilySymbol).WherePasses(filter)
    ids = []
    for c in col:
            ids.append(c.Id)
    return ids

# doc   current document
def GetUnusedInPlaceIdsForPurge(doc, unusedTypeGetter):
    """returns symbol(type) ids and family ids (when no type is in use) of in place familis of system types which can be purged"""
    unusedIds = []
    unusedFamilyIds = []
    # get all unused type Ids
    unusedTypeIds = unusedTypeGetter(doc)
    # get family Elements belonging to those type ids
    fams = GetSymbolsFromType(doc, unusedTypeIds)
    # check whether an entire family can be purged and if so remove their symbol(type) ids from 
    # from unusedType ids list since we will be purging the family instead
    for key, value in fams.items():
        if(FamilyAllTypesInUse(value, unusedTypeIds)):
            unusedFamilyIds.append(key)
            unusedTypeIds = util.RemoveItemsFromList(unusedTypeIds, value)
    # check whether entire families can be purged and if so add their ids to list to be returned
    if(len(unusedFamilyIds)>0):
        unusedIds = unusedFamilyIds + unusedTypeIds
    else:
        unusedIds = unusedTypeIds
    return unusedIds
