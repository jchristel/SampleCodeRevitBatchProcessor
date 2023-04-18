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

import clr
import System



clr.AddReference('System.Core')
clr.ImportExtensions(System.Linq)
clr.AddReference('System')


# import common library
# utility functions for most commonly used Revit API tasks
from duHast.APISamples.Common import RevitElementParameterGetUtils as rParaGet
# utilities
from duHast.Utilities import FilesIO as util
# class used for stats reporting
from duHast.Utilities import Result as res
# implementation of Revit API callback required when loading families into a Revit model
from duHast.APISamples.Family import RevitFamilyLoadOption as famLoadOpt
# load everything required from family load call back 
from duHast.APISamples.Family.RevitFamilyLoadOption import *
from duHast.APISamples.Common import RevitTransaction as rTran
# import Autodesk Revit DataBase namespace
import Autodesk.Revit.DB as rdb

from duHast.APISamples.Family.Utility.LoadableFamilyCategories import CATEGORIES_LOADABLE_3D, CATEGORIES_LOADABLE_TAGS

# --------------------------------------------------- Family Loading / inserting -----------------------------------------

def load_family(doc, familyFilePath):
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
                actionReturnValue.update_sep(reloadStatus,'Loaded family: ' + familyFilePath + ' :: ' + str(reloadStatus))
                if(reloadStatus):
                    actionReturnValue.result.append(returnFamily.Value)
            except Exception as e:
                actionReturnValue.update_sep(False,'Failed to load family ' + familyFilePath + ' with exception: '+ str(e))
            return actionReturnValue
        transaction = rdb.Transaction(doc, 'Loading Family: ' + str(util.get_file_name_without_ext(familyFilePath)))
        dummy = rTran.in_transaction(transaction, action)
        result.update(dummy)
    except Exception as e:
        result.update_sep(False,'Failed to load families with exception: '+ str(e))
    return result


# ------------------------ filter functions -------------------------------------------------------------------------------------

def get_family_symbols(doc, cats):
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

def get_family_instances_by_built_in_categories(doc, cats):
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

def get_family_instances_of_built_in_category(doc, builtinCat):
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

def get_all_loadable_families(doc):
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

def get_all_loadable_family_ids_through_types(doc):
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

def get_all_in_place_families(doc):
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

def get_all_family_instances(doc):
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


def is_any_nested_family_instance_label_driven(doc):
    '''
    Checks whether any family isntance in document is driven by the 'Label' property.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: True if at least one instance is driven by label property. Othewise False
    :rtype: bool
    '''

    flag = False
    famInstances = get_all_family_instances(doc)
    
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

def get_symbols_from_type(doc, typeIds):
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

def get_family_instances_by_symbol_type_id(doc, typeId):
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

def get_all_in_place_type_ids_in_model_of_category(doc, famBuiltInCategory):
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

# --------------------------family purge  ----------------

def get_family_symbols_ids(doc, cats, excludeSharedFam = True):
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

def get_all_non_shared_family_symbol_ids(doc):
    '''
    Filters family symbols (types) belonging to hard coded categories lists (catsLoadableThreeD, catsLoadableTags)
    
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A list of Element Ids representing the family symbols matching filter.
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    ids = []
    allLoadableThreeDTypeIds = get_family_symbols_ids(doc, CATEGORIES_LOADABLE_3D)
    allLoadableTagsTypeIds = get_family_symbols_ids(doc, CATEGORIES_LOADABLE_TAGS)
    ids = allLoadableThreeDTypeIds + allLoadableTagsTypeIds
    return ids