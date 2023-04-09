'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Revit category helper functions.
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
from System.Collections.Generic import List

from duHast.APISamples.Common import RevitDeleteElements as rDel
from duHast.Utilities import Result as res
from duHast.APISamples.Common import RevitTransaction as rTran

import Autodesk.Revit.DB as rdb
from duHast.APISamples.Categories.RevitFamilySubCategories import CreateNewCategoryFromSavedProperties
from duHast.APISamples.Categories.Utility.RevitCategoryPropertiesGetUtils import GetCategoryGraphicStyleIds, GetCategoryProperties
from duHast.APISamples.Categories.Utility.RevitElementsByCategoryUtils import GetElementsByCategory, MoveElementsToCategory

#: subcategory renaming sampled dictionary
#: key is the current subcategory name, value is the new subcategory name 
CAT_RENAMING = {
    'Clearance Zones': 'AMAZING'
}

#: list of built in parameters attached to family elements containing subcategory ids
ELEMENTS_PARAS_SUB = [
    rdb.BuiltInParameter.FAMILY_CURVE_GSTYLE_PLUS_INVISIBLE,
    rdb.BuiltInParameter.FAMILY_CURVE_GSTYLE_PLUS_INVISIBLE_MINUS_ANALYTICAL,
    rdb.BuiltInParameter.FAMILY_ELEM_SUBCATEGORY,
    rdb.BuiltInParameter.CLINE_SUBCATEGORY
]

def GetMainSubCategories(doc):
    '''
    Returns all subcategories of the family category in a dictionary where\
        key: sub category name
        value: sub category 

    :param doc: Current Revit family document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A dictionary.
    :rtype: dictionary {str: Autodesk.Revit.DB.Category}
    '''

    catData = {}
    # get the family category
    familyCategoryName = doc.OwnerFamily.FamilyCategory.Name
    # get all subcategories in Document
    for mainCat in doc.Settings.Categories:
        # find the category matching this docs category
        # to ensure default subcategories with an id less then 0 are also extracted
        if (mainCat.Name == familyCategoryName):
            # loop over all sub categories
            for subCat in mainCat.SubCategories:
                catData[subCat.Name] = subCat
    return catData

def DoesMainSubCategoryExists(doc, subCatName):
    '''
    Checks whether a given subcategory exists in the family.

    Note: Only subcategory directly belonging to the family category will be checked for a match.

    :param doc: Current Revit family document.
    :type doc: Autodesk.Revit.DB.Document
    :param subCatName: The name of the subcategory to be checked against.
    :type subCatName: str

    :return: True if subcategory exists in family, otherwise False
    :rtype: bool
    '''

    # get all sub categories belonging to family category
    subCats = GetMainSubCategories(doc)
    if(subCatName in subCats):
        return True
    else:
        return False

def DeleteMainSubCategory(doc, subCatName):
    '''
    Deletes a given subcategory from the family.

    Note: Only subcategory directly belonging to the family category will be checked for a match.

    ::param doc: Current Revit family document.
    :type doc: Autodesk.Revit.DB.Document
    :param subCatName: The name of the subcategory to be deleted.
    :type subCatName: str

    :return: True if subcategory exists in family and was deleted successfully, otherwise False
    :rtype: bool
    '''

    # get all sub categories belonging to family category
    subCats = GetMainSubCategories(doc)
    if(subCatName in subCats):
        # delete subcategory
        statusDelete = rDel.DeleteByElementIds(
            doc,
            [subCats[subCatName].Id],
            'delete subcategory: ' + subCatName,
            'subcategory'
        )
        return statusDelete.status
    else:
        return False


def GetFamilyCategory(doc):
    '''
    Gets the family category in a dictionary where\
        key: category name
        value: category 

    :param doc: Current Revit family document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A dictionary.
    :rtype: dictionary {str: Autodesk.Revit.DB.Category}
    '''

    catData = {}
    # get the family category
    currentFamCat = doc.OwnerFamily.FamilyCategory
    catData [currentFamCat.Name] = currentFamCat
    return catData

def GetOtherSubCategories(doc):
    '''
    Returns all family subcategories which do not belong to the actual family category.

    key: category name
    value: dictionary : key sub cat name, value: subcategory

    Note: custom subcategories have an Id greater 0
    
    :param doc: Current Revit family document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A dictionary.
    :rtype: dictionary {str: {str:Autodesk.Revit.DB.Category} }
    '''

    catData = {}
    # get the family category
    familyCategoryName = doc.OwnerFamily.FamilyCategory.Name
    # get all subcategories in Document
    for mainCat in doc.Settings.Categories:
        # find the category not matching this docs category
        # to ensure default subcategories with an id less then 0 are also extracted
        if (mainCat.Name != familyCategoryName):
            if (mainCat.Name not in catData):
                catData[mainCat.Name] = {}
            # loop over all sub categories
            for subCat in mainCat.SubCategories:
                catData[mainCat.Name][subCat.Name] = subCat
              
    return catData

def GetOtherCustomSubCategories(doc):
    '''
    Returns all family custom subcategories which do not belong to the actual family category.
    Custom categories have an Id greater then 0.

    key: category name
    value: dictionary : key sub cat name, value: subcategory

    Note: custom subcategories have an Id greater 0
    
    :param doc: Current Revit family document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A dictionary.
    :rtype: dictionary {str: {str:Autodesk.Revit.DB.Category} }
    '''

    catData = {}
    # get the family category
    familyCategoryName = doc.OwnerFamily.FamilyCategory.Name
    # get all subcategories in Document
    for mainCat in doc.Settings.Categories:
        # find the category not matching this docs category
        # to ensure default subcategories with an id less then 0 are also extracted
        if (mainCat.Name != familyCategoryName):
            if (mainCat.Name not in catData):
                catData[mainCat.Name] = {}
            # loop over all sub categories
            for subCat in mainCat.SubCategories:
                if(subCat.Id.IntegerValue > 0):
                    catData[mainCat.Name][subCat.Name] = subCat
    return catData

