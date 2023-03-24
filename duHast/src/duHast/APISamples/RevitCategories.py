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

from duHast.APISamples import RevitCommonAPI as com
from duHast.APISamples import RevitElementParameterGetUtils as rParaGet
from duHast.APISamples import RevitElementParameterSetUtils as rParaSet
from duHast.APISamples import RevitFamilyUtils as rFamUtils
from duHast.APISamples import RevitLinks as rLink
from duHast.Utilities import Result as res
from duHast.APISamples import RevitLineStylesPatterns as rPat
from duHast.APISamples import RevitTransaction as rTran

import Autodesk.Revit.DB as rdb

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


#-------------------------- get category properties ---------------------------------

#: category properties dictionary key names and default values
#: material name
PROPERTY_MATERIAL_NAME = 'MaterialName'
#: material name default value
PROPERTY_MATERIAL_NAME_VALUE_DEFAULT = 'None'
#: material id
PROPERTY_MATERIAL_ID = 'MaterialId'

#: line weight projection name
PROPERTY_LINE_WEIGHT_PROJECTION_NAME = 'LineWeightProjection'
#: line weight cut name
PROPERTY_LINE_WEIGHT_CUT_NAME = 'LineWeightCut'

#: line colour red name
PROPERTY_LINE_COLOUR_RED_NAME = 'Red'
#: line colour green name
PROPERTY_LINE_COLOUR_GREEN_NAME = 'Green'
#: line colour blue name
PROPERTY_LINE_COLOUR_BLUE_NAME = 'Blue'


#: graphic styles used for elements in families
#: graphic style projection name
CATEGORY_GRAPHIC_STYLE_PROJECTION = 'Projection'
#: graphic style cut name
CATEGORY_GRAPHIC_STYLE_CUT = 'Cut'
#: graphic style 3D name
CATEGORY_GRAPHIC_STYLE_3D = '3D'


