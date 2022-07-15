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

import RevitCommonAPI as com
import RevitFamilyUtils as rFamUtils
import Result as res

clr.AddReference('System.Core')
clr.ImportExtensions(System.Linq)
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
    rdb.BuiltInParameter.FAMILY_ELEM_SUBCATEGORY
]


#-------------------------- get category properties ---------------------------------

#: category properties dictionary key names and default values
#: material name
PROPERTY_MATERIAL_NAME = 'MaterialName'
#: material name default value
PROPERTY_MATERIAL_NAME_VALUE_DEFAULT = 'None'
#: material id
PROPERTY_MATERIAL_ID = 'MaterialId'

#: pattern name
PROPERTY_PATTERN_NAME = 'PatternName'
#: pattern name default value, hard coded solid line pattern name
PROPERTY_PATTERN_NAME_VALUE_DEFAULT = 'Solid'
#: pattern id
PROPERTY_PATTERN_ID = 'PatternId'

#: line weight projection name
PROPERTY_LINEWEIGHT_PROJECTION_NAME = 'LineWeightProjection'
#: line weight cut name
PROPERTY_LINEWEIGHT_CUT_NAME = 'LineWeightCut'

#: line colour red name
PROPERTY_LINECOLOUR_RED_NAME = 'Red'
#: line colour green name
PROPERTY_LINECOLOUR_GREEN_NAME = 'Green'
#: line colour blue name
PROPERTY_LINECOLOUR_BLUE_NAME = 'Blue'


#: graphic styles used for elements in families
#: graphic style projection name
CATEGORY_GRAPHICSTYLE_PROJECTION = 'Projection'
#: graphic style cut name
CATEGORY_GRAPHICSTYLE_CUT = 'Cut'
#: graphic style 3D name
CATEGORY_GRAPHICSTYLE_3D = '3D'


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
    PROPERTY_PATTERN_NAME.upper(), 
    PROPERTY_PATTERN_ID.upper(), 
    PROPERTY_LINEWEIGHT_PROJECTION_NAME.upper(), 
    PROPERTY_LINEWEIGHT_CUT_NAME.upper(), 
    PROPERTY_LINECOLOUR_RED_NAME.upper(), 
    PROPERTY_LINECOLOUR_GREEN_NAME.upper(), 
    PROPERTY_LINECOLOUR_BLUE_NAME.upper(),
    CATEGORY_GRAPHICSTYLE_3D.upper(), 
    CATEGORY_GRAPHICSTYLE_PROJECTION.upper(), 
    CATEGORY_GRAPHICSTYLE_CUT.upper() 
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
            for subcat in mainCat.SubCategories:
                catData[subcat.Name] = subcat
    return catData

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
    # set as default the same as the projection style since that seems to be always available
    iDGraphicStyleCut = iDGraphicStyleProjection
    if(graphicStyleCut != None):
        iDGraphicStyleCut = cat.GetGraphicsStyle(rdb.GraphicsStyleType.Cut).Id
    # build category dictionary where key is the style type, values is the corresponding Id
    dic = {}
    dic[CATEGORY_GRAPHICSTYLE_PROJECTION] = iDGraphicStyleProjection 
    dic[CATEGORY_GRAPHICSTYLE_CUT] = iDGraphicStyleCut
    dic[CATEGORY_GRAPHICSTYLE_3D] = cat.Id
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

def GetCategoryLinePattern(cat, doc):
    '''
    Returns the line pattern properties as a dictionary\
         where key is property name and value the pattern id.

    :param cat: A category.
    :type cat: Autodesk.REvit.DB.Category
    :param doc: Current Revit family document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A dictionary.
    :rtype: dictionary {str: Autodesk.Revit.DB.ElementId}
    '''

    dicPattern = {}
    dicPattern[PROPERTY_PATTERN_NAME] = PROPERTY_PATTERN_NAME_VALUE_DEFAULT
    dicPattern[PROPERTY_PATTERN_ID] = patternId = cat.GetLinePatternId(rdb.GraphicsStyleType.Projection)
    '''check for 'solid' pattern which apparently is not a pattern at all
    *The RevitAPI.chm documents says: Note that Solid is special. It isn't a line pattern at all -- 
    * it is a special code that tells drawing and export code to use solid lines rather than patterned lines. 
    * Solid is visible to the user when selecting line patterns. 
    '''
    if(patternId != rdb.LinePatternElement.GetSolidPatternId()):
        # not a solid line pattern
        collector = rdb.FilteredElementCollector(doc).OfClass(rdb.LinePatternElement)
        linePatternElement = None
        for c in collector:
            if(patternId == c.Id):
                dicPattern[PROPERTY_PATTERN_NAME] = rdb.Element.Name.GetValue(c)         
    return dicPattern

