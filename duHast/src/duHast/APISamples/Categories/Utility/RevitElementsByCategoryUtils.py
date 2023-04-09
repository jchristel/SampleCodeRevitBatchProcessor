'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Revit elements to category helper functions.
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

import Autodesk.Revit.DB as rdb

from duHast.APISamples.Common import RevitElementParameterSetUtils as rParaSet
from duHast.Utilities import Result as res
from duHast.APISamples.Links import RevitCadLinksGeometry as rCadLinkGeo
from duHast.APISamples.Family import RevitFamilyUtils as rFamUtils
from duHast.APISamples.Common import RevitElementParameterGetUtils as rParaGet

from duHast.APISamples.Categories.RevitCategories import ELEMENTS_PARAS_SUB, GetMainSubCategories
from duHast.APISamples.Categories.Utility.RevitCategoryPropertiesGetUtils import GetCategoryGraphicStyleIds
from duHast.APISamples.Categories.Utility.RevitCategoryPropertyNames import CATEGORY_GRAPHIC_STYLE_3D


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
    elImport = rCadLinkGeo.GetAllCADImportInstancesGeometry(doc)
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