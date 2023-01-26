'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Revit ceilings helper functions.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''
#
#License:
#
#
# Revit Batch Processor Sample Code
#
# Copyright (c) 2021  Jan Christel
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

# import common library modules
from duHast.APISamples import RevitCommonAPI as com
from duHast.APISamples import RevitFamilyUtils as rFam
from duHast.APISamples import RevitGeometry as rGeo
from duHast.APISamples import RevitDesignSetOptions as rDesignO
from duHast.DataSamples import DataCeiling as dCeiling
from duHast.APISamples import RevitPhases as rPhase

# import Autodesk
import Autodesk.Revit.DB as rdb

clr.ImportExtensions(System.Linq)

# -------------------------------------------- common variables --------------------
#: header used in reports
REPORT_CEILINGS_HEADER = ['HOSTFILE', 'CEILINGTYPEID', 'CEILINGTYPENAME']
#: Built in family name for compound ceilings
COMPOUND_CEILING_FAMILY_NAME = 'Compound Ceiling'
#: Built in family name for basic ceilings
BASIC_CEILING_FAMILY_NAME = 'Basic Ceiling'
#: Built in family name for roof soffits
ROOF_SOFFIT_FAMILY_NAME = 'Roof Soffit'
#: List of all Built in ceiling family names
BUILTIN_CEILING_TYPE_FAMILY_NAMES = [
    COMPOUND_CEILING_FAMILY_NAME,
    BASIC_CEILING_FAMILY_NAME,
    ROOF_SOFFIT_FAMILY_NAME
]

# --------------------------------------------- utility functions ------------------

def GetAllCeilingTypesByCategory(doc):
    '''
    Gets a filtered element collector of all ceiling types in the model:

    - Compound Ceiling
    - In place families or loaded families
    - Basic Ceiling

    Filters by category.
    It will therefore not return any roof soffit types ..

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector containing ceiling types.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    collector = rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_Ceilings).WhereElementIsElementType()
    return collector

def GetCeilingTypesByClass(doc):
    '''
    Gets a filtered element collector of all ceiling types in the model:

    - Roof Soffit
    - Compound Ceiling
    - Basic Ceiling

    Filters by class.
    It will therefore not return any in place family types.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector containing ceiling types.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    return  rdb.FilteredElementCollector(doc).OfClass(rdb.CeilingType)

def BuildCeilingTypeDictionary(collector, dic):
    '''
    Returns the dictionary past in with keys and or values added retrieved from collector past in.

    Keys are built in ceiling family type names.

    TODO: Use more generic code.

    :param collector: A filtered element collector containing ceiling types.
    :type collector: Autodesk.Revit.DB.FilteredElementCollector
    :param dic: A dictionary containing key: ceiling type family name, value: list of ids belonging to that type.
    :type dic: dictionary (key str, value list of Autodesk.Revit.DB.ElementId)

    :return: A dictionary containing key: built in ceiling type family name, value: list of ids belonging to that type.
    :rtype: dictionary (key str, value list of Autodesk.Revit.DB.ElementId)
    '''

    for c in collector:
        if(dic.has_key(c.FamilyName)):
            if(c.Id not in dic[c.FamilyName]):
                dic[c.FamilyName].append(c.Id)
        else:
            dic[c.FamilyName] = [c.Id]
    return dic

def SortCeilingTypesByFamilyName(doc):
    '''
    Returns a dictionary of all ceiling types in the model where key is the build in wall family name, values are ids of associated wall types.

    TODO: Use more generic code.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A dictionary containing key: built in ceiling type family name, value: list of ids belonging to that type.
    :rtype: dictionary (key str, value list of Autodesk.Revit.DB.ElementId)
    '''

    # get all ceiling Type Elements
    wts = GetCeilingTypesByClass(doc)
    # get all ceiling types including in place ceiling families
    wts_two = GetAllCeilingTypesByCategory(doc)
    usedWts = {}
    usedWts = BuildCeilingTypeDictionary(wts, usedWts)
    usedWts = BuildCeilingTypeDictionary(wts_two, usedWts)
    return usedWts

# -------------------------------- none in place ceiling types -------------------------------------------------------

def GetAllCeilingInstancesInModelByCategory(doc):
    '''
    Gets all ceiling elements placed in model. Ignores roof soffits.

    Filters by category.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector containing ceiling instances.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    return rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_Ceilings).WhereElementIsNotElementType()

def GetAllCeilingInstancesInModelByClass(doc):
    '''
    Gets all ceiling elements placed in model. Ignores in place families.

    Filters by class.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector containing ceiling instances.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    return rdb.FilteredElementCollector(doc).OfClass(rdb.Ceiling).WhereElementIsNotElementType()