def GetCategoryLineWeights(cat):
    '''
    Returns the line weight properties (cut and projection) as a dictionary\
         where key is property description and value the property value

    :param cat: A category.
    :type cat: Autodesk.REvit.DB.Category

    :return: A dictionary.
    :rtype: dictionary {str: nullable integer}
    '''

    dicLineWeights = {}
    dicLineWeights[PROPERTY_LINEWEIGHT_PROJECTION_NAME] = cat.GetLineWeight(rdb.GraphicsStyleType.Projection)
    dicLineWeights[PROPERTY_LINEWEIGHT_CUT_NAME] = cat.GetLineWeight(rdb.GraphicsStyleType.Cut)
    return dicLineWeights

def GetCategoryColour(cat):
    '''
    Returns the colour properties (RGB) and values as a dictionary where key is colour name\
         and value the property value

    :param cat: A category.
    :type cat: Autodesk.REvit.DB.Category

    :return: A dictionary.
    :rtype: dictionary {str: byte}
    '''

    dicColour = {}
    dicColour[PROPERTY_LINECOLOUR_RED_NAME] = 0
    dicColour[PROPERTY_LINECOLOUR_GREEN_NAME] = 0
    dicColour[PROPERTY_LINECOLOUR_BLUE_NAME] = 0
    if (cat.LineColor.IsValid):
        dicColour[PROPERTY_LINECOLOUR_RED_NAME] = cat.LineColor.Red
        dicColour[PROPERTY_LINECOLOUR_GREEN_NAME] = cat.LineColor.Green
        dicColour[PROPERTY_LINECOLOUR_BLUE_NAME] = cat.LineColor.Blue
    return dicColour

def GetCategoryProperties(cat, doc):
    '''
    Returns a dictionary where keys are category property names and value is the associated property value.

    :param cat: A category.
    :type cat: Autodesk.REvit.DB.Category
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
    dicPattern = GetCategoryLinePattern(cat, doc)
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
            cat.Material = mat
        transaction = rdb.Transaction(doc,'Updating subcategory material: ' + str(rdb.Element.Name.GetValue(mat)))
        updateMat = com.InTransaction(transaction, action)
    except Exception as e:
        print('SetCategoryMaterial ' + str(e))
        flag = False
    return flag
    
def SetCategoryLinePattern(doc, cat, linePatternId):
    '''
    Updates line pattern property of a given category.

    :param doc: Current Revit family document.
    :type doc: Autodesk.Revit.DB.Document
    :param cat: A category.
    :type cat: Autodesk.Revit.DB.Category
    :param materialId: The new material element id.
    :type materialId: Autodesk.Revit.DB.ElementId

    :return: True if line pattern property was updated successfully, otherwise False.
    :rtype: bool
    '''

    flag = True
    try:
        def action():
            cat.SetLinePatternId(linePatternId, rdb.GraphicsStyleType.Cut)
            cat.SetLinePatternId(linePatternId, rdb.GraphicsStyleType.Projection)
        transaction = rdb.Transaction(doc,'Updating subcategory line pattern')
        updateLinePattern = com.InTransaction(transaction, action)
    except Exception as e:
        print('SetCategoryLinePattern ' + str(e))
        flag = False
    return flag

def SetCategoryLineWeights(doc, cat, lineThickNessCut, lineThicknessProjection):
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
    
    :return: True if line weight property was updated successfully, otherwise False.
    :rtype: bool
    '''

    flag = True
    try:
        def action():
            cat.SetLineWeight(lineThickNessCut, rdb.GraphicsStyleType.Cut)
            cat.SetLineWeight(lineThicknessProjection, rdb.GraphicsStyleType.Projection)
        transaction = rdb.Transaction(doc,'Updating subcategory line weights')
        updateLineWeights = com.InTransaction(transaction, action)
    except Exception as e:
        print('SetCategoryLineWeights:' + str(e))
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
            newColour = rdb.Color(red, green, blue)
            cat.LineColor = newColour
        transaction = rdb.Transaction(doc,'Updating subcategory colour')
        updateColour = com.InTransaction(transaction, action)
    except Exception as e:
        print('SetCategoryColour ' + str(e))
        flag = False
    return flag

