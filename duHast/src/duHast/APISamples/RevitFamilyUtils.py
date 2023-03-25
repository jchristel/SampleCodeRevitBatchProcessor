'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Revit families helper functions.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''
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
# utility functions for most commonly used Revit API tasks
from duHast.APISamples import RevitCommonAPI as com
from duHast.APISamples import RevitElementParameterGetUtils as rParaGet
from duHast.APISamples import RevitElementParameterSetUtils as rParaSet
# utilities
from duHast.Utilities import Utility as util
# class used for stats reporting
from duHast.Utilities import Result as res
# implementation of Revit API callback required when loading families into a Revit model
from duHast.APISamples import RevitFamilyLoadOption as famLoadOpt
# load everything required from family load call back 
from duHast.APISamples.RevitFamilyLoadOption import *
from duHast.APISamples import RevitTransaction as rTran
# import Autodesk Revit DataBase namespace
import Autodesk.Revit.DB as rdb


# --------------------------------------------------- Family Loading / inserting -----------------------------------------

def LoadFamily(doc, familyFilePath):
    '''
    Loads or reloads a single family into a Revit document.
    
    Will load/ reload family provided in in path. By default the parameter values in the project file will be overwritten
    with parameter values in family.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param familyFilePath: The fully qualified file path of the family to be loaded.
    :type familyFilePath: str
    :raise: None
    
    :return: 
        Result class instance.

        - Reload status (bool) returned in result.status.
        - Reload status returned from Revit in result.message property.
        - Return family reference stored in result.result property on successful reload only
        
        On exception
        
        - Reload.status (bool) will be False
        - Reload.message will contain the exception message

    :rtype: :class:`.Result`
    '''

    result = res.Result()
    try:
        # set up load / reload action to be run within a transaction
        def action():
            # set up return value for the load / reload
            returnFamily = clr.Reference[rdb.Family]()
            actionReturnValue = res.Result()
            try:
                reloadStatus = doc.LoadFamily(
                    familyFilePath, 
                    famLoadOpt.FamilyLoadOption(), # overwrite parameter values etc
                    returnFamily)
                actionReturnValue.UpdateSep(reloadStatus,'Loaded family: ' + familyFilePath + ' :: ' + str(reloadStatus))
                if(reloadStatus):
                    actionReturnValue.result.append(returnFamily.Value)
            except Exception as e:
                actionReturnValue.UpdateSep(False,'Failed to load family ' + familyFilePath + ' with exception: '+ str(e))
            return actionReturnValue
        transaction = rdb.Transaction(doc, 'Loading Family: ' + str(util.GetFileNameWithoutExt(familyFilePath)))
        dummy = rTran.in_transaction(transaction, action)
        result.Update(dummy)
    except Exception as e:
        result.UpdateSep(False,'Failed to load families with exception: '+ str(e))
    return result


# ----------------------------------------------- filter family symbols -------------------------------------------------------

# ---------------- preset builtin category lists of categories which represent loadable families used in filtering

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

# ------------------------ filter functions -------------------------------------------------------------------------------------

def GetFamilySymbols(doc, cats):
    '''
    Filters all family symbols (Revit family types) of given built in categories from the Revit model.
    
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param cats: ICollection of Autodesk.Revit.DB.BuiltInCategory values.
    :type cats: ICollection
        :cats sample: cats = List[rdb.BuiltInCategory] ([rdb.BuiltInCategory.OST_Furniture, rdb.BuiltInCategory.OST_Parking])

    :return: A collector of Autodesk.Revit.DB.Element matching filter.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    elements = []
    try:
        multiCatFilter = rdb.ElementMulticategoryFilter(cats)
        elements = rdb.FilteredElementCollector(doc).OfClass(rdb.FamilySymbol).WherePasses(multiCatFilter).ToElements()
        return elements
    except Exception:
        return elements

def GetFamilyInstancesByBuiltInCategories(doc, cats):
    '''
    Filters all family instances of given built in categories from the Revit model.
    
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param cats: ICollection of Autodesk.Revit.DB.BuiltInCategory values:
    :type cats: ICollection
        :cats sample: cats = List[rdb.BuiltInCategory] ([rdb.BuiltInCategory.OST_Furniture, rdb.BuiltInCategory.OST_Parking])
    
    :return: A collector of Autodesk.Revit.DB.Element matching filter.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''
    
    elements = []
    try:
        multiCatFilter = rdb.ElementMulticategoryFilter(cats)
        elements = rdb.FilteredElementCollector(doc).OfClass(rdb.FamilyInstance).WherePasses(multiCatFilter).ToElements()
        return elements
    except Exception:
        return elements