# -------------------------------------------- common variables --------------------
#: Header used in report files
REPORT_CATEGORIES_HEADER = [
    'HOSTFILE', 
    'FAMILY CATEGORY',
    'MAINCATEGORYNAME', 
    'SUBCATEGORYNAME',
    'CATEGORYID',
    PROPERTY_MATERIAL_NAME.upper(), 
    PROPERTY_MATERIAL_ID.upper(), 
    rPat.PROPERTY_PATTERN_NAME.upper(), 
    rPat.PROPERTY_PATTERN_ID.upper(), 
    PROPERTY_LINE_WEIGHT_PROJECTION_NAME.upper(), 
    PROPERTY_LINE_WEIGHT_CUT_NAME.upper(), 
    PROPERTY_LINE_COLOUR_RED_NAME.upper(), 
    PROPERTY_LINE_COLOUR_GREEN_NAME.upper(), 
    PROPERTY_LINE_COLOUR_BLUE_NAME.upper(),
    CATEGORY_GRAPHIC_STYLE_3D.upper(), 
    CATEGORY_GRAPHIC_STYLE_PROJECTION.upper(), 
    CATEGORY_GRAPHIC_STYLE_CUT.upper() 
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
        statusDelete = com.DeleteByElementIds(
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

def GetCategoryGraphicStyleIds(cat):
    '''
    Returns a dictionary with keys: Projection, Cut, 3D and their respective ids
    
    :param cat: A category.
    :type cat: Autodesk.REvit.DB.Category
    
    :return: A dictionary
    :rtype: dictionary {str: Autodesk.Revit.DB.ElementId}
    '''

    iDGraphicStyleProjection = cat.GetGraphicsStyle(rdb.GraphicsStyleType.Projection).Id
    
    # check if this category has a cut style ( some families always appear in elevation only!)
    graphicStyleCut = cat.GetGraphicsStyle(rdb.GraphicsStyleType.Cut)
    # set as default invalid element id
    iDGraphicStyleCut = rdb.ElementId.InvalidElementId
    if(graphicStyleCut != None):
        iDGraphicStyleCut = cat.GetGraphicsStyle(rdb.GraphicsStyleType.Cut).Id
    # build category dictionary where key is the style type, values is the corresponding Id
    dic = {}
    dic[CATEGORY_GRAPHIC_STYLE_PROJECTION] = iDGraphicStyleProjection 
    dic[CATEGORY_GRAPHIC_STYLE_CUT] = iDGraphicStyleCut
    dic[CATEGORY_GRAPHIC_STYLE_3D] = cat.Id
    return dic

def GetCategoryMaterial(cat):
    '''
    Returns the material properties name and id as a dictionary where key is property name and\
         value the property id.

    :param cat: A category.
    :type cat: Autodesk.REvit.DB.Category

    :return: A dictionary
    :rtype: dictionary {str: Autodesk.Revit.DB.ElementId}\
        If no material is assigned to a category it will return {'None: Autodesk.Revit.DB.ElementId.InvalidElementId}
    '''

    dicMaterial = {}
    dicMaterial[PROPERTY_MATERIAL_NAME] = PROPERTY_MATERIAL_NAME_VALUE_DEFAULT
    dicMaterial[PROPERTY_MATERIAL_ID] = rdb.ElementId.InvalidElementId
    material = cat.Material
    if(material != None):
        dicMaterial[PROPERTY_MATERIAL_NAME] = rdb.Element.Name.GetValue(material)
        dicMaterial[PROPERTY_MATERIAL_ID] = material.Id
    return dicMaterial

def GetCategoryLineWeights(cat):
    '''
    Returns the line weight properties (cut and projection) as a dictionary\
         where key is property description and value the property value

    :param cat: A category.
    :type cat: Autodesk.Revit.DB.Category

    :return: A dictionary.
    :rtype: dictionary {str: nullable integer}
    '''

    dicLineWeights = {}
    dicLineWeights[PROPERTY_LINE_WEIGHT_PROJECTION_NAME] = cat.GetLineWeight(rdb.GraphicsStyleType.Projection)
    dicLineWeights[PROPERTY_LINE_WEIGHT_CUT_NAME] = cat.GetLineWeight(rdb.GraphicsStyleType.Cut)
    return dicLineWeights

def GetCategoryColour(cat):
    '''
    Returns the colour properties (RGB) and values as a dictionary where key is colour name\
         and value the property value

    :param cat: A category.
    :type cat: Autodesk.Revit.DB.Category

    :return: A dictionary.
    :rtype: dictionary {str: byte}
    '''

    dicColour = {}
    dicColour[PROPERTY_LINE_COLOUR_RED_NAME] = 0
    dicColour[PROPERTY_LINE_COLOUR_GREEN_NAME] = 0
    dicColour[PROPERTY_LINE_COLOUR_BLUE_NAME] = 0
    if (cat.LineColor.IsValid):
        dicColour[PROPERTY_LINE_COLOUR_RED_NAME] = cat.LineColor.Red
        dicColour[PROPERTY_LINE_COLOUR_GREEN_NAME] = cat.LineColor.Green
        dicColour[PROPERTY_LINE_COLOUR_BLUE_NAME] = cat.LineColor.Blue
    return dicColour

def GetCategoryProperties(cat, doc):
    '''
    Returns a dictionary where keys are category property names and value is the associated property value.

    :param cat: A category.
    :type cat: Autodesk.Revit.DB.Category
    :param doc: Current Revit family document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A dictionary.
    :rtype: list [{str: var}]
    '''
    
    properties = []
    
    # material
    dicMaterial = GetCategoryMaterial(cat)
    properties.append(dicMaterial)
    
    # line pattern
    dicPattern = rPat.GetLinePatternFromCategory(cat, doc)
    properties.append(dicPattern)
    
    # line weights
    dicLineWeights = GetCategoryLineWeights(cat)
    properties.append(dicLineWeights)
    
    # category colour
    dicColour = GetCategoryColour(cat)
    properties.append(dicColour)
    return properties

def GetSavedCategoryPropertyByName(properties, propNames):
    '''
    Returns property values matching property names in saved category data.

    :param properties: List of dictionaries in format as per GetCategoryProperties(cat) method.
    :type properties: list [{str: var}]
    :param propNames: List of property names of which the values are to be returned
    :type propNames: list str

    :return: A list of values.
    :rtype: list var
    '''

    propValues = []
    for propName in propNames:
        match = False
        for savedProp in properties:
            if (propName in savedProp):
                propValues.append(savedProp[propName])
                match = True
        if(match == False):
            propValues.append(None)
    return propValues

#-------------------------- set category properties ---------------------------------

def SetCategoryMaterial(doc, cat, materialId):
    '''
    Updates material property of a given category.

    :param doc: Current Revit family document.
    :type doc: Autodesk.Revit.DB.Document
    :param cat: A category.
    :type cat: Autodesk.Revit.DB.Category
    :param materialId: The new material element id.
    :type materialId: Autodesk.Revit.DB.ElementId
    
    :return: True if material property was updated successfully, otherwise False.
    :rtype: bool
    '''

    flag = True
    try:
        mat = doc.GetElement(materialId)
        def action():
            actionReturnValue = res.Result()
            try:
                cat.Material = mat
                actionReturnValue.UpdateSep(True, 'Successfully set material value of subcategory')
            except Exception as e:
                actionReturnValue.UpdateSep(False, 'Failed to set material value of subcategory with exception: {}'.format(e))
            return actionReturnValue
        transaction = rdb.Transaction(doc,'Updating subcategory material: ' + str(rdb.Element.Name.GetValue(mat)))
        updateMat = rTran.in_transaction(transaction, action)
        flag = updateMat.status
    except Exception as e:
        flag = False
    return flag
    
def SetCategoryLinePattern(doc, cat, linePatternId, ignoreMissingCutStyle):
    '''
    Updates line pattern property of a given category.

    Note: in cases where the 'cut' property does not exist on a sub category this will return false even though the 'projection' property will most
    likely have been updated without a problem...

    :param doc: Current Revit family document.
    :type doc: Autodesk.Revit.DB.Document
    :param cat: A category.
    :type cat: Autodesk.Revit.DB.Category
    :param materialId: The new material element id.
    :type materialId: Autodesk.Revit.DB.ElementId
    :param ignoreMissingCutStyle: If true will not flag an exception if applying styles fails on missing cut style.
    :type ignoreMissingCutStyle: bool

    :return: True if line pattern property was updated successfully, otherwise False.
    :rtype: bool
    '''

    flag = True
    try:
        def action():
            actionReturnValue = res.Result()
            try:
                cat.SetLinePatternId(linePatternId, rdb.GraphicsStyleType.Cut)
                actionReturnValue.UpdateSep(True, 'Successfully set cut line pattern of subcategory')
            except Exception as e:
                if(ignoreMissingCutStyle):
                    actionReturnValue.UpdateSep(True, 'Failed to set cut line pattern of subcategory with exception: {}. Exception ignored!'.format(e))
                else:
                    actionReturnValue.UpdateSep(False, 'Failed to set cut line pattern of subcategory with exception: {}'.format(e))
            try:
                cat.SetLinePatternId(linePatternId, rdb.GraphicsStyleType.Projection)
                actionReturnValue.UpdateSep(True, 'Successfully set projection line pattern of subcategory')
            except Exception as e:
                actionReturnValue.UpdateSep(False, 'Failed to set projection line pattern of subcategory with exception: {}'.format(e))
            return actionReturnValue
        transaction = rdb.Transaction(doc,'Updating subcategory line pattern')
        updateLinePattern = rTran.in_transaction(transaction, action)
        flag = updateLinePattern.status
    except Exception as e:
        flag = False
    return flag

def SetCategoryLineWeights(doc, cat, lineThickNessCut, lineThicknessProjection, ignoreMissingCutStyle):
    '''
    Updates line weight properties of a given category.

    :param doc: Current Revit family document.
    :type doc: Autodesk.Revit.DB.Document
    :param cat: A category.
    :type cat: Autodesk.Revit.DB.Category
    :param lineThickNessCut: The cut line weight.
    :type lineThickNessCut: int
    :param lineThicknessProjection: The projection line weight.
    :type lineThicknessProjection: int
    :param ignoreMissingCutStyle: If true will not flag an exception if applying styles fails on missing cut style.
    :type ignoreMissingCutStyle: bool
    
    :return: True if line weight property was updated successfully, otherwise False.
    :rtype: bool
    '''

    flag = True
    try:
        def action():
            actionReturnValue = res.Result()
            try:
                cat.SetLineWeight(lineThickNessCut, rdb.GraphicsStyleType.Cut)
                actionReturnValue.UpdateSep(True, 'Successfully set cut line weight of subcategory')
            except Exception as e:
                if(ignoreMissingCutStyle):
                    actionReturnValue.UpdateSep(True, 'Failed to set cut line weight of subcategory with exception: {}. Exception ignored!'.format(e))
                else:
                    actionReturnValue.UpdateSep(False, 'Failed to set cut line weight of subcategory with exception: {}'.format(e))
            try:
                cat.SetLineWeight(lineThicknessProjection, rdb.GraphicsStyleType.Projection)
                actionReturnValue.UpdateSep(True, 'Successfully set projection line weight of subcategory')
            except Exception as e:
                actionReturnValue.UpdateSep(False, 'Failed to set projection line weight of subcategory with exception: {}'.format(e))
            return actionReturnValue
        transaction = rdb.Transaction(doc,'Updating subcategory line weights')
        updateLineWeights = rTran.in_transaction(transaction, action)
        flag = updateLineWeights.status
    except Exception as e:
        flag = False
    return flag

def SetCategoryColour(doc, cat, red, green, blue):
    '''
    Updates colour properties of a given category.

    :param doc: Current Revit family document.
    :type doc: Autodesk.Revit.DB.Document
    :param cat: A category.
    :type cat: Autodesk.Revit.DB.Category
    :param red: The colour red channel.
    :type red: byte
    :param green: The colour green channel.
    :type green: byte
    :param blue: The colour blue channel.
    :type blue: byte

    :return: True if colour property was updated successfully, otherwise False.
    :rtype: bool
    '''

    flag = True
    try:
        def action():
            actionReturnValue = res.Result()
            try:
                newColour = rdb.Color(red, green, blue)
                cat.LineColor = newColour
                actionReturnValue.UpdateSep(True, 'Successfully set colour value of subcategory')
            except Exception as e:
                actionReturnValue.UpdateSep(False, 'Failed to set colour value of subcategory with exception: {}'.format(e))
            return actionReturnValue
        transaction = rdb.Transaction(doc,'Updating subcategory colour')
        updateColour = rTran.in_transaction(transaction, action)
        flag = updateColour.status
    except Exception as e:
        flag = False
    return flag

def SetCategoryProperties(doc, cat, properties, ignoreMissingCutStyle):
    '''
    Updates varies property values of a given category.
    
    :param doc: Current Revit family document.
    :type doc: Autodesk.Revit.DB.Document
    :param cat: A category.
    :type cat: Autodesk.Revit.DB.Category
    :param properties: List of property values to be applied to category.
    :type properties: list of dictionaries in format as per GetCategoryProperties(cat) method.
    :param ignoreMissingCutStyle: If true will not flag an exception if applying styles fails on missing cut style.
    :type ignoreMissingCutStyle: bool

    :return: True if all properties where updated successfully, otherwise False.
    :rtype: bool
    '''
    
    # material
    matId = GetSavedCategoryPropertyByName(properties, [PROPERTY_MATERIAL_ID])
    flagMat = SetCategoryMaterial(doc, cat, matId[0])
    
    # line pattern
    linePatternId = GetSavedCategoryPropertyByName(properties, [rPat.PROPERTY_PATTERN_ID])
    flagPattern = SetCategoryLinePattern(doc, cat, linePatternId[0], ignoreMissingCutStyle)
    
    # line weights
    lineWeights = GetSavedCategoryPropertyByName(properties, [PROPERTY_LINE_WEIGHT_CUT_NAME, PROPERTY_LINE_WEIGHT_PROJECTION_NAME])
    flagLineWeights = SetCategoryLineWeights(doc, cat, lineWeights[0], lineWeights[1], ignoreMissingCutStyle)
    
    # category colour
    colourRGB = GetSavedCategoryPropertyByName(properties, [PROPERTY_LINE_COLOUR_RED_NAME, PROPERTY_LINE_COLOUR_GREEN_NAME, PROPERTY_LINE_COLOUR_BLUE_NAME])
    flagColours = SetCategoryColour(doc, cat, colourRGB[0], colourRGB[1], colourRGB[2])
    
    return flagMat & flagPattern & flagLineWeights & flagColours

#-------------------------- utilities ---------------------------------

# doc                       current family document
# newCategoryName           
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
   
def CreateNewSubCategoryToFamilyCategory(doc, newSubCategoryName):
    '''
    Creates a new subcategory to the family category and returns it.
    
    Note: if a subcategory with the name provided already exist it will be returned instead of trying to create another one with the same name.

    :param doc: Current Revit family document.
    :type doc: Autodesk.Revit.DB.Document
    :param newSubCategoryName: The new subcategory name
    :type newSubCategoryName: str

    :return: The new subcategory. Exception "The name 'xys' is already in use" if subcategory with the same name is already in file.
    :rtype: A category. (or str if exception occurred)
    '''

    returnValue = res.Result()
    if (doc.IsFamilyDocument):
        # check if subcategory already exists
        if(DoesMainSubCategoryExists(doc, newSubCategoryName)):
            # just return the already existing subcategory
            mainSubCategories = GetMainSubCategories(doc)
            returnValue.UpdateSep(True, 'Subcategory already in family.')
            returnValue.result = mainSubCategories[newSubCategoryName]
        else:
            # create a new subcategory
            # get the family category
            currentFamCat = doc.OwnerFamily.FamilyCategory
            parentCategory = None
            # get parent category object from Revit internal settings
            for mainCat in doc.Settings.Categories:
                if (mainCat.Name == currentFamCat.Name):
                    parentCategory = mainCat
                    break
            if(newSubCategoryName != parentCategory.Name):
                def action():
                    actionReturnValue = res.Result()
                    try:
                        newSubCategory = doc.Settings.Categories.NewSubcategory(parentCategory, newSubCategoryName)
                        actionReturnValue.UpdateSep(True, 'Created subcategory ' + str(newSubCategoryName))
                        actionReturnValue.result = newSubCategory
                    except Exception as e:
                        actionReturnValue.UpdateSep(False, 'Failed to create ' + str(newSubCategoryName) + ' with exception: ' + str(e))
                    return actionReturnValue
                transaction = rdb.Transaction(doc,'Creating subcategory: ' + str(newSubCategoryName))
                returnValue = rTran.in_transaction(transaction, action)
            else:
                returnValue.UpdateSep(False, 'Cant create subcategory with the same name as the family category!')
    else:
        returnValue.UpdateSep(False, 'This is not a family document!')
    return returnValue
          
def SortElementsByCategory(elements, elementDic):
    '''
    Returns a dictionary of element ids where key is the category they belong to.

    :param elements:  List of revit elements.
    :type elements: [Autodesk.Revit.DB.Element]
    :param elementDic:  Dictionary where key is subcategory and values are element ids.
    :type elementDic: {Autodesk.Revit.DB.Category: [Autodesk.Revit.DB.ElementId]}
    
    :return: Dictionary where key is subcategory id and values are element ids.
    :rtype: {Autodesk.Revit.DB.ElementId: [Autodesk.Revit.DB.ElementId]}
    '''

    for el in elements:
        for builtinDef in ELEMENTS_PARAS_SUB:
            value = rParaGet.get_built_in_parameter_value(el, builtinDef, rParaGet.get_parameter_value_as_element_id)
            if (value != None):
                if(value in elementDic):
                    elementDic[value].append(el.Id)
                else:
                    elementDic[value] = [el.Id]
                break
    return elementDic

def SortGeometryElementsByCategory(elements, elementDic, doc):
    counter = 0
    for el in elements:
        counter = counter + 1
        graphicStyleId = rdb.ElementId.InvalidElementId
        if(type(el) is rdb.Solid):
            # get graphic style id from edges
            edgeArray = el.Edges
            if(edgeArray.IsEmpty == False):
                for edge in edgeArray:
                    graphicStyleId = edge.GraphicsStyleId
        else:
            graphicStyleId = el.GraphicsStyleId
        # failed to get an id?
        if(graphicStyleId != rdb.ElementId.InvalidElementId):
            graphicStyle = doc.GetElement(graphicStyleId)
            graphCatId = graphicStyle.GraphicsStyleCategory.Id
            # geometry elements have no Id property ... Doh!! pass in invalid element id...
            if (graphCatId != None):
                if(graphCatId in elementDic):
                    elementDic[graphCatId].append(rdb.ElementId.InvalidElementId)
                else:
                    elementDic[graphCatId] = [rdb.ElementId.InvalidElementId]
    return elementDic

def _sortAllElementsByCategory(doc):
    '''
    Sorts all elements in a family by category.

    :param doc: Current Revit family document.
    :type doc: Autodesk.Revit.DB.Document

    :return: Dictionary where key is subcategory id and values are element ids.
    :rtype: {Autodesk.Revit.DB.ElementId: [Autodesk.Revit.DB.ElementId]}
    '''

    # get all elements in family
    dic = {}
    elCurve = rFamUtils.GetAllCurveBasedElementsInFamily(doc)
    elForms = rFamUtils.GetAllGenericFormsInFamily(doc)
    elMText = rFamUtils.GetAllModelTextElementsInFamily(doc)
    elRefPlanes = rFamUtils.GetAllReferencePlanesInFamily(doc)
    # get import Instance elements
    elImport = rLink.GetAllCADImportInstancesGeometry(doc)
    # build dictionary where key is category or graphic style id of  a category
    dic = SortElementsByCategory(elCurve, dic)
    dic = SortElementsByCategory(elForms, dic)
    dic = SortElementsByCategory(elMText, dic)
    dic = SortElementsByCategory(elRefPlanes, dic)
    # geometry instances use a property rather then a parameter to store the category style Id
    dic = SortGeometryElementsByCategory(elImport, dic, doc)
    return dic

def GetElementsByCategory(doc, cat):
    '''
    Returns elements in family assigned to a specific category

    :param doc: Current Revit family document.
    :type doc: Autodesk.Revit.DB.Document
    :param cat: A category.
    :type cat: Autodesk.Revit.DB.Category

    :return: Dictionary where key is subcategory and values are element ids.
    :rtype: {Autodesk.Revit.DB.Category: [Autodesk.Revit.DB.ElementId]}
    '''

    # get all elements in family
    dic = _sortAllElementsByCategory(doc)
    # get id and graphic style id of category to be filtered by
    categoryIds = GetCategoryGraphicStyleIds(cat)
    # check whether category past in is same as owner family category
    if(doc.OwnerFamily.FamilyCategory.Name == cat.Name):
        # 3d elements within family which have subcategory set to 'none' belong to owner family
        # category. Revit uses a None value as id rather then the actual category id
        # my get parameter value translates that into -1 (invalid element id)
        categoryIds[CATEGORY_GRAPHIC_STYLE_3D] = rdb.ElementId.InvalidElementId
    dicFiltered = {}
    # filter elements by category ids
    for key,value in categoryIds.items():
        #print (key + ' ' + str(value))
        if value in dic:
            dicFiltered[key] = dic[value]
        else:
            dicFiltered[key] = []
    return dicFiltered

def GetUsedCategoryIds(doc):
    '''
    Returns all category ids in a family which have an element assigned to them

    :param doc: Current Revit family document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of categories.
    :rtype: [Autodesk.Revit.DB.Category]
    '''

    # get all elements in family
    dic = _sortAllElementsByCategory(doc)
    return dic.keys ()

# ----------------------------- modify / create subcategories -------------------------------------

def CreateNewCategoryAndTransferProperties(doc, newCatName, existingCatName):
    '''
    Creates a new subcategory and transfer properties from existing subcategory.

    :param doc: Current Revit family document.
    :type doc: Autodesk.Revit.DB.Document
    :param newCatName: The new sub category name.
    :type newCatName: str
    :param existingCatName: The existing subcategory name
    :type existingCatName: str

    :return: 
        Result class instance.

        - result.status. True if category was created or already existed in file, otherwise False.
        - result.message will contain the name of the category created.
        - result.result returns new category, if category already exists in file it will return that
        
        On exception:
        
        - result.status (bool) will be False.
        - result.message will contain generic exception message.
        - result.result will be empty

    :rtype: :class:`.Result`
    '''

    returnValue = res.Result()
    cats = GetMainSubCategories(doc)
    # check if existing category actually exists in family
    if(existingCatName in cats):
        # check whether the new category already exists!
        if (newCatName not in cats):
            copyFromCat = cats[existingCatName]
            catProps = GetCategoryProperties(copyFromCat, doc)
            resultNewSubCat = CreateNewCategoryFromSavedProperties(doc, newCatName, catProps)
            returnValue.Update(resultNewSubCat)
        else:
            returnValue.UpdateSep(True, 'Category already in file:'+ str(newCatName))
            returnValue.result = cats[newCatName]
    else:
        returnValue.UpdateSep(False, 'Template category: '+ str(existingCatName) + ' does not exist in file!')
    return returnValue

def CreateNewCategoryFromSavedProperties(doc, newCatName, savedCatProps, ignoreMissingCutStyle = False):
    '''
    Creates a new category and applies properties stored.

    :param doc: Current Revit family document.
    :type doc: Autodesk.Revit.DB.Document
    :param newCatName: The new sub category name.
    :type newCatName: str
    :param savedCatProps: Dictionary containing subcategory properties.
    :type savedCatProps: list of dictionaries in format as per GetCategoryProperties(cat) method.
    :param ignoreMissingCutStyle: If true will not flag an exception if applying styles fails on missing cut style.
    :type ignoreMissingCutStyle: bool

    :return: 
        Result class instance.

        - result.status. True if category was created or already existed in file, otherwise False.
        - result.message will contain the name of the category created.
        - result.result returns new category, if category already exists in file it will return that
        
        On exception:
        
        - result.status (bool) will be False.
        - result.message will contain generic exception message.
        - result.result will be empty

    :rtype: :class:`.Result`
    '''

    returnValue = res.Result()
    resultNewSubCat = CreateNewSubCategoryToFamilyCategory(doc, newCatName)
    if(resultNewSubCat.status):
        newSubCat = resultNewSubCat.result
        flag = SetCategoryProperties(doc, newSubCat, savedCatProps, ignoreMissingCutStyle)
        if(flag):
            returnValue.UpdateSep(True, 'Successfully created category: '+ str(newCatName))
            returnValue.result = newSubCat
        else:
            returnValue.UpdateSep(False, 'Failed to apply properties to new category: '+ str(newCatName))
    else:
        returnValue.UpdateSep(False, 'Failed to create new subcategory: '+ str(newCatName))
    return returnValue

def MoveElementsFromSubCategoryToSubCategory(doc, fromCategoryName, toCategoryName):
    '''
    Moves elements from one subcategory to another one identified by their names.

    :param doc: Current Revit family document.
    :type doc: Autodesk.Revit.DB.Document
    :param fromCategoryName: The source subcategory name. 
    :type fromCategoryName: str
    :param toCategoryName: The destination subcategory name.
    :type toCategoryName: str

    :return: 
        Result class instance.

        - result.status. True if all elements from source subcategory where moved to destination subcategory, otherwise False.
        - result.message will contain the name of the destination subcategory by element.
        - result.result empty list
        
        On exception:
        
        - result.status (bool) will be False.
        - result.message will contain generic exception message.
        - result.result will be empty

    :rtype: :class:`.Result`
    '''

    returnValue = res.Result()
    # check whether source and destination category exist in file
    cats = GetMainSubCategories(doc)
    if(fromCategoryName in cats):
        if(toCategoryName in cats):
            # dictionary containing destination category ids (3D, cut and projection)
            destinationCatIds = GetCategoryGraphicStyleIds(cats[toCategoryName])
            # get elements on source category
            dic = GetElementsByCategory(doc, cats[fromCategoryName])
            # move elements
            returnValue = MoveElementsToCategory(doc, dic, toCategoryName, destinationCatIds)
        else:
            returnValue.UpdateSep(False, 'Destination category: '+ str(toCategoryName) + ' does not exist in file!')
    else:
       returnValue.UpdateSep(False, 'Source category: '+ str(fromCategoryName) + ' does not exist in file!')
    return returnValue

def MoveElementsToCategory(doc, elements, toCategoryName, destinationCatIds):
    '''
    Moves elements provided in dictionary to another category specified by name.

    :param doc: Current Revit family document.
    :type doc: Autodesk.Revit.DB.Document
    :param elements: Dictionary of elements, key are graphic style names.
    :type elements: {Autodesk.Revit.DB.Category: [Autodesk.Revit.DB.ElementId]}
    :param toCategoryName: The name of the subcategory elements are to be moved to.
    :type toCategoryName: str
    :param destinationCatIds: Dictionary of ids of graphic style, key are graphic style names
    :type destinationCatIds: dictionary {str: Autodesk.Revit.DB.ElementId}

    :return: 
        Result class instance.

        - result.status. True if all elements where moved to destination subcategories, otherwise False.
        - result.message will contain the name of the destination subcategory by element.
        - result.result empty list
        
        On exception:
        
        - result.status (bool) will be False.
        - result.message will contain generic exception message.
        - result.result will be empty

    :rtype: :class:`.Result`
    '''

    returnValue = res.Result()
    # check whether destination category exist in file
    cats = GetMainSubCategories(doc)
    if(toCategoryName in cats):
        for key,value in elements.items():
                # anything needing moving?
                if(len(value)>0):
                    for elId in value:
                        el = doc.GetElement(elId)
                        paras = el.GetOrderedParameters()
                        # find the parameter driving the subcategory
                        for p in paras:
                            if (p.Definition.BuiltInParameter in ELEMENTS_PARAS_SUB):
                                # get the subcategory style id
                                targetId = destinationCatIds[key]
                                # check if a 'cut' style id exists...if not move to 'projection' instead
                                # not sure how this works in none - english versions of Revit...
                                if(key == 'Cut' and targetId == rdb.ElementId.InvalidElementId):
                                    targetId = destinationCatIds['Projection']
                                    returnValue.AppendMessage('No cut style present in family, using projection style instead')
                                updatedPara = rParaSet.set_parameter_value(p, str(targetId), doc)
                                returnValue.Update(updatedPara)
                                break
    else:
        returnValue.UpdateSep(False, 'Destination category: '+ str(toCategoryName) + ' does not exist in file!')
    return returnValue

def RenameSubCategory(doc, oldSubCatName, newSubCatName):
    '''
    Renames a family custom subcategory.

    Note: Only subcategory directly belonging to the family category will be checked for a match.

    - Revit API does currently not allow to change a subcategory name. This method instead:

        - duplicates the old subcategory with the new name
        - moves all elements belonging to the old subcategory to the new subcategory
        - deletes the old subcategory

    - If the new subcategory already exists in the file:

        - moves all elements belonging to the old subcategory to the new subcategory
        - deletes the old subcategory

    :param doc: Current Revit family document.
    :type doc: Autodesk.Revit.DB.Document
    :param oldSubCatName: The subcategory name to be re-named
    :type oldSubCatName: str
    :param newSubCatName: The new subcategory name.
    :type newSubCatName: str

    :return: 
        Result class instance.

        - result.status. True if subcategory was renamed successfully , otherwise False.
        - result.message will contain rename process messages.
        - result.result empty list
        
        On exception:
        
        - result.status (bool) will be False.
        - result.message will contain generic exception message.
        - result.result will be empty

    :rtype: :class:`.Result`
    '''

    returnValue = res.Result()
    # check whether ol;d subcategory exists in family file
    alreadyInFamilyOld = DoesMainSubCategoryExists(doc, oldSubCatName)
    if(alreadyInFamilyOld):
        # check whether new subcategory already in family
        alreadyInFamily = DoesMainSubCategoryExists(doc, newSubCatName)
        if(alreadyInFamily):
            # just move elements from old sub category to new one
            returnValue.AppendMessage('Subcategory: ' + newSubCatName + ' already in family.')
        else:
            # duplicate old sub category
            createNewStatus = CreateNewCategoryAndTransferProperties(doc, newSubCatName, oldSubCatName)
            returnValue.Update(createNewStatus)
        # check if we have a subcategory to move elements to
        if(returnValue.status):
            # move elements
            moveStatus = MoveElementsFromSubCategoryToSubCategory(doc, oldSubCatName, newSubCatName)
            returnValue.Update(moveStatus)
            if(moveStatus.status):
                deletedOldSubCategory = DeleteMainSubCategory(doc, oldSubCatName)
                if(deletedOldSubCategory):
                    returnValue.UpdateSep(True, 'Subcategory: ' + oldSubCatName + ' deleted successfully.')
                else:
                    returnValue.UpdateSep(True, 'Subcategory: ' + oldSubCatName + ' failed to delete subcategory...Exiting')
            else:
                returnValue.UpdateSep(False, 'Subcategory: ' + newSubCatName + ' failed to move elements to new subcategory. Exiting...')
        else:
            returnValue.UpdateSep(False, 'Subcategory: ' + newSubCatName + ' failed to create in family. Exiting...')
    else:
        returnValue.UpdateSep(False, 'Base subcategory: ' + oldSubCatName + ' does not exist in family. Exiting...')
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

# --------------------------------------- reporting --------------------------------------------------------------

def BuildReportDataByCategory(doc, dic, familyCat, mainCatName, docFilePath):
    '''
    Formats category properties into lists for reports

    :param doc: Current Revit family document.
    :type doc: Autodesk.Revit.DB.Document
    :param dic: dictionary containing category properties
    :type dic: _type_
    :param familyCat: The family category name.
    :type familyCat: str
    :param mainCatName: A hard coded revit category name. Can be the same as familyCat.
    :type mainCatName: str
    :param docFilePath: The fully qualified family file path.
    :type docFilePath: str

    :return: A list of list of strings. Each row represents one category.
    :rtype: list[list[str]]
    '''

    data = []
    for key in dic:
        row = [str(docFilePath).encode('utf-8'), 
            familyCat.encode('utf-8'), 
            mainCatName.encode('utf-8'), 
            key.encode('utf-8'),
            str(dic[key].Id)]
        # get elements
        elements = GetElementsByCategory (doc, dic[key])
        # get properties
        dicMaterial = GetCategoryMaterial(dic[key])
        row.append(str(dicMaterial[PROPERTY_MATERIAL_NAME]).encode('utf-8'))
        row.append(str(dicMaterial[PROPERTY_MATERIAL_ID]).encode('utf-8'))
        # line pattern
        dicPattern = rPat.GetLinePatternFromCategory(dic[key], doc)
        row.append(str(dicPattern[rPat.PROPERTY_PATTERN_NAME]).encode('utf-8'))
        row.append(str(dicPattern[rPat.PROPERTY_PATTERN_ID]).encode('utf-8'))
        # line weights
        dicLineWeights = GetCategoryLineWeights(dic[key])
        row.append(str(dicLineWeights[PROPERTY_LINE_WEIGHT_PROJECTION_NAME]).encode('utf-8'))
        row.append(str(dicLineWeights[PROPERTY_LINE_WEIGHT_CUT_NAME]).encode('utf-8'))
        # category colour
        dicColour = GetCategoryColour(dic[key])
        row.append(str(dicColour[PROPERTY_LINE_COLOUR_RED_NAME]).encode('utf-8'))
        row.append(str(dicColour[PROPERTY_LINE_COLOUR_GREEN_NAME]).encode('utf-8'))
        row.append(str(dicColour[PROPERTY_LINE_COLOUR_BLUE_NAME]).encode('utf-8'))
        # elements
        row.append(str(len(elements[CATEGORY_GRAPHIC_STYLE_3D])).encode('utf-8'))
        row.append(str(len(elements[CATEGORY_GRAPHIC_STYLE_PROJECTION])).encode('utf-8'))
        row.append(str(len(elements[CATEGORY_GRAPHIC_STYLE_CUT])).encode('utf-8'))

        data.append(row)
    return data

def GetReportData(doc, revitFilePath):
    '''
    Reports all categories, their properties and all elements belonging to them.

    :param doc: Current Revit family document.
    :type doc: Autodesk.Revit.DB.Document
    :param revitFilePath: The fully qualified family file path.
    :type revitFilePath: str
    
    :return: A list of list of strings. Each row represents one category.
    :rtype: list[list[str]]
    '''

    data = []
    # get all sub categories in family and associates elements;
    subCats = GetMainSubCategories(doc) # i/e family is specialty equipment and all its associated sub categories
    familyCat = GetFamilyCategory(doc) # any 3D element which is set to 'None' in subcategory (if family is specialty equipment so is this element)
    otherCats = GetOtherSubCategories(doc) # Imports in Families cats are here
    familyCatName = list(familyCat.keys())[0]
    # build output
    data = BuildReportDataByCategory(doc, familyCat, familyCatName, familyCatName, revitFilePath)
    data = data + BuildReportDataByCategory(doc, subCats, familyCatName, familyCatName, revitFilePath)
    # check for imports
    if ('Imports in Families' in otherCats):
        data = data + BuildReportDataByCategory(doc, otherCats['Imports in Families'], familyCatName, 'Imports in Families', revitFilePath)
    return data