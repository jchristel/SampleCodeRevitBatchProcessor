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
# utility functions for most coomonly used Revit API tasks
import Utility as util
# utilities
import Result as res
# class used for stats reporting
import RevitFamilyLoadOption as famLoadOpt
# implementation of Revit API callback required when loading families into a Revit model
from RevitFamilyLoadOption import *
# load everything required from family load call back 

from Autodesk.Revit.DB import *
# import everything from Autodesk Revit DataBase namespace (Revit API)

# --------------------------------------------------- Family Loading / inserting -----------------------------------------

def ModifyLoadFamilies(doc, revitFilePath, familyData):
    '''
    reloads a number of families with settings:
    - parameter values overwritten: true

    Parameters:
    doc - current revit model document
    revitFilePath - not used (TODO: omit!)
    familyData - list 

    returns: result class instance containing reload status of each revit family (refer to LoadFamily() method for exact content)
    '''

    result = res.Result()
    try:
        for loadFam in familyData:
            resultLoad = LoadFamily(doc, loadFam)
            result.Update(resultLoad)
    except Exception as e:
        result.UpdateSep(False,'Failed to load families with exception: '+ str(e))
    return result

def LoadFamily(doc, familyFilePath):
    '''
    loads or reloads a single family with settings:
    - parameter values overwritten: true

    Parameters:
    doc - current revit model document
    familyFilePath - the fully qualified file path of the family to be loaded

    returns: result class instance 
    - reload status (bool) returned in result.status
    - reload status returned from revit in result.message property,
    - return family reference stored in result.result property on succesful reload only
    on exception:
    - reload.status is False
    - reload.message: the exception message
    '''

    result = res.Result()
    try:
        # set upo reload action
        def action():
            # set up return value
            returnFamily = clr.Reference[Autodesk.Revit.DB.Family]()
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
        transaction = Transaction(doc, 'Loading Family: ' + str(util.GetFileNameWithoutExt(familyFilePath)))
        dummy = com.InTransaction(transaction, action)
        result.Update(dummy)
    except Exception as e:
        result.UpdateSep(False,'Failed to load families with exception: '+ str(e))
    return result


# ----------------------------------------------- filter family symbols -------------------------------------------------------

# ---------------- preset builtin category lists of categories which represent loadable families used in filtering

# this list contains 3D element categories and is used in obsolete revit family purge function
# any revit category commented out with note 'purged else where' can be found in list 'catsLoadableThreeDOther'
catsLoadableThreeD = List[BuiltInCategory] ([
    #BuiltInCategory.OST_CableTrayFitting,  purged else where
    BuiltInCategory.OST_Casework,
    BuiltInCategory.OST_Columns,
    BuiltInCategory.OST_CommunicationDevices,
    # BuiltInCategory.OST_ConduitFitting,  purged else where
    # BuiltInCategory.OST_CurtainWallPanels, purged else where
    BuiltInCategory.OST_DataDevices,
    # BuiltInCategory.OST_DetailComponents, purged else where
    BuiltInCategory.OST_Doors,
    #BuiltInCategory.OST_DuctAccessory,  purged else where
    #BuiltInCategory.OST_DuctTerminal, purged else where
    #BuiltInCategory.OST_DuctFitting,  purged else where
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
    #BuiltInCategory.OST_PipeAccessory,  purged else where
    #BuiltInCategory.OST_PipeFitting,  purged else where
    BuiltInCategory.OST_Planting,
    BuiltInCategory.OST_PlumbingFixtures,
    #BuiltInCategory.OST_ProfileFamilies, #purged elsewhere
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

# contains 3D family categories which needed specific purge code, rather then checking for unplaced family instances
# i.e. built in revit type settings
catsLoadableThreeDOther = List[BuiltInCategory] ([
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
    BuiltInCategory.OST_StairsRailingBaluster
])

# this list contains 2D element categories and is used in obsolete revit family purge function
# any revit category commented out with note 'purged else where' can be found in list 'catsLoadableTagsOther'
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
    #BuiltInCategory.OST_SpotElevSymbols, #purged elsewhere
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
    #BuiltInCategory.OST_ViewportLabel, #purged elsewhere
    BuiltInCategory.OST_WallTags,
    BuiltInCategory.OST_WindowTags
])