def GetFamilyInstancesOfBuiltInCategory(doc, builtinCat):
    '''
    Filters all family instances of a single given built in category from the Revit model.
    
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param builtinCat: single revit builtInCategory Enum value.
    :type builtinCat: Autodesk.Revit.DB.BuiltInCategory
    
    :return: A collector of Autodesk.Revit.DB.FamilyInstance matching filter.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    filter = rdb.ElementCategoryFilter(builtinCat)
    col = rdb.FilteredElementCollector(doc).OfClass(rdb.FamilyInstance).WherePasses(filter)
    return col

def GetAllLoadableFamilies(doc):
    '''
    Filters all families in revit model by whether it is not an InPlace family.
    
    Note: slow filter due to use of lambda and cast to list.
    
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A list of families matching filter.
    :rtype: list Autodesk.Revit.DB.Family
    '''

    collector = rdb.FilteredElementCollector(doc)
    families = collector.OfClass(rdb.Family).Where(lambda e: (e.IsInPlace == False)).ToList()
    return families

def GetAllLoadableFamilyIdsThroughTypes(doc):
        '''
        Get all loadable family ids in file.

        :param doc: Current family document.
        :type doc: Autodesk.Revit.DB.Document
        :return: list of family ids
        :rtype: [Autodesk.Revit.DB.ElementId]
        '''

        familyIds = []
        col = rdb.FilteredElementCollector(doc).OfClass(rdb.FamilySymbol) 
        # get families from symbols and filter out in place families
        for famSymbol in col:
            if (famSymbol.Family.Id not in familyIds and famSymbol.Family.IsInPlace == False):
                familyIds.append(famSymbol.Family.Id)
        return familyIds

def GetAllInPlaceFamilies(doc):
    '''
    Filters all families in revit model by whether it is an InPlace family.
    
    Note: slow filter due to use of lambda and cast to list
    
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A list of families matching filter.
    :rtype: list Autodesk.Revit.DB.Family
    '''

    collector = rdb.FilteredElementCollector(doc)
    families = collector.OfClass(rdb.Family).Where(lambda e: (e.IsInPlace == True)).ToList()
    return families

def GetAllFamilyInstances(doc):
    '''
    Returns all family instances in document.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A collector with all family instances in document.
    :rtype: Autodesk.Revit.DB.Collector
    '''

    col = rdb.FilteredElementCollector(doc).OfClass(rdb.FamilyInstance)
    return col

# --------------------------family data ----------------


def IsAnyNestedFamilyInstanceLabelDriven(doc):
    '''
    Checks whether any family isntance in document is driven by the 'Label' property.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: True if at least one instance is driven by label property. Othewise False
    :rtype: bool
    '''

    flag = False
    famInstances = GetAllFamilyInstances(doc)
    
    for famInstance in famInstances:
        # get the Label parameter value
        pValue = rParaGet.get_built_in_parameter_value(
            famInstance,
            rdb.BuiltInParameter.ELEM_TYPE_LABEL,
            rParaGet.get_parameter_value_as_element_id
            )
        # a valid Element Id means family instance is driven by Label
        if (pValue != rdb.ElementId.InvalidElementId):
            flag = True
            break
            
    return flag

def GetSymbolsFromType(doc, typeIds):
    '''
    Get all family types belonging to the same family as types past in.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param typeIds: - list of element id's representing family symbols (family types)
    :type typeIds: list of Autodesk.Revit.DB.ElementId

    :return: dictionary:
        where key is the family id as Autodesk.Revit.DB.ElementId
        value is a list of all symbol(family type) ids as Autodesk.Revit.DB.ElementId belonging to the family
    :rtype: dic {Autodesk.Revit.DB.ElementId: list[Autodesk.Revit.DB.ElementId]}
    '''

    families = {}
    for tId in typeIds:
        # get family element
        typeEl = doc.GetElement(tId)
        famEl = typeEl.Family
        # check whether family was already processed
        if(famEl.Id not in families):
            # get all available family types
            sIds = famEl.GetFamilySymbolIds().ToList()
            families[famEl.Id] = sIds
    return families

def GetFamilyInstancesBySymbolTypeId(doc, typeId):
    '''
    Filters all family instances of a single given family symbol (type).
    
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param Autodesk.Revit.DB.ElementId typeId: The symbol (type) id

    :return: A collector of Autodesk.Revit.DB.FamilyInstance matching filter.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    pvpSymbol = rdb.ParameterValueProvider(rdb.ElementId( rdb.BuiltInParameter.SYMBOL_ID_PARAM ) )
    equals = rdb.FilterNumericEquals()
    idFilter = rdb.FilterElementIdRule( pvpSymbol, equals, typeId)
    elementFilter =  rdb.ElementParameterFilter( idFilter )
    collector = rdb.FilteredElementCollector(doc).WherePasses( elementFilter )
    return collector

