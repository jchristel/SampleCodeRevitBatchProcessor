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

import sys
sys.path.append('C:\Users\jchristel\Documents\deployRevitBP')

import RevitCommonAPI as com
import RevitFamilyUtils as rFamUtils
import Result as res

clr.AddReference('System.Core')
clr.ImportExtensions(System.Linq)
from Autodesk.Revit.DB import *


CAT_RENAMING = {
    'Clearance Zones': 'AMAZING'
}

# list of built in parameters attached to elements containing subcategory ids
ELEMENTS_PARAS_SUB = [
    BuiltInParameter.FAMILY_CURVE_GSTYLE_PLUS_INVISIBLE,
    BuiltInParameter.FAMILY_CURVE_GSTYLE_PLUS_INVISIBLE_MINUS_ANALYTICAL,
    BuiltInParameter.FAMILY_ELEM_SUBCATEGORY
]


#-------------------------- get category properties ---------------------------------

# category properties dictioanry key names and default values
PROPERTY_MATERIAL_NAME = 'MaterialName'
PROPERTY_MATERIAL_NAME_VALUE_DEFAULT = 'None'
PROPERTY_MATERIAL_ID = 'MaterialId'

PROPERTY_PATTERN_NAME = 'PatternName'
PROPERTY_PATTERN_NAME_VALUE_DEFAULT = 'Solid' # hard coded solid line pattern name
PROPERTY_PATTERN_ID = 'PatternId'

PROPERTY_LINEWEIGHT_PROJECTION_NAME = 'LineWeightProjection'
PROPERTY_LINEWEIGHT_CUT_NAME = 'LineWeightCut'

PROPERTY_LINECOLOUR_RED_NAME = 'Red'
PROPERTY_LINECOLOUR_GREEN_NAME = 'Green'
PROPERTY_LINECOLOUR_BLUE_NAME = 'Blue'


# graphic styles used for elements in familis
CATEGORY_GRAPHICSTYLE_PROJECTION = 'Projection'
CATEGORY_GRAPHICSTYLE_CUT = 'Cut'
CATEGORY_GRAPHICSTYLE_3D = '3D'


# -------------------------------------------- common variables --------------------
# header used in reports
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


# doc   current family document
def GetMainSubCategories(doc):
    '''
    reports all subcategories of the family category in a dictionary where
    key: sub category name
    data: sub category 
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

# doc   current family document
def GetFamilyCategory(doc):
    '''
    reports family category in a dictionary where
    key: category name
    data: category 
    '''
    catData = {}
    # get the family category
    currentFamCat = doc.OwnerFamily.FamilyCategory
    catData [currentFamCat.Name] = currentFamCat
    return catData

# doc   current family document
def GetOtherSubCategories(doc):
    '''
    reports all family sub categories which do not belong to the actual family category
    note: custom categories have an Id greater 0
    key: category name
    data: dictionary : key sub cat name, data: subcategory
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
            for subcat in mainCat.SubCategories:
                catData[mainCat.Name][subcat.Name] = subcat
              
    return catData

#  cat    revit category
def GetCategoryGraphicStyleIds(cat):
    '''
    returns dic with keys: Projection, Cut, 3D and their respective ids
    '''
    iDGraphicStyleProjection = cat.GetGraphicsStyle(GraphicsStyleType.Projection).Id
    
    # check if this category has a cut style ( some families always appear in elevation only!)
    graphicStyleCut = cat.GetGraphicsStyle(GraphicsStyleType.Cut)
    # set as default the same as the projection style since that seems to be always available
    iDGraphicStyleCut = iDGraphicStyleProjection
    if(graphicStyleCut != None):
        iDGraphicStyleCut = cat.GetGraphicsStyle(GraphicsStyleType.Cut).Id
    # build category dictioanry where key is the style type, values is the coresponding Id
    dic = {}
    dic[CATEGORY_GRAPHICSTYLE_PROJECTION] = iDGraphicStyleProjection 
    dic[CATEGORY_GRAPHICSTYLE_CUT] = iDGraphicStyleCut
    dic[CATEGORY_GRAPHICSTYLE_3D] = cat.Id
    return dic