def SetCategoryProperties(doc, cat, properties):
    '''
    Updates varies property values of a given category.
    
    :param doc: Current Revit family document.
    :type doc: Autodesk.Revit.DB.Document
    :param cat: A category.
    :type cat: Autodesk.Revit.DB.Category
    :param properties: List of property values to be applied to category.
    :type properties: list of dictionaries in format as per GetCategoryProperties(cat) method.

    :return: True if all properties where updated successfully, otherwise False.
    :rtype: bool
    '''
    
    # material
    matId = GetSavedCategoryPropertyByName(properties, [PROPERTY_MATERIAL_ID])
    flagMat = SetCategoryMaterial(doc, cat, matId[0])
    
    # line pattern
    linePatternId = GetSavedCategoryPropertyByName(properties, [PROPERTY_PATTERN_ID])
    flagPattern = SetCategoryLinePattern(doc, cat, linePatternId[0])
    
    # line weights
    lineWeights = GetSavedCategoryPropertyByName(properties, [PROPERTY_LINEWEIGHT_CUT_NAME, PROPERTY_LINEWEIGHT_PROJECTION_NAME])
    flagLineWeights = SetCategoryLineWeights(doc, cat, lineWeights[0], lineWeights[1])
    
    # category colour
    colourRGB = GetSavedCategoryPropertyByName(properties, [PROPERTY_LINECOLOUR_RED_NAME, PROPERTY_LINECOLOUR_GREEN_NAME, PROPERTY_LINECOLOUR_BLUE_NAME])
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
    
    :return: True only if the category was changed successfully. Any other case False! (That includes situations when the family is already of the new catgeory)
    :rtype: bool
    '''
    
    returnValue = res.Result()
    cat = doc.OwnerFamily.FamilyCategory
    if (cat.Name != newCategoryName):
        if (doc.Settings.Categories.Contains(newCategoryName)):
            def action():
                doc.OwnerFamily.FamilyCategory = doc.Settings.Categories.get_Item(newCategoryName)
            transaction = rdb.Transaction(doc,'Changing family category to:' + str(newCategoryName))
            changeCat = com.InTransaction(transaction, action)
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
    
    TODO: Bubble up exception if subcategory already exists!

    :param doc: Current Revit family document.
    :type doc: Autodesk.Revit.DB.Document
    :param newSubCategoryName: The new subcategory name
    :type newSubCategoryName: str

    :return: The new subcategory. Exception "The name 'xys' is already in use" if subcategory with the same name is already in file.
    :rtype: A category. (or str if exception occurred)
    '''

    returnValue = res.Result()
    if (doc.IsFamilyDocument):
        # get the family category
        currentFamCat = doc.OwnerFamily.FamilyCategory
        parentCategory = None
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
            returnValue = com.InTransaction(transaction, action)
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
    
    :return: Dictionary where key is subcategory and values are element ids.
    :rtype: {Autodesk.Revit.DB.Category: [Autodesk.Revit.DB.ElementId]}
    '''

    for el in elements:
        for builtinDef in ELEMENTS_PARAS_SUB:
            value = com.GetBuiltInParameterValue(el, builtinDef)
            if (value != None):
                if(value in elementDic):
                    elementDic[value].append(el.Id)
                else:
                    elementDic[value] = [el.Id]
                break
    return elementDic

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
    dic = {}
    elCurve = rFamUtils.GetAllCurveBasedElementsInFamily(doc)
    elForms = rFamUtils.GetAllGenericFormsInFamily(doc)
    elMText = rFamUtils.GetAllModelTextElementsInFamily(doc)
    # build dictionary where key is category or graphic style id of  a category
    dic = SortElementsByCategory(elCurve, dic)
    dic = SortElementsByCategory(elForms, dic)
    dic = SortElementsByCategory(elMText, dic)
    # get id and graphic style id of category to be filtered by
    categoryIds = GetCategoryGraphicStyleIds(cat)
    # check whether category past in is same as owner family category
    if(doc.OwnerFamily.FamilyCategory.Name == cat.Name):
        # 3d elements within family which have subcategory set to 'none' belong to owner family
        # category. Revit uses a None value as id rather then the actual category id
        # my get parameter value translates that into -1 (invalid element id)
        categoryIds[CATEGORY_GRAPHICSTYLE_3D] = rdb.ElementId.InvalidElementId
    dicFiltered = {}
    # filter elements by category ids
    for key,value in categoryIds.items():
        # print (key + ' ' + str(value))
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
    dic = {}
    elCurve = rFamUtils.GetAllCurveBasedElementsInFamily(doc)
    elForms = rFamUtils.GetAllGenericFormsInFamily(doc)
    elMText = rFamUtils.GetAllModelTextElementsInFamily(doc)
    # build dictionary where key is category or graphic style id of a category
    dic = SortElementsByCategory(elCurve, dic)
    dic = SortElementsByCategory(elForms, dic)
    dic = SortElementsByCategory(elMText, dic)
    return dic.keys ()

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
        returnValue.UpdateSep(False, 'Template category '+ str(existingCatName) + ' does not exist in file!')
    return returnValue

def CreateNewCategoryFromSavedProperties(doc, newCatName, savedCatProps):
    '''
    Creates a new category and applies properties stored.

    :param doc: Current Revit family document.
    :type doc: Autodesk.Revit.DB.Document
    :param newCatName: The new sub category name.
    :type newCatName: str
    :param savedCatProps: Dictionary containing subcategory properties.
    :type savedCatProps: list of dictionaries in format as per GetCategoryProperties(cat) method.

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
    if(resultNewSubCat.result):
        newSubCat = resultNewSubCat.result
        flag = SetCategoryProperties(newSubCat, savedCatProps)
        if(flag):
            returnValue.UpdateSep(True, 'Successfully created category '+ str(newCatName))
            returnValue.result = newSubCat
        else:
            returnValue.UpdateSep(False, 'Failed to apply properties to new category: '+ str(newCatName))
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
            returnValue.UpdateSep(False, 'Destination category '+ str(toCategoryName) + ' does not exist in file!')
    else:
       returnValue.UpdateSep(False, 'Source category '+ str(fromCategoryName) + ' does not exist in file!')
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
                        for p in paras:
                            if (p.Definition.BuiltInParameter in ELEMENTS_PARAS_SUB):
                                targetId = destinationCatIds[key]
                                updatedPara = com.setParameterValue(p, str(targetId), doc)
                                returnValue.Update(updatedPara)
                                break
    else:
        returnValue.UpdateSep(False, 'Destination category '+ str(toCategoryName) + ' does not exist in file!')
    return returnValue