def FamilyAllTypesInUse(famTypeIds, usedTypeIds):
    ''' 
    Checks if symbols (types) of a family are in use in a model.
    
    Check is done by comparing entries of famTypeIds with usedTypeIds.
    
    :param famTypeIds: list of symbol(type) ids of a family
    :type famTypeIds: list Autodesk.Revit.DB.ElementId
    :param  usedTypeIds: list of symbol(type) ids in use in a project
    :type usedTypeIds: list Autodesk.Revit.DB.ElementId

    :return: False if a single symbol id contained in list famTypeIds has a match in list usedTypeIds, otherwise True.
    :rtype: bool
    '''

    match = True
    for famTypeId in famTypeIds:
        if (famTypeId not in usedTypeIds):
            match = False
            break
    return match

def GetAllInPlaceTypeIdsInModelOfCategory(doc, famBuiltInCategory):
    ''' 
    Filters family symbol (type) ids off all available in place families of single given built in category.
    
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param famBuiltInCategory: built in revit category 
    :type famBuiltInCategory: Autodesk.Revit.DB.BuiltInCategory

    :return: A list of Element Ids representing the family symbols matching filter.
    :rtype: list Autodesk.Revit.DB.ElementId
    '''

    # filter model for family symbols of given built in category
    filter = rdb.ElementCategoryFilter(famBuiltInCategory)
    col = rdb.FilteredElementCollector(doc).OfClass(rdb.FamilySymbol).WherePasses(filter)
    ids = []
    for c in col:
        fam = c.Family
        # check if this an in place or loaded family!
        if (fam.IsInPlace == True):
            ids.append(c.Id)
    return ids

def GetUnusedInPlaceIdsForPurge(doc, unusedTypeGetter):
    '''
    Filters symbol(type) ids and family ids (when not a single type of given family is in use) of families.
    
    The returned list of ids can be just unused family symbols or entire families if none of their symbols are in use.
    in terms of purging its faster to delete an entire family definition rather then deleting it's symbols first and then the 
    definition.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param unusedTypeGetter: 
        A function returning ids of unused symbols (family types) as a list. 
        It requires as argument the current model document only.
    :type unusedTypeGetter: function (doc) -> list Autodesk.Revit.DB.ElementId

    :return: A list of Element Ids representing the family symbols and or family id's matching filter.
    :rtype: list Autodesk.Revit.DB.ElementId
    '''

    unusedIds = []
    unusedFamilyIds = []
    # get all unused type Ids
    unusedTypeIds = unusedTypeGetter(doc)
    # get family Elements belonging to those type ids
    families = GetSymbolsFromType(doc, unusedTypeIds)
    # check whether an entire family can be purged and if so remove their symbol(type) ids from 
    # from unusedType ids list since we will be purging the family instead
    for key, value in families.items():
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

def GetFamilySymbolsIds(doc, cats, excludeSharedFam = True):
    '''
    Filters family symbols belonging to list of built in categories past in.
    
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param ICollection cats: ICollection of Autodesk.Revit.DB.BuiltInCategory values.
    :type cats: cats = List[rdb.BuiltInCategory] ([rdb.BuiltInCategory.OST_Furniture, rdb.BuiltInCategory.OST_Parking])

    :return: A list of Element Ids representing the family symbols matching filter.
    :rtype: list Autodesk.Revit.DB.ElementId
    '''

    ids = []
    try:
        multiCatFilter = rdb.ElementMulticategoryFilter(cats)
        elements = rdb.FilteredElementCollector(doc).OfClass(rdb.FamilySymbol).WherePasses(multiCatFilter)
        for el in elements:
            # check if shared families are to be excluded from return list
            if(excludeSharedFam):
                fam = el.Family
                pValue = rParaGet.get_built_in_parameter_value(fam, rdb.BuiltInParameter.FAMILY_SHARED)
                if(pValue != None):
                    if(pValue == 'No' and el.Id not in ids):
                        ids.append(el.Id)
                else:
                    # some revit families cant be of type shared...()
                    ids.append(el.Id)
            else:
                ids.append(el.Id)
        return ids
    except Exception:
        return ids