def GetAllCeilingTypeIdsInModelByCategory(doc):
    '''
    Gets all ceiling element type ids available in model.

    Filters by category.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector containing ceiling type ids.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    ids = []
    colCat = GetAllCeilingTypesByCategory(doc)
    ids = com.GetIdsFromElementCollector(colCat)
    return ids

def GetAllCeilingTypeIdsInModelByClass(doc):
    '''
    Gets all ceiling element type ids available in model.

    Filters by class.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    
    :return: A filtered element collector containing ceiling type ids.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    ids = []
    colClass = GetCeilingTypesByClass(doc)
    ids = com.GetIdsFromElementCollector(colClass)
    return ids

def GetUsedCeilingTypeIds(doc):
    '''
    Gets all used ceiling type ids.

    Filters by category.
    Used: at least one instance of this type is placed in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of element ids representing used ceiling types.
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    ids = com.GetUsedUnusedTypeIds(doc, GetAllCeilingTypeIdsInModelByCategory, 1)
    return ids

def FamilyNoTypesInUse(famTypeIds,unUsedTypeIds):
    '''
    Compares two lists of ids. True if any id is not in unUsedTypeIds.

    TODO: check for more generic list comparison and remove this function.

    :param famTypeIds: List of family type ids to check.
    :type famTypeIds: List of Autodesk.Revit.DB.ElementId
    :param unUsedTypeIds: Reference list of ids.
    :type unUsedTypeIds: List of Autodesk.Revit.DB.ElementId

    :return: True if any id from famTypeIds is not in unUsedTypeIds.
    :rtype: bool
    '''

    match = True
    for famTypeId in famTypeIds:
        if (famTypeId not in unUsedTypeIds):
            match = False
            break
    return match
 
def GetUnusedNonInPlaceCeilingTypeIdsToPurge(doc):
    '''
    Gets all unused ceiling type id's.
    
    - Roof Soffit
    - Compound Ceiling
    - Basic Ceiling

    This method can be used to safely delete unused ceiling types:
    In the case that no ceiling instance using any of the types is placed this will return all but one type id since\
        Revit requires at least one ceiling type definition to be in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of element ids representing not used ceiling types.
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    # get unused type ids
    ids = com.GetUsedUnusedTypeIds(doc, GetAllCeilingTypeIdsInModelByClass, 0)
    # make sure there is at least on ceiling type per system family left in model
    ceilingTypes = SortCeilingTypesByFamilyName(doc)
    for key, value in ceilingTypes.items():
        if(key in BUILTIN_CEILING_TYPE_FAMILY_NAMES):
            if(FamilyNoTypesInUse(value,ids) == True):
                # remove one type of this system family from unused list
                ids.remove(value[0])
    return ids
 
# -------------------------------- In place ceiling types -------------------------------------------------------

def GetInPlaceCeilingFamilyInstances(doc):
    '''
    Gets all instances of in place families of category ceiling.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector containing in place ceiling instances.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''
    
    filter = rdb.ElementCategoryFilter(rdb.BuiltInCategory.OST_Ceilings)
    return rdb.FilteredElementCollector(doc).OfClass(rdb.FamilyInstance).WherePasses(filter)

def GetAllInPlaceCeilingTypeIdsInModel(doc):
    '''
    Gets all type ids off all available in place families of category ceiling.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of element ids representing in place ceiling types.
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    ids = rFam.GetAllInPlaceTypeIdsInModelOfCategory(doc, rdb.BuiltInCategory.OST_Ceilings)
    return ids

def GetUsedInPlaceCeilingTypeIds(doc):
    '''
    Gets all used in place ceiling type ids in the model.

    Used: at least one instance of this type is placed in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of element ids representing used in place ceiling types.
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    ids = com.GetUsedUnusedTypeIds(doc, GetAllInPlaceCeilingTypeIdsInModel, 1)
    return ids

def GetUnusedInPlaceCeilingTypeIds(doc):
    '''
    Gets all unused in place ceiling type ids in the model.

    Unused: Not one instance of this type is placed in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of element ids representing unused in place ceiling types.
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    ids = com.GetUsedUnusedTypeIds(doc, GetAllInPlaceCeilingTypeIdsInModel, 0)
    return ids