# contains 2D family categories which needed specific purge code, rather then checking for unplaced family instances
# i.e. built in revit type settings
catsLoadableTagsOther = List[BuiltInCategory] ([
    BuiltInCategory.OST_CalloutHeads,
    BuiltInCategory.OST_ElevationMarks,
    BuiltInCategory.OST_GenericAnnotation,
    BuiltInCategory.OST_GridHeads,
    BuiltInCategory.OST_LevelHeads,
    BuiltInCategory.OST_ReferenceViewerSymbol,
    BuiltInCategory.OST_SectionHeads,
    BuiltInCategory.OST_SpotElevSymbols,
    BuiltInCategory.OST_ViewportLabel
])

# ------------------------ filter functions -------------------------------------------------------------------------------------

def GetFamilySymbols(doc, cats):
    '''
    Filters all family symbols (revit family types) of given built in categories from the revit model
    
    Parameters:
    doc - current model document
    cats - needs to be an ICollection:
    cats sample: cats = List[BuiltInCategory] ([BuiltInCategory.OST_Furniture, BuiltInCategory.OST_Parking])
    
    returns revit collector of revit elements matching filter
    '''

    elements = []
    try:
        multiCatFilter = ElementMulticategoryFilter(cats)
        elements = FilteredElementCollector(doc).OfClass(FamilySymbol).WherePasses(multiCatFilter).ToElements()
        return elements
    except Exception:
        return elements

def GetFamilyInstancesByBuiltInCategories(doc, cats):
    '''
    Filters all family instances of given built in categories from the revit model
    
    Parameters:
    doc - current model document
    cats - needs to be an ICollection:
    cats sample: cats = List[BuiltInCategory] ([BuiltInCategory.OST_Furniture, BuiltInCategory.OST_Parking])
    
    returns revit collector of revit elements matching filter
    '''
    
    elements = []
    try:
        multiCatFilter = ElementMulticategoryFilter(cats)
        elements = FilteredElementCollector(doc).OfClass(FamilyInstance).WherePasses(multiCatFilter).ToElements()
        return elements
    except Exception:
        return elements

def GetFamilyInstancesOfBuiltInCategory(doc, builtinCat):
    '''
    Filters all family instances of a single given built in category from the revit model
    
    Parameters:
    doc - current model document
    builtinCat - single revit builInCategory Enum value
    
    returns revit collector of revit elements matching filter
    '''

    filter = ElementCategoryFilter(builtinCat)
    col = FilteredElementCollector(doc).OfClass(FamilyInstance).WherePasses(filter)
    return col

def GetAllLoadableFamilies(doc):
    '''
    Filters all families in revit model by whether it is not an InPlace family
    (note: slow filter due to use of lambda and cast to list)
    
    Parameters:
    doc - current model document
    
    returns a list of revit family objects matching filter
    '''

    collector = FilteredElementCollector(doc)
    families = collector.OfClass(Family).Where(lambda e: (e.IsInPlace == False)).ToList()
    return families

def GetAllInPlaceFamilies(doc):
    '''
    Filters all families in revit model by whether it is an InPlace family
    (note: slow filter due to use of lambda and cast to list)
    
    Parameters:
    doc - current model document
    
    returns a list of revit family objects matching filter
    '''
    collector = FilteredElementCollector(doc)
    families = collector.OfClass(Family).Where(lambda e: (e.IsInPlace == True)).ToList()
    return families

# --------------------------family data ----------------

def GetSymbolsFromType(doc, typeIds):
    '''
    Get all family types belonging to the same family as types passt in

    Parameters:
    doc - current model document
    typeIds - list of element id's representing family symbols (fmaily types)
    
    returns dictionary where key is the family id and value is a list of all symbol(family type) ids belonging to the family
    '''

    fams = {}
    for tId in typeIds:
        # get family element
        typeEl = doc.GetElement(tId)
        famEl = typeEl.Family
        # check whether family was already processed
        if(famEl.Id not in fams):
            # get all available family types
            sIds = famEl.GetFamilySymbolIds().ToList()
            fams[famEl.Id] = sIds
    return fams

