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
    BuiltInCategory.OST_CableTrayFitting,
    BuiltInCategory.OST_Casework,
    BuiltInCategory.OST_Columns,
    BuiltInCategory.OST_CommunicationDevices,
    BuiltInCategory.OST_ConduitFitting,
    # BuiltInCategory.OST_CurtainWallPanels, purged else where
    BuiltInCategory.OST_DataDevices,
    # BuiltInCategory.OST_DetailComponents, purged else where
    BuiltInCategory.OST_Doors,
    BuiltInCategory.OST_DuctAccessory,
    BuiltInCategory.OST_DuctTerminal,
    BuiltInCategory.OST_DuctFitting,
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
    BuiltInCategory.OST_PipeAccessory,
    BuiltInCategory.OST_PipeFitting,
    BuiltInCategory.OST_Planting,
    BuiltInCategory.OST_PlumbingFixtures,
    BuiltInCategory.OST_ProfileFamilies,
    BuiltInCategory.OST_SecurityDevices,
    BuiltInCategory.OST_Site,
    BuiltInCategory.OST_SpecialityEquipment,
    BuiltInCategory.OST_Sprinklers,
    #BuiltInCategory.OST_StairsRailingBaluster, #purged else where
    BuiltInCategory.OST_StructuralColumns,
    BuiltInCategory.OST_StructuralFoundation,
    BuiltInCategory.OST_StructuralFraming,
    BuiltInCategory.OST_TitleBlocks,
    BuiltInCategory.OST_TelephoneDevices,
    BuiltInCategory.OST_Windows
])

catsLoadableTags = List[BuiltInCategory] ([
    BuiltInCategory.OST_CurtainWallPanelTags,
    BuiltInCategory.OST_AreaTags,
    BuiltInCategory.OST_CaseworkTags,
    #BuiltInCategory.OST_CalloutHeads, #purged separately
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
    #BuiltInCategory.OST_ElevationMarks, #purged separately
    BuiltInCategory.OST_FabricAreaTags,
    BuiltInCategory.OST_FabricReinforcementTags,
    BuiltInCategory.OST_FireAlarmDeviceTags,
    BuiltInCategory.OST_FlexDuctTags,
    BuiltInCategory.OST_FlexPipeTags,
    BuiltInCategory.OST_FloorTags,
    BuiltInCategory.OST_FoundationSlabAnalyticalTags,
    BuiltInCategory.OST_FurnitureSystemTags,
    BuiltInCategory.OST_GenericModelTags,
    #BuiltInCategory.OST_GenericAnnotation, # purged separately tricky one...some of these might be used in dimensions for instance...
    #BuiltInCategory.OST_GridHeads, # purged separately
    BuiltInCategory.OST_InternalAreaLoadTags,
    BuiltInCategory.OST_InternalLineLoadTags,
    BuiltInCategory.OST_InternalPointLoadTags,
    BuiltInCategory.OST_IsolatedFoundationAnalyticalTags,
    BuiltInCategory.OST_KeynoteTags,
    #uiltInCategory.OST_LevelHeads, #purged separately
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
    #BuiltInCategory.OST_ReferenceViewerSymbol, #purged separately
    BuiltInCategory.OST_RevisionCloudTags,
    BuiltInCategory.OST_RoofTags,
    BuiltInCategory.OST_RoomTags,
    #BuiltInCategory.OST_SectionHeads, #purged separately
    BuiltInCategory.OST_SecurityDeviceTags,
    BuiltInCategory.OST_SitePropertyLineSegmentTags,
    BuiltInCategory.OST_SitePropertyTags,
    BuiltInCategory.OST_SpecialityEquipmentTags,
    BuiltInCategory.OST_SpotElevSymbols,
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
    BuiltInCategory.OST_ViewportLabel,
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

# doc:      current model document
# typeId:   symbol type id
def GetFamilyInstancesBySymbolTypeId(doc, typeId):
    """returns all instances of a given family symbol"""
    pvpSymbol = ParameterValueProvider(ElementId( BuiltInParameter.SYMBOL_ID_PARAM ) )
    equals = FilterNumericEquals()
    idFilter = FilterElementIdRule( pvpSymbol, equals, typeId)
    efilter =  ElementParameterFilter( idFilter )
    collector = FilteredElementCollector(doc).WherePasses( efilter )
    return collector

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
        fam = c.Family
        # check if this an in place or loaded family!
        if (fam.IsInPlace == True):
            ids.append(c.Id)
    return ids

# doc                   current document
# unusedTypeGetter      returns ids of unused symbols (family types)
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

# --------------------------family purge  ----------------

# doc             current document
# cats          list of builtin categories to filter by
def GetFamilySymbolsIds(doc, cats, excludeSharedFam = True):
    """"returns a list of family symbols belonging to categories passt in"""
    ids = []
    try:
        multiCatFilter = ElementMulticategoryFilter(cats)
        elements = FilteredElementCollector(doc).OfClass(FamilySymbol).WherePasses(multiCatFilter)
        for el in elements:
            if(excludeSharedFam):
                fam = el.Family
                paras = fam.GetOrderedParameters()
                for p in paras:
                    if(p.Definition.BuiltInParameter == BuiltInParameter.FAMILY_SHARED):
                        if(com.getParameterValue(p) == 'No' and el.Id not in ids):
                            ids.append(el.Id)
                        break
            else:
                ids.append(el.Id)
        return ids
    except Exception:
        return ids

# doc             current document
def GetAllNonSharedFamilySymbolIds(doc):
    """"returns a list of all non shared family symbol ids in the model based on hard coded family category lists!"""
    ids = []
    allLoadableThreeDTypeIds = GetFamilySymbolsIds(doc, catsLoadableThreeD)
    allLoadableTagsTypeIds = GetFamilySymbolsIds(doc, catsLoadableTags)
    ids = allLoadableThreeDTypeIds + allLoadableTagsTypeIds
    return ids

# doc             current document
# useTyep         0, no dependent elements; 1: has dependent elements
# typeIdGetter    list of type ids to be checked for dependent elements
def GetUsedUnusedTypeIds(doc, typeIdGetter, useType = 0, excludeSharedFam = True):
    """returns either used or unused type ids"""
    # get all types elements available
    allLoadableThreeDTypeIds = typeIdGetter(doc, catsLoadableThreeD, excludeSharedFam)
    allLoadableTagsTypeIds = typeIdGetter(doc, catsLoadableTags, excludeSharedFam)
    allTypeIds = allLoadableThreeDTypeIds + allLoadableTagsTypeIds
    ids = []
    for typeId in allTypeIds:
        type = doc.GetElement(typeId)
        hasDependents = com.HasDependentElements(doc, type)
        if(hasDependents == useType):
            ids.append(typeId)
    return ids

# doc             current document
def GetUnusedFamilyTypes(doc, excludeSharedFam = True):
    """returns all unused family type ids in model"""
    ids = GetUsedUnusedTypeIds(doc, GetFamilySymbolsIds, 0, excludeSharedFam)
    return ids

# doc             current document
def GetUnusedNonSharedFamilySymbolsAndTypeIdsToPurge(doc):
    """returns all unused non shared family types and symbol ids in model"""
    idsUnused = GetUnusedInPlaceIdsForPurge(doc, GetUnusedFamilyTypes)
    return idsUnused 