def ChangeFamilyCategory(doc, newCategoryName):
    '''
    Changes the current family category to the new one specified.

    Revit's default behaviour when changing the category of a family is to discard all custom subcategories created and assign elements which are on those custom subcategories\
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
        props[subCat] = props
    
    # change family category
    changeFam = SetFamilyCategory(doc, newCategoryName)

    if(changeFam.status):
        # re-create custom sub categories
        for subCat in subCats:
            # only re-create custom sub categories (id greater then 0)
            if(subCats[subCat].Id.IntegerValue > 0):
                createCat = CreateNewCategoryFromSavedProperties(doc, subCat, props[subCat])
                if(createCat.status):
                    # move elements back onto custom subcategories
                    moveEl = MoveElementsToCategory(doc, elements[subCat], subCat, props[subCat])
                    returnValue.Update(moveEl)
                else:
                    returnValue.Update(createCat)
    else:
        returnValue.UpdateSep(False, 'Failed to change family category:' + changeFam.message)
    return returnValue

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
        dicPattern = GetCategoryLinePattern(dic[key], doc)
        row.append(str(dicPattern[PROPERTY_PATTERN_NAME]).encode('utf-8'))
        row.append(str(dicPattern[PROPERTY_PATTERN_ID]).encode('utf-8'))
        # line weights
        dicLineWeights = GetCategoryLineWeights(dic[key])
        row.append(str(dicLineWeights[PROPERTY_LINEWEIGHT_PROJECTION_NAME]).encode('utf-8'))
        row.append(str(dicLineWeights[PROPERTY_LINEWEIGHT_CUT_NAME]).encode('utf-8'))
        # category colour
        dicColour = GetCategoryColour(dic[key])
        row.append(str(dicColour[PROPERTY_LINECOLOUR_RED_NAME]).encode('utf-8'))
        row.append(str(dicColour[PROPERTY_LINECOLOUR_GREEN_NAME]).encode('utf-8'))
        row.append(str(dicColour[PROPERTY_LINECOLOUR_BLUE_NAME]).encode('utf-8'))
        # elements
        row.append(str(len(elements[CATEGORY_GRAPHICSTYLE_3D])).encode('utf-8'))
        row.append(str(len(elements[CATEGORY_GRAPHICSTYLE_PROJECTION])).encode('utf-8'))
        row.append(str(len(elements[CATEGORY_GRAPHICSTYLE_CUT])).encode('utf-8'))

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
    subCats = GetMainSubCategories(doc)
    familyCat = GetFamilyCategory(doc)
    otherCats = GetOtherSubCategories(doc)
    familyCatName = list(familyCat.keys())[0]
    # build output
    data = BuildReportDataByCategory(doc, familyCat, familyCatName, familyCatName, revitFilePath)
    data = data + BuildReportDataByCategory(doc, subCats, familyCatName, familyCatName, revitFilePath)
    for cat in otherCats:
        data = data + BuildReportDataByCategory(doc, otherCats[cat], familyCatName, cat, revitFilePath)
    return data