def GetFamilyInstancesBySymbolTypeId(doc, typeId):
    '''
    Filters all family instances of a single given family symbol (type)
    
    Parameters:
    doc - current model document
    typeId - symbol (type) id
    
    returns revit collector of revit family symbols (types) matching filter
    '''

    pvpSymbol = ParameterValueProvider(ElementId( BuiltInParameter.SYMBOL_ID_PARAM ) )
    equals = FilterNumericEquals()
    idFilter = FilterElementIdRule( pvpSymbol, equals, typeId)
    efilter =  ElementParameterFilter( idFilter )
    collector = FilteredElementCollector(doc).WherePasses( efilter )
    return collector

def FamilyAllTypesInUse(famTypeIds, usedTypeIds):
    ''' 
    checks if symbols (types) of a family are in use in a model
    
    Parameters:
    famTypeIds - list of symbol(type) ids of a family
    usedTypeIds - list of symbol(type) ids in use in a project
    
    returns False if a single symbol id  contained in list famTypeIds has a match in list usedTypeIds otherwise True
    '''

    match = True
    for famTypeId in famTypeIds:
        if (famTypeId not in usedTypeIds):
            match = False
            break
    return match

def GetAllInPlaceTypeIdsInModelOfCategory(doc, famBuiltInCategory):
    ''' 
    Filters family symbol (type) ids off all available in place families of single given built in category
    
    Parameters:
    doc - current model document
    famBuiltInCategory - built in revit category 
    
    returns list of revit family symbol (type) id's matching filter
    '''

    # filter model for family symbols of given built in category
    filter = ElementCategoryFilter(famBuiltInCategory)
    col = FilteredElementCollector(doc).OfClass(FamilySymbol).WherePasses(filter)
    ids = []
    for c in col:
        fam = c.Family
        # check if this an in place or loaded family!
        if (fam.IsInPlace == True):
            ids.append(c.Id)
    return ids

def GetUnusedInPlaceIdsForPurge(doc, unusedTypeGetter):
    '''
    filters symbol(type) ids and family ids (when not a single type of given family is in use) of families.
    Since these are not in juse they can be purged

    Parameters:
    doc - current model document
    unusedTypeGetter - function returning ids of unused symbols (family types) as a list, requires as argument the current model doc only

    returns list of revit family symbol (type) id's and or family id's matching filter
    '''

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

