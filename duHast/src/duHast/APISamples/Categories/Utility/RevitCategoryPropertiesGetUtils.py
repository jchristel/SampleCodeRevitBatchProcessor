'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Revit sub-category property get functions .
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
from duHast.APISamples.LinePattern import RevitLineStylesPatterns as rPat
from duHast.APISamples.Categories.Utility.RevitCategoryPropertyNames import CATEGORY_GRAPHIC_STYLE_3D, CATEGORY_GRAPHIC_STYLE_CUT, CATEGORY_GRAPHIC_STYLE_PROJECTION, PROPERTY_LINE_COLOUR_BLUE_NAME, PROPERTY_LINE_COLOUR_GREEN_NAME, PROPERTY_LINE_COLOUR_RED_NAME, PROPERTY_LINE_WEIGHT_CUT_NAME, PROPERTY_LINE_WEIGHT_PROJECTION_NAME, PROPERTY_MATERIAL_ID, PROPERTY_MATERIAL_NAME, PROPERTY_MATERIAL_NAME_VALUE_DEFAULT


def get_category_graphic_style_ids(cat):
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


def get_category_material(cat):
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


def get_category_line_weights(cat):
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


def get_category_colour(cat):
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


def get_category_properties(cat, doc):
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
    dicMaterial = get_category_material(cat)
    properties.append(dicMaterial)

    # line pattern
    dicPattern = rPat.GetLinePatternFromCategory(cat, doc)
    properties.append(dicPattern)

    # line weights
    dicLineWeights = get_category_line_weights(cat)
    properties.append(dicLineWeights)

    # category colour
    dicColour = get_category_colour(cat)
    properties.append(dicColour)
    return properties


def get_saved_category_property_by_name(properties, propNames):
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