def GetAllNonSharedFamilySymbolIds(doc):
    '''
    Filters family symbols (types) belonging to hard coded categories lists (catsLoadableThreeD, catsLoadableTags)
    
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A list of Element Ids representing the family symbols matching filter.
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    ids = []
    allLoadableThreeDTypeIds = GetFamilySymbolsIds(doc, catsLoadableThreeD)
    allLoadableTagsTypeIds = GetFamilySymbolsIds(doc, catsLoadableTags)
    ids = allLoadableThreeDTypeIds + allLoadableTagsTypeIds
    return ids

def GetUsedUnusedTypeIds(doc, typeIdGetter, useType = 0, excludeSharedFam = True):
    '''
    Filters types obtained by past in typeIdGetter method and depending on useType past in returns either the used or unused symbols of a family

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param typeIdGetter: 
        A function returning ids of symbols (family types) as a list, requires as argument: 
        the current model doc, 
        ICollection of built in categories, 
        bool: exclude shared families
    :type typeIdGetter: function (doc, ICollection, bool) -> list[Autodesk.Revit.DB.ElementId]
    :param useType: 0, no dependent elements (not used); 1: has dependent elements(is in use)
    :type useType: int

    :return: A list of Element Ids representing the family symbols matching filter.
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

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

def GetUnusedFamilyTypes(doc, excludeSharedFam = True):
    '''
    Filters unused non shared family (symbols) type ids in model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param excludeSharedFam: Default is True (exclude any shared families from filter result)
    :type excludeSharedFam: bool

    :return: A list of Element Ids representing the family symbols matching filter.
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    ids = GetUsedUnusedTypeIds(doc, GetFamilySymbolsIds, 0, excludeSharedFam)
    return ids

def GetUnusedNonSharedFamilySymbolsAndTypeIdsToPurge(doc):
    '''
    Filters unused, non shared and in place family (symbols) type ids in model which can be purged from the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    
    :return: A list of Element Ids representing the family symbols matching filter.
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    idsUnused = GetUnusedInPlaceIdsForPurge(doc, GetUnusedFamilyTypes)
    return idsUnused

# -------------------------- family elements  ----------------

#: Types of lines in family available
LINE_NAMES = [
    'Model Lines', # 3D families
    'Symbolic Lines', # 3D families
    'Line' # annotation (tag) families
    ]

def GetAllGenericFormsInFamily(doc):
    '''
    Filters all generic forms (3D extrusions) in family.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A collector of Autodesk.Revit.DB.GenericForm.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    col = rdb.FilteredElementCollector(doc).OfClass(rdb.GenericForm)
    return col

def GetAllCurveBasedElementsInFamily(doc):
    '''
    Filters all curve based elements in family.

    These are:

        - Symbolic Lines
        - Model Lines
    
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A list of Autodesk.Revit.DB.CurveElement.
    :rtype: list Autodesk.Revit.DB.CurveElement
    '''

    elements = []
    col = rdb.FilteredElementCollector(doc).OfClass(rdb.CurveElement)
    for c in col:
        if(rdb.Element.Name.GetValue(c) in LINE_NAMES):
            elements.append(c)
    return elements

def GetAllModelTextElementsInFamily(doc):
    '''
    Filters all model text elements in family.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    
    :return: A collector of Autodesk.Revit.DB.ModelText.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    
    '''

    col = rdb.FilteredElementCollector(doc).OfClass(rdb.ModelText)
    return col

def GetAllReferencePlanesInFamily(doc):
    '''
    Filters all reference planes in family.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A collector of Autodesk.Revit.DB.ReferencePlane.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    col = rdb.FilteredElementCollector(doc).OfClass(rdb.ReferencePlane)
    return col

# -------------------------- ref planes  ----------------

