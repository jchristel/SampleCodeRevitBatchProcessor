"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Revit sub-category property get functions .
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright © 2023, Jan Christel
# All rights reserved.

# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

# - Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# - Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# - Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
#
# This software is provided by the copyright holder "as is" and any express or implied warranties, including, but not limited to, the implied warranties of merchantability and fitness for a particular purpose are disclaimed. 
# In no event shall the copyright holder be liable for any direct, indirect, incidental, special, exemplary, or consequential damages (including, but not limited to, procurement of substitute goods or services; loss of use, data, or profits; 
# or business interruption) however caused and on any theory of liability, whether in contract, strict liability, or tort (including negligence or otherwise) arising in any way out of the use of this software, even if advised of the possibility of such damage.
#
#
#


import Autodesk.Revit.DB as rdb
from duHast.Revit.LinePattern import line_patterns as rPat
from duHast.Revit.Categories.Utility.category_property_names import (
    CATEGORY_GRAPHIC_STYLE_3D,
    CATEGORY_GRAPHIC_STYLE_CUT,
    CATEGORY_GRAPHIC_STYLE_PROJECTION,
    PROPERTY_LINE_COLOUR_BLUE_NAME,
    PROPERTY_LINE_COLOUR_GREEN_NAME,
    PROPERTY_LINE_COLOUR_RED_NAME,
    PROPERTY_LINE_WEIGHT_CUT_NAME,
    PROPERTY_LINE_WEIGHT_PROJECTION_NAME,
    PROPERTY_MATERIAL_ID,
    PROPERTY_MATERIAL_NAME,
    PROPERTY_MATERIAL_NAME_VALUE_DEFAULT,
)


def get_category_graphic_style_ids(cat):
    """
    Returns a dictionary with keys: Projection, Cut, 3D and their respective ids
    :param cat: A category.
    :type cat: Autodesk.REvit.DB.Category
    :return: A dictionary
    :rtype: dictionary {str: Autodesk.Revit.DB.ElementId}
    """

    i_d_graphic_style_projection = cat.GetGraphicsStyle(
        rdb.GraphicsStyleType.Projection
    ).Id

    # check if this category has a cut style ( some families always appear in elevation only!)
    graphic_style_cut = cat.GetGraphicsStyle(rdb.GraphicsStyleType.Cut)
    # set as default invalid element id
    i_d_graphic_style_cut = rdb.ElementId.InvalidElementId
    if graphic_style_cut != None:
        i_d_graphic_style_cut = cat.GetGraphicsStyle(rdb.GraphicsStyleType.Cut).Id
    # build category dictionary where key is the style type, values is the corresponding Id
    dic = {}
    dic[CATEGORY_GRAPHIC_STYLE_PROJECTION] = i_d_graphic_style_projection
    dic[CATEGORY_GRAPHIC_STYLE_CUT] = i_d_graphic_style_cut
    dic[CATEGORY_GRAPHIC_STYLE_3D] = cat.Id
    return dic


def get_category_material(cat):
    """
    Returns the material properties name and id as a dictionary where key is property name and\
         value the property id.
    :param cat: A category.
    :type cat: Autodesk.REvit.DB.Category
    :return: A dictionary
    :rtype: dictionary {str: Autodesk.Revit.DB.ElementId}\
        If no material is assigned to a category it will return {'None: Autodesk.Revit.DB.ElementId.InvalidElementId}
    """

    dic_material = {}
    dic_material[PROPERTY_MATERIAL_NAME] = PROPERTY_MATERIAL_NAME_VALUE_DEFAULT
    dic_material[PROPERTY_MATERIAL_ID] = rdb.ElementId.InvalidElementId
    material = cat.Material
    if material != None:
        dic_material[PROPERTY_MATERIAL_NAME] = rdb.Element.Name.GetValue(material)
        dic_material[PROPERTY_MATERIAL_ID] = material.Id
    return dic_material


def get_category_line_weights(cat):
    """
    Returns the line weight properties (cut and projection) as a dictionary\
         where key is property description and value the property value
    :param cat: A category.
    :type cat: Autodesk.Revit.DB.Category
    :return: A dictionary.
    :rtype: dictionary {str: nullable integer}
    """

    dic_line_weights = {}
    dic_line_weights[PROPERTY_LINE_WEIGHT_PROJECTION_NAME] = cat.GetLineWeight(
        rdb.GraphicsStyleType.Projection
    )
    dic_line_weights[PROPERTY_LINE_WEIGHT_CUT_NAME] = cat.GetLineWeight(
        rdb.GraphicsStyleType.Cut
    )
    return dic_line_weights


def get_category_colour(cat):
    """
    Returns the colour properties (RGB) and values as a dictionary where key is colour name\
         and value the property value
    :param cat: A category.
    :type cat: Autodesk.Revit.DB.Category
    :return: A dictionary.
    :rtype: dictionary {str: byte}
    """

    dic_colour = {}
    dic_colour[PROPERTY_LINE_COLOUR_RED_NAME] = 0
    dic_colour[PROPERTY_LINE_COLOUR_GREEN_NAME] = 0
    dic_colour[PROPERTY_LINE_COLOUR_BLUE_NAME] = 0
    if cat.LineColor.IsValid:
        dic_colour[PROPERTY_LINE_COLOUR_RED_NAME] = cat.LineColor.Red
        dic_colour[PROPERTY_LINE_COLOUR_GREEN_NAME] = cat.LineColor.Green
        dic_colour[PROPERTY_LINE_COLOUR_BLUE_NAME] = cat.LineColor.Blue
    return dic_colour


def get_category_properties(cat, doc):
    """
    Returns a dictionary where keys are category property names and value is the associated property value.
    :param cat: A category.
    :type cat: Autodesk.Revit.DB.Category
    :param doc: Current Revit family document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A dictionary.
    :rtype: list [{str: var}]
    """

    properties = []

    # material
    dic_material = get_category_material(cat)
    properties.append(dic_material)

    # line pattern
    dic_pattern = rPat.get_line_pattern_from_category(cat, doc)
    properties.append(dic_pattern)

    # line weights
    dic_line_weights = get_category_line_weights(cat)
    properties.append(dic_line_weights)

    # category colour
    dic_colour = get_category_colour(cat)
    properties.append(dic_colour)
    return properties


def get_saved_category_property_by_name(properties, prop_names):
    """
    Returns property values matching property names in saved category data.
    :param properties: List of dictionaries in format as per GetCategoryProperties(cat) method.
    :type properties: list [{str: var}]
    :param prop_names: List of property names of which the values are to be returned
    :type prop_names: list str
    :return: A list of values.
    :rtype: list var
    """

    prop_values = []
    for prop_name in prop_names:
        match = False
        for saved_prop in properties:
            if prop_name in saved_prop:
                prop_values.append(saved_prop[prop_name])
                match = True
        if match == False:
            prop_values.append(None)
    return prop_values