def GetUnusedInPlaceCeilingIdsForPurge(doc):
    '''
    Gets symbol(type) ids and family ids (when no type is in use) of in place ceiling families which can be safely deleted from the model.

    This method can be used to safely delete unused in place ceiling types. There is no requirement by Revit to have at least one\
        in place ceiling definition in the model.
    
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of element ids representing unused in place ceiling types and families.
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    ids = rFam.GetUnusedInPlaceIdsForPurge(doc, GetUnusedInPlaceCeilingTypeIds)
    return ids

# -------------------------------- ceiling geometry -------------------------------------------------------

def Get2DPointsFromRevitCeiling(ceiling):
    '''
    Returns a list of lists of points representing the flattened(2D geometry) of the ceiling
    List of Lists because a ceiling can be made up of multiple sketches. Each nested list represents one ceiling sketch.
    Does not work with in place ceilings

    :param ceiling: A revit ceiling instance.
    :type ceiling: Autodesk.Revit.DB.Ceiling

    :return: A list of data geometry instances.
    :rtype: list of :class:`.DataGeometry`
    '''

    allCeilingPoints = []
    # get geometry from ceiling
    opt = rdb.Options()
    fr1_geom = ceiling.get_Geometry(opt)
    solids = []
    # check geometry for Solid elements
    # todo check for FamilyInstance geometry ( in place families!)
    for item in fr1_geom:
        if(type(item) is rdb.Solid):
            solids.append(item)
   
    # process solids to points 
    # in place families may have more then one solid
    for s in solids:
        pointPerCeilings = rGeo.ConvertSolidToFlattened2DPoints(s)
        if(len(pointPerCeilings) > 0):
            for pLists in pointPerCeilings:
                allCeilingPoints.append(pLists)
    return allCeilingPoints

def Get2DPointsFromRevitCeilingsInModel(doc):
    '''
    Returns a list of lists of points representing the flattened(2D geometry) of the ceiling
    List of Lists because a ceiling can be made up of multiple sketches. Each nested list represents one ceiling sketch.
    Does not work with in place ceilings

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A list of data geometry instances.
    :rtype: list of :class:`.DataGeometry`
    '''

    ceilingInstances =  GetAllCeilingInstancesInModelByCategory(doc)
    allCeilingPoints = []
    for cI in ceilingInstances:
       ceilingPoints = Get2DPointsFromRevitCeiling(cI)
       if(len(ceilingPoints) > 0 ):
           allCeilingPoints.append (ceilingPoints)
    return allCeilingPoints

# -------------------------------- ceiling data -------------------------------------------------------

def GetAllCeilingData(doc):
    '''
    Gets a list of ceiling data objects for each ceiling element in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A list of data ceiling instances.
    :rtype: list of :class:`.DataCeiling`
    '''

    allCeilingData = []
    ceilings = GetAllCeilingInstancesInModelByCategory(doc)
    for ceiling in ceilings:
        cd = PopulateDataCeilingObject(doc, ceiling)
        if(cd is not None):
            allCeilingData.append(cd)
    return allCeilingData


def PopulateDataCeilingObject(doc, revitCeiling):
    '''
    Returns a custom ceiling data objects populated with some data from the revit model ceiling past in.

    - ceiling id
    - ceiling type name
    - ceiling mark
    - ceiling type mark
    - ceiling level name
    - ceiling level id
    - ceiling offset from level

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param revitCeiling: A revit ceiling instance.
    :type revitCeiling: Autodesk.Revit.DB.Ceiling

    :return: A data ceiling object instance.
    :rtype: :class:`.DataCeiling`
    '''

    # set up data class object
    dataC = dCeiling.DataCeiling() 
    # get ceiling geometry (boundary points)
    revitGeometryPointGroups = Get2DPointsFromRevitCeiling(revitCeiling)
    if(len(revitGeometryPointGroups) > 0):
        ceilingPointGroupsAsDoubles = []
        for allCeilingPointGroups in revitGeometryPointGroups:
            dataGeoConverted = rGeo.ConvertXYZInDataGeometry(doc, allCeilingPointGroups)
            ceilingPointGroupsAsDoubles.append(dataGeoConverted)
        dataC.geometry = ceilingPointGroupsAsDoubles
        # get other data
        dataC.designSetAndOption = rDesignO.GetDesignSetOptionInfo(doc, revitCeiling)
        ceilingTypeId = revitCeiling.GetTypeId()
        ceilingType = doc.GetElement(ceilingTypeId)
        dataC.id = revitCeiling.Id.IntegerValue
        dataC.typeName = rdb.Element.Name.GetValue(revitCeiling).encode('utf-8')
        dataC.mark = com.GetBuiltInParameterValue(revitCeiling, rdb.BuiltInParameter.ALL_MODEL_MARK)  # need to get the mark here...
        dataC.typeMark = com.GetBuiltInParameterValue(ceilingType, rdb.BuiltInParameter.ALL_MODEL_TYPE_MARK)
        dataC.levelName = rdb.Element.Name.GetValue(doc.GetElement(revitCeiling.LevelId)).encode('utf-8')
        dataC.levelId = revitCeiling.LevelId.IntegerValue
        dataC.offsetFromLevel = com.GetBuiltInParameterValue(revitCeiling, rdb.BuiltInParameter.CEILING_HEIGHTABOVELEVEL_PARAM)   # offset from level
        # get the model name
        if(doc.IsDetached):
            dataC.modelName = 'Detached Model'
        else:
            dataC.modelName = doc.Title
        # get phasing information
        dataC.phaseCreated = rPhase.GetPhaseNameById(doc, com.GetBuiltInParameterValue(revitCeiling, rdb.BuiltInParameter.PHASE_CREATED, com.GetParameterValueAsElementId)).encode('utf-8')
        dataC.phaseDemolished = rPhase.GetPhaseNameById(doc, com.GetBuiltInParameterValue(revitCeiling, rdb.BuiltInParameter.PHASE_DEMOLISHED, com.GetParameterValueAsElementId)).encode('utf-8')
        return dataC
    else:
        return None