# doc             current document
def SetRefPlanesToNotAReference(doc):
    ''' 
    This will set any reference plane with reference type 'weak' within a family to reference type 'not a reference'.
    
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    
    :return:
        Result class instance.

        - result.status: (bool) True if at least one reference plane type was successfully changed otherwise False
        - result.message: one row entry per reference plane requiring reference type change
        - result.result: not used

    :rtype: :class:`.Result`
    '''

    '''    
    Revit API reference types and their int value:
    ('ref name ', 'Left', ' reference type as int ', 0, ' reference type as string ', 'Left')
    ('ref name ', 'Center (Left/Right)', ' reference type as int ', 1, ' reference type as string ', 'Center (Left/Right)')
    ('ref name ', 'Right', ' reference type as int ', 2, ' reference type as string ', 'Right')
    ('ref name ', 'Front', ' reference type as int ', 3, ' reference type as string ', 'Front')
    ('ref name ', 'Reference Plane', ' reference type as int ', 4, ' reference type as string ', 'Center (Front/Back)')
    ('ref name ', 'Back', ' reference type as int ', 5, ' reference type as string ', 'Back')
    ('ref name ', 'Reference Plane', ' reference type as int ', 6, ' reference type as string ', 'Bottom')
    ('ref name ', 'Reference Plane', ' reference type as int ', 7, ' reference type as string ', 'Center (Elevation)')
    ('ref name ', 'Top', ' reference type as int ', 8, ' reference type as string ', 'Top')
    ('ref name ', 'Reference Plane', ' reference type as int ', 12, ' reference type as string ', 'Not a Reference')
    ('ref name ', 'Reference Plane', ' reference type as int ', 13, ' reference type as string ', 'Strong Reference')
    ('ref name ', 'Reference Plane', ' reference type as int ', 14, ' reference type as string ', 'Weak Reference')
    
    '''

    result = res.Result()
    result.UpdateSep(True, 'Changing reference status of reference planes...')
    matchAtAll = False
    collectorRefPlanes = rdb.FilteredElementCollector(doc).OfClass(rdb.ReferencePlane)
    for refP in collectorRefPlanes:
        valueInt = rParaGet.get_built_in_parameter_value(
            refP, 
            rdb.BuiltInParameter.ELEM_REFERENCE_NAME, 
            rParaGet.get_parameter_value_as_integer)
        # check if an update is required (id is greater then 12)
        if (valueInt > 13):
            resultChange = rParaSet.set_built_in_parameter_value(
                doc, 
                refP, 
                rdb.BuiltInParameter.ELEM_REFERENCE_NAME,
                '12'
                )
            # set overall flag to indicate that at least one element was changed
            if(resultChange.status == True and matchAtAll == False):
                matchAtAll = True
            result.Update(resultChange)
    if(matchAtAll == False):
        result.status = False
        result.message = 'No reference planes found requiring reference type update'
    return result

# -------------------------- symbolic and model lines  ----------------

# doc             current document
def SetSymbolicAndModelLinesToNotAReference(doc):
    ''' 
    This will set any model or symbolic curve in a family with reference type 'weak' to reference type 'not a reference'.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    
    :return:
        Result class instance.

        - result.status: (bool) True if at least one curve reference type was successfully changed otherwise False
        - result.message: one row entry per curve element requiring reference type change
        - result.result: not used

    :rtype: :class:`.Result`
    '''
    
    '''
    Revit API
    ('ref name ', 'Model Lines', ' reference type as int ', 0, ' reference type as string ', 'Not a Reference')
    ('ref name ', 'Model Lines', ' reference type as int ', 1, ' reference type as string ', 'Weak Reference')
    ('ref name ', 'Model Lines', ' reference type as int ', 2, ' reference type as string ', 'Strong Reference')
    ('ref name ', 'Symbolic Lines', ' reference type as int ', 0, ' reference type as string ', 'Not a Reference')
    ('ref name ', 'Symbolic Lines', ' reference type as int ', 1, ' reference type as string ', 'Weak Reference')
    ('ref name ', 'Symbolic Lines', ' reference type as int ', 2, ' reference type as string ', 'Strong Reference')
    '''

    result = res.Result()
    result.UpdateSep(True, 'Changing reference status of model and symbolic curves...')
    matchAtAll = False
    curves = GetAllCurveBasedElementsInFamily(doc)
    for curve in curves:
        # get the current reference type
        valueInt = rParaGet.get_built_in_parameter_value(
            curve, 
            rdb.BuiltInParameter.ELEM_IS_REFERENCE, 
            rParaGet.get_parameter_value_as_integer)
        # check if an update is required (id equals 1)
        if (valueInt == 1):
            resultChange = rParaSet.set_built_in_parameter_value(
                doc, 
                curve, 
                rdb.BuiltInParameter.ELEM_IS_REFERENCE,
                '0'
                )
            # set overall flag to indicate that at least one element was changed
            if(resultChange.status == True and matchAtAll == False):
                matchAtAll = True
            result.Update(resultChange)
    if(matchAtAll == False):
        result.status = False
        result.message = 'No curve elements found requiring reference type update'
    return result