def GetFamilySymbolsIds(doc, cats, excludeSharedFam = True):
    '''
    filters family symbols belonging to categories passt in
    
    Parameters:
    doc - current model document
    cats - list of builtin categories to filter by, needs to be an ICollection:
    cats sample: cats = List[BuiltInCategory] ([BuiltInCategory.OST_Furniture, BuiltInCategory.OST_Parking])
    excludeSharedFam - bool: default is True (exclude any shared families from filter result)
    
    returns list of id's of family symbols (types) matching filter
    '''

    ids = []
    try:
        multiCatFilter = ElementMulticategoryFilter(cats)
        elements = FilteredElementCollector(doc).OfClass(FamilySymbol).WherePasses(multiCatFilter)
        for el in elements:
            # check if shared fams are to be excluded from return list
            if(excludeSharedFam):
                fam = el.Family
                pValue = com.GetBuiltInParameterValue(fam, BuiltInParameter.FAMILY_SHARED)
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
    filters family symbols (types) belonging to hard coded categories lists (catsLoadableThreeD, catsLoadableTags)
    
    Parameters:
    doc - current model document

    returns list of id's of family symbols (types) matching filter
    '''

    ids = []
    allLoadableThreeDTypeIds = GetFamilySymbolsIds(doc, catsLoadableThreeD)
    allLoadableTagsTypeIds = GetFamilySymbolsIds(doc, catsLoadableTags)
    ids = allLoadableThreeDTypeIds + allLoadableTagsTypeIds
    return ids

def GetUsedUnusedTypeIds(doc, typeIdGetter, useType = 0, excludeSharedFam = True):
    '''
    filers types obtained by passt in typeIdGetter method and depending on useType passt in returns eiteher the used or unsed symbols of a family

    Parameters:
    doc - current model document
    typeIdGetter -  function returning ids of symbols (family types) as a list, requires as argument: 
        the current model doc, ICollection of built in categories, bool: exclude shared families
    useType - int: 0, no dependent elements (not used); 1: has dependent elements(is in use)
    
    returns list of id's of family symbols (types) matching filter
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
    filters unused non shared family (symbols) type ids in model

    Parameters:
    doc - current model document
    excludeSharedFam - bool: default is True (exclude any shared families from filter result)

    returns list of family symbol (type) id's
    '''

    ids = GetUsedUnusedTypeIds(doc, GetFamilySymbolsIds, 0, excludeSharedFam)
    return ids

def GetUnusedNonSharedFamilySymbolsAndTypeIdsToPurge(doc):
    '''
    filters unused non shared and in place family (symbols) type ids in model

    Parameters:
    doc - current model document
    
    returns list of family symbol (type) id's
    '''

    idsUnused = GetUnusedInPlaceIdsForPurge(doc, GetUnusedFamilyTypes)
    return idsUnused

# -------------------------- family elements  ----------------

# types of lines in family available
LINE_NAMES = ['Model Lines', 'Symbolic Lines']

def GetAllGenericFormsInFamily(doc):
    '''
    filters all generic forms (3D extrusions) in family

    Parameters:
    doc - current model document

    returns revit collector of revit API GenericForm objects
    '''

    col = FilteredElementCollector(doc).OfClass(GenericForm)
    return col

def GetAllCurveBasedElementsInFamily(doc):
    '''
    filters all curve based elements in family with name:
    - Symbolic Lines
    - Model Lines
    
    Parameters:
    doc - current model document

    returns list of revit API CurveElement objects
    '''

    elements = []
    col = FilteredElementCollector(doc).OfClass(CurveElement)
    for c in col:
        if(Element.Name.GetValue(c) in LINE_NAMES):
            elements.append(c)
    return elements

def GetAllModelTextElementsInFamily(doc):
    '''
    filters all model text elements in family

    Parameters:
    doc - current model document
    
    returns revit collector of revit API ModelText objects
    '''

    col = FilteredElementCollector(doc).OfClass(ModelText)
    return col

# -------------------------- ref planes  ----------------

# doc             current document
def SetRefPlanesToNotAReference(doc):
    ''' 
    Method will set any reference plane with reference type 'weak' within a family to reference type 'not a reference'
    
    Parameters:
    doc - current model document
    
    returns: result class instance 
    - result.status: (bool) True if at least one reference plane type was successfully changed oherwise False
    - result.message: one row entry per reference plane requiring reference type change
    - result.result: not used
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
    collectorRefPlanes = FilteredElementCollector(doc).OfClass(ReferencePlane)
    for refP in collectorRefPlanes:
        valueInt = com.GetBuiltInParameterValue(
            refP, 
            BuiltInParameter.ELEM_REFERENCE_NAME, 
            com.GetParameterValueAsInteger)
        # check if an update is required (id is greater then 12)
        if (valueInt > 13):
            resultChange = com.SetBuiltInParameterValue(
                doc, 
                refP, 
                BuiltInParameter.ELEM_REFERENCE_NAME,
                '12'
                )
            # set overall flag to indicate that at leasst one element was changed
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
    Method will set any model or symbolic curve in a family with reference type 'weak' to reference type 'not a reference'

    Parameters:
    doc - current model document
    
    returns: result class instance 
    - result.status: (bool) True if at least one curve reference type was successfully changed oherwise False
    - result.message: one row entry per curve element requiring reference type change
    - result.result: not used
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
        valueInt = com.GetBuiltInParameterValue(
            curve, 
            BuiltInParameter.ELEM_IS_REFERENCE, 
            com.GetParameterValueAsInteger)
        # check if an update is required (id equals 1)
        if (valueInt == 1):
            resultChange = com.SetBuiltInParameterValue(
                doc, 
                curve, 
                BuiltInParameter.ELEM_IS_REFERENCE,
                '0'
                )
            # set overall flag to indicate that at leasst one element was changed
            if(resultChange.status == True and matchAtAll == False):
                matchAtAll = True
            result.Update(resultChange)
    if(matchAtAll == False):
        result.status = False
        result.message = 'No curve elements found requiring reference type update'
    return result