def GetOtherCategories(doc):
    '''
    Returns all family pre defined categories which do not belong to the actual family category.

    :param doc: Current Revit family document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A list of categories.
    :rtype: [Autodesk.Revit.DB.Category]
    '''

    catData = []
    # get the family category
    familyCategoryName = doc.OwnerFamily.FamilyCategory.Name
    # get all subcategories in Document
    for mainCat in doc.Settings.Categories:
        # find the category not matching this docs category
        # to ensure default subcategories with an id less then 0 are also extracted
        if (mainCat.Name != familyCategoryName):
            if (mainCat not in catData):
                catData.append(mainCat)
    return catData

def GetCategoryByBuiltInDefName(doc, builtInDefs):
    '''
    Returns categories by their built in definition 

    :param doc: Current Revit family document.
    :type doc: Autodesk.Revit.DB.Document
    :param builtInDefs: list of BuiltInCategory Enumeration values
    :type builtInDefs: [Autodesk.Revit.DB.BuiltInCategory]

    :return: list of categories
    :rtype: [Autodesk.Revit.DB.Category]
    '''

    cats = []
    documentSettings = doc.Settings
    groups = documentSettings.Categories
    for builtInDef in builtInDefs:
        cat = groups.get_Item(builtInDef)
        if cat!=None:
            cats.append(cat)
    return cats
   
def SetFamilyCategory(doc, newCategoryName):
    '''
    Changes the family category to new one specified by name.
    
    :param doc: Current Revit family document.
    :type doc: Autodesk.Revit.DB.Document
    :param newCategoryName: The name of the new family category.
    :type newCategoryName: str
    
    :return: True only if the category was changed successfully. Any other case False! (That includes situations when the family is already of the new category)
    :rtype: bool
    '''
    
    returnValue = res.Result()
    cat = doc.OwnerFamily.FamilyCategory
    if (cat.Name != newCategoryName):
        if (doc.Settings.Categories.Contains(newCategoryName)):
            def action():
                doc.OwnerFamily.FamilyCategory = doc.Settings.Categories.get_Item(newCategoryName)
            transaction = rdb.Transaction(doc,'Changing family category to:' + str(newCategoryName))
            changeCat = rTran.in_transaction(transaction, action)
            if(changeCat.status):
                returnValue.UpdateSep(True, 'Successfully changed family category to: '+str(newCategoryName))
            else:
                returnValue.Update(changeCat)
        else:
            returnValue.UpdateSep(False, 'Invalid Category name supplied: ' + str(newCategoryName))
    else:
        returnValue.UpdateSep(False, 'Family is already of category: '+str(newCategoryName))
    return returnValue
   
# --------------------------------------- family category  --------------------------------------------------------------

def ChangeFamilyCategory(doc, newCategoryName):
    '''
    Changes the current family category to the new one specified.

    Revit's default behavior when changing the category of a family is to discard all custom subcategories created and assign elements which are on those custom subcategories\
        to the new family category.
    
    This function will also re-create any user created subcategories under the new category and assign elements to it to match the subcategory they where on before\
         the category change.

    :param doc: Current Revit family document.
    :type doc: Autodesk.Revit.DB.Document
    :param newCategoryName: The new family category
    :type newCategoryName: str

    :return: 
        Result class instance.

        - result.status. True if all custom subcategories where re-created under the new family category and elements where moved to those subcategories, otherwise False.
        - result.message will confirm successful creation of subcategories and element move.
        - result.result empty list
        
        On exception:
        
        - result.status (bool) will be False.
        - result.message will contain generic exception message.
        - result.result will be empty
        
    :rtype: :class:`.Result`
    '''

    returnValue = res.Result()
    # get sub categories in family
    subCats = GetMainSubCategories (doc)
    
    # get all elements on custom subcategories
    elements = {}
    for subCat in subCats:
        el = GetElementsByCategory(doc, subCats[subCat])
        elements[subCat] = el
    
    # get properties of all custom sub categories
    props = {}
    for subCat in subCats:
        prop = GetCategoryProperties(subCats[subCat], doc)
        props[subCat] = prop
    
    # change family category
    changeFam = SetFamilyCategory(doc, newCategoryName)
    returnValue.Update(changeFam)

    if(changeFam.status):
        # re-create custom sub categories
        for subCat in subCats:
            # only re-create custom sub categories (id greater then 0)
            if(subCats[subCat].Id.IntegerValue > 0):
                # create new sub categories with flag: ignore if cut graphic style is missing set to true!
                createCat = CreateNewCategoryFromSavedProperties(doc, subCat, props[subCat], True)
                returnValue.Update(createCat)
                if(createCat.status):
                    # get the graphic style ids of the new subcategory for elements to use
                    destinationCatIds = GetCategoryGraphicStyleIds(createCat.result)
                    # move elements back onto custom subcategories
                    moveEl = MoveElementsToCategory(doc, elements[subCat], subCat, destinationCatIds)
                    returnValue.Update(moveEl)
                else:
                    returnValue.Update(createCat)
    else:
        returnValue.UpdateSep(False, 'Failed to change family category:' + changeFam.message)
    return returnValue