#  cat    revit category
def GetCategoryMaterial(cat):
    '''
    returns the material properties name and id as a dictionary where key is property description and value the property value
    '''
    dicMaterial = {}
    dicMaterial[PROPERTY_MATERIAL_NAME] = PROPERTY_MATERIAL_NAME_VALUE_DEFAULT
    dicMaterial[PROPERTY_MATERIAL_ID] = ElementId.InvalidElementId
    material = cat.Material
    if(material != None):
        dicMaterial[PROPERTY_MATERIAL_NAME] = Element.Name.GetValue(material)
        dicMaterial[PROPERTY_MATERIAL_ID] = material.Id
    return dicMaterial

#  cat    revit category
def GetCategoryLinePattern(cat, doc):
    '''
    returns the line pattern properties name and id as a dictionary where key is property description and value the property value
    '''
    dicPattern = {}
    dicPattern[PROPERTY_PATTERN_NAME] = PROPERTY_PATTERN_NAME_VALUE_DEFAULT
    dicPattern[PROPERTY_PATTERN_ID] = patternId = cat.GetLinePatternId(GraphicsStyleType.Projection)
    '''check for 'solid' pattern which apparently is not a pattern at all
    *The RevitAPI.chm documents says: Note that Solid is special. It isn't a line pattern at all -- 
    * it is a special code that tells drawing and export code to use solid lines rather than patterned lines. 
    * Solid is visible to the user when selecting line patterns. 
    '''
    if(patternId != LinePatternElement.GetSolidPatternId()):
        # not a solid line pattern
        collector = FilteredElementCollector(doc).OfClass(LinePatternElement)
        linePatternElement = None
        for c in collector:
            if(patternId == c.Id):
                dicPattern[PROPERTY_PATTERN_NAME] = Element.Name.GetValue(c)         
    return dicPattern

#  cat    revit category
def GetCategoryLineWeights(cat):
    '''
    returns the line weight properties (cut and projection) and values as a dictionary where key is property description and value the property value
    '''
    dicLineWeights = {}
    dicLineWeights[PROPERTY_LINEWEIGHT_PROJECTION_NAME] = cat.GetLineWeight(GraphicsStyleType.Projection)
    dicLineWeights[PROPERTY_LINEWEIGHT_CUT_NAME] = cat.GetLineWeight(GraphicsStyleType.Cut)
    return dicLineWeights

#  cat    revit category
def GetCategoryColour(cat):
    '''
    returns the colour properties (RGB) and values as a dictionary where key is property description and value the property value
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

# cat   category
def GetCategoryProperties(cat, doc):
    '''
    returns a dictionary where keys are property names and value is the associated property value
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

# properties    list of dictionaries in format as per GetCategoryProperties(cat) method
# propNames     list of proprty names of which the values are to be returned
def GetSavedCategoryPropertyByName(properties, propNames):
    '''
    returns property values matching property names in saved category data
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

# doc           family document
# cat           category
# materialId    material id to be assigned to category
def SetCategoryMaterial(doc, cat, materialId):
    '''
    updates material property of a given category
    '''
    flag = True
    try:
        mat = doc.GetElement(materialId)
        def action():
            cat.Material = mat
        transaction = Transaction(doc,'Updating subcategory material: ' + str(Element.Name.GetValue(mat)))
        updateMat = com.InTransaction(transaction, action)
    except Exception as e:
        print('SetCategoryMaterial ' + str(e))
        flag = False
    return flag
    
# doc               family document
# cat               category
# linePatternId     line pattern id to be assigned to category
def SetCategoryLinePattern(doc, cat, linePatternId):
    '''
    updates line pattern property of a given category
    '''
    flag = True
    try:
        def action():
            cat.SetLinePatternId(linePatternId, GraphicsStyleType.Cut)
            cat.SetLinePatternId(linePatternId, GraphicsStyleType.Projection)
        transaction = Transaction(doc,'Updating subcategory line pattern')
        updateLinePattern = com.InTransaction(transaction, action)
    except Exception as e:
        print('SetCategoryLinePattern ' + str(e))
        flag = False
    return flag

# doc                         family document
# cat                         category
# lineThickNessCut            integer value
# lineThickNessProjection     integer value
def SetCategoryLineWeights(doc, cat, lineThickNessCut, lineThicknessProjection):
    '''
    updates line weight properties of a given category
    '''
    flag = True
    try:
        def action():
            cat.SetLineWeight(lineThickNessCut, GraphicsStyleType.Cut)
            cat.SetLineWeight(lineThicknessProjection, GraphicsStyleType.Projection)
        transaction = Transaction(doc,'Updating subcategory line weights')
        updateLineWeights = com.InTransaction(transaction, action)
    except Exception as e:
        print('SetCategoryLineWeights:' + str(e))
        flag = False
    return flag

# doc     family document
# cat     category
# red     byte value for red
# green   byte value for green
# blue    byte value for blue
def SetCategoryColour(doc, cat, red, green, blue):
    '''
    updates colour properties of a given category
    '''
    flag = True
    try:
        def action():
            newColour = Color(red, green, blue)
            cat.LineColor = newColour
        transaction = Transaction(doc,'Updating subcategory colour')
        updateColour = com.InTransaction(transaction, action)
    except Exception as e:
        print('SetCategoryColour ' + str(e))
        flag = False
    return flag

# cat   category of which properties are to be changed
# properties    list of dictionaries in format as per GetCategoryProperties(cat) method
def SetCategoryProperties(cat, properties):
    '''
    updates property values of a given category
    '''
    flag = True
    
    # material
    matId = GetSavedCategoryPropertyByName(properties, [PROPERTY_MATERIAL_ID])
    flagMat = SetCategoryMaterial(doc, cat, matId[0])
    
    # line pattern
    linePatternId = GetSavedCategoryPropertyByName(properties, [PROPERTY_PATTERN_ID])
    flagPattern = SetCategoryLinePattern(doc, cat, linePatternId[0])
    
    # line weights
    lineWeights = GetSavedCategoryPropertyByName(properties, [PROPERTY_LINEWEIGHT_CUT_NAME, PROPERTY_LINEWEIGHT_PROJECTION_NAME])
    flagLineweights = SetCategoryLineWeights(doc, cat, lineWeights[0], lineWeights[1])
    
    # category colour
    colourRGB = GetSavedCategoryPropertyByName(properties, [PROPERTY_LINECOLOUR_RED_NAME, PROPERTY_LINECOLOUR_GREEN_NAME, PROPERTY_LINECOLOUR_BLUE_NAME])
    flagColours = SetCategoryColour(doc, cat, colourRGB[0], colourRGB[1], colourRGB[2])
    
    return flagMat & flagPattern & flagLineweights & flagColours

#-------------------------- utilities ---------------------------------

# doc                       current family document
# newCategoryName           the name of the new familyncategory
def SetFamilyCategory(doc, newCategoryName):
    '''
    changes the family category to new one specified by name.
    Returns true only if the category was changed. Any other case is false! (that includes situations when the family is already of the new catgeory)
    '''
    returnvalue = res.Result()
    cat = doc.OwnerFamily.FamilyCategory
    if (cat.Name != newCategoryName):
        if (doc.Settings.Categories.Contains(newCategoryName)):
            def action():
                doc.OwnerFamily.FamilyCategory = doc.Settings.Categories.get_Item(newCategoryName)
            transaction = Transaction(doc,'Changing family category to:' + str(newCategoryName))
            changeCat = com.InTransaction(transaction, action)
            if(changeCat.status):
                returnvalue.UpdateSep(True, 'Succesfully changed family category to: '+str(newCategoryName))
            else:
                returnvalue.Update(changeCat)
        else:
            returnvalue.UpdateSep(False, 'Invalid Category name supplied: ' + str(newCategoryName))
    else:
        returnvalue.UpdateSep(False, 'Family is already of category: '+str(newCategoryName))
    return returnvalue

# doc                   current family document
# newSubCategoryName    the new subcategroy name
def CreateNewSubCategoryToFamilyCategory(doc, newSubCategoryName):
    '''
    creates a new subcategory to the family category and returns it
    returns exception "The name 'xys' is already in use" if category with the same name is already in file
    '''
    returnvalue = res.Result()
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
                    newSubcategory = doc.Settings.Categories.NewSubcategory(parentCategory, newSubCategoryName)
                    actionReturnValue.UpdateSep(True, 'Created subcategory ' + str(newSubCategoryName))
                    actionReturnValue.result = newSubcategory
                except Exception as e:
                    actionReturnValue.UpdateSep(False, 'Failed to create ' + str(newSubCategoryName) + ' with exception: ' + str(e))
                return actionReturnValue
            transaction = Transaction(doc,'Creating subcategory: ' + str(newSubCategoryName))
            returnvalue = com.InTransaction(transaction, action)
        else:
          returnvalue.UpdateSep(False, 'Cant create subcategory with the same name as the family category!')
    else:
        returnvalue.UpdateSep(False, 'This is not a family document!')
    return returnvalue

# elements              list of revit elements
# elememtDic            dictionary where key is category and values are element ids
def SortElementsByCategory(elements, elementDic):
    '''
    returns a dicionary of element ids where key is the 
    category
    '''
    for el in elements:
        for builinDef in ELEMENTS_PARAS_SUB:
            value = com.GetBuiltInParameterValue(el, builinDef)
            if (value != None):
                if(value in elementDic):
                    elementDic[value].append(el.Id)
                else:
                    elementDic[value] = [el.Id]
                break
    return elementDic

# doc                   current family document
# cat                   category to which the elements are assigned
def GetElementsByCategory(doc, cat):
    '''
    returns elements in family assign to a specific category
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
        categoryIds[CATEGORY_GRAPHICSTYLE_3D] = ElementId.InvalidElementId
    dicFiltered = {}
    # filter elements by category ids
    for key,value in categoryIds.items():
        # print (key + ' ' + str(value))
        if value in dic:
            dicFiltered[key] = dic[value]
        else:
            dicFiltered[key] = []
    return dicFiltered

# doc                   current family document
def GetUsedCategoryIds(doc):
    '''
    returns all category ids in a family which have an element assigned to them
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

# doc                   current family document
# newCatName            name of category to be created
# existingCatName       exisitng category of which to clone properties
def CreateNewCategoryAndTransferProperties(doc, newCatName, existingCatName):
    '''
    creates a new category and applies properties from existing category, Returns new category
    if category already exists in file it will return that
    '''
    returnvalue = res.Result()
    cats = GetMainSubCategories(doc)
    # check if existing category actually exists in family
    if(existingCatName in cats):
        # check whether the new category already exists!
        if (newCatName not in cats):
            copyFromCat = cats[existingCatName]
            catProps = GetCategoryProperties(copyFromCat, doc)
            resultNewSubCat = CreateNewCategoryFromSavedProperties(doc, newCatName, catProps)
            returnvalue.Update(resultNewSubCat)
        else:
            returnvalue.UpdateSep(True, 'Category already in file:'+ str(newCatName))
            returnvalue.result = cats[newCatName]
    else:
        returnvalue.UpdateSep(False, 'Template category '+ str(existingCatName) + ' does not exist in file!')
    return returnvalue

# doc                   current family document
# newCatName            name of category to be created
# savedCatProps         existtng category properties
def CreateNewCategoryFromSavedProperties(doc, newCatName, savedCatProps):
    '''
    creates a new category and applies properties stored , Returns new category
    if category already exists in file it will return that
    '''
    returnvalue = res.Result()
    resultNewSubCat = CreateNewSubCategoryToFamilyCategory(doc, newCatName)
    if(resultNewSubCat.result):
        newSubcat = resultNewSubCat.result
        flag = SetCategoryProperties(newSubcat, savedCatProps)
        if(flag):
            returnvalue.UpdateSep(True, 'Succesfully created category '+ str(newCatName))
            returnvalue.result = newSubcat
        else:
            returnvalue.UpdateSep(False, 'Failed to apply properties to new category: '+ str(newCatName))
    return returnvalue

# doc                         current family document
# fromCategoryName            name of source category
# toCategoryName              name of destination category
def MoveElementsFromSubCategoryToSubCategory(doc, fromCategoryName, toCategoryName):
    '''
    moves elements from one category to another specified by their names
    '''
    returnvalue = res.Result()
    # check whether source and destination category exist in file
    cats = GetMainSubCategories(doc)
    if(fromCategoryName in cats):
        if(toCategoryName in cats):
            # dictionary containing destination catgory ids (3D, cut and projection)
            destinationCatIds = GetCategoryGraphicStyleIds(cats[toCategoryName])
            # get elements on source category
            dic = GetElementsByCategory(doc, cats[fromCategoryName])
            # move elements
            returnvalue = MoveElementsToCategory(doc, dic, toCategoryName, destinationCatIds)
        else:
            returnvalue.UpdateSep(False, 'Destination category '+ str(toCategoryName) + ' does not exist in file!')
    else:
       returnvalue.UpdateSep(False, 'Source category '+ str(fromCategoryName) + ' does not exist in file!')
    return returnvalue

# doc                           current family document
# elements                      dictionary of elements, key are graphic style names
# toCategoryName                name of destination category
# destinationCatIds             dictionary of ids of graphic styleids, key are graphic style names
def MoveElementsToCategory(doc, elements, toCategoryName, destinationCatIds):
    '''
    moves elements provided in dictionary another category specified by their names
    '''
    returnvalue = res.Result()
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
                                updataPara = com.setParameterValue(p, str(targetId), doc)
                                returnvalue.Update(updataPara)
                                break
    else:
        returnvalue.UpdateSep(False, 'Destination category '+ str(toCategoryName) + ' does not exist in file!')
    return returnvalue

# doc                       current family document
# newCategoryName           the name of the new familyncategory
def ChangeFamilyCategory(doc, newCategoryName):
    '''
    changes the current family category to the new one specified
    it will also transfer any user created subcategories to the new category and assign elements to it
    '''
    returnvalue = res.Result()
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
            # only re-create custom sub cagtegories (id greater then 0)
            if(subCats[subCat].Id.IntegerValue > 0):
                createCat = CreateNewCategoryFromSavedProperties(doc, subCat, props[subCat])
                if(createCat.status):
                    # move elements back onto custom subcategories
                    moveEl = MoveElementsToCategory(doc, elements[subCat], subCat, props[subCat])
                    returnvalue.Update(moveEl)
                else:
                    returnvalue.Update(createCat)
    else:
        returnvalue.UpdateSep(False, 'Failed to change family category:' + changeFam.message)
    return returnvalue
    
# doc                           current family document
# dic                           dictionary containing category properties
# familyCat                     family category name
# mainCatName                   hard coded revit category name
# docFilePath                   family file path
def BuildReportDataByCategory(doc, dic, familyCat, mainCatName, docFilePath):
    '''
    formats category properties into lists for reports
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

# doc                           current family document
# revitFilePath                 document file path
def GetReportData(doc, revitFilePath):
    '''
    reports all categories, properties and all elements belonging to them
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
