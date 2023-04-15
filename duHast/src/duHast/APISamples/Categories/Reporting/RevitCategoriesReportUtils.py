'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Revit category report functions .
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


from duHast.APISamples.LinePattern import RevitLineStylesPatterns as rPat
from duHast.APISamples.Categories.RevitCategories import get_family_category, get_main_sub_categories, get_other_sub_categories
from duHast.APISamples.Categories.Utility.RevitCategoryPropertiesGetUtils import get_category_colour, get_category_line_weights, get_category_material
from duHast.APISamples.Categories.Utility.RevitCategoryPropertyNames import CATEGORY_GRAPHIC_STYLE_3D, CATEGORY_GRAPHIC_STYLE_CUT, CATEGORY_GRAPHIC_STYLE_PROJECTION, PROPERTY_LINE_COLOUR_BLUE_NAME, PROPERTY_LINE_COLOUR_GREEN_NAME, PROPERTY_LINE_COLOUR_RED_NAME, PROPERTY_LINE_WEIGHT_CUT_NAME, PROPERTY_LINE_WEIGHT_PROJECTION_NAME, PROPERTY_MATERIAL_ID, PROPERTY_MATERIAL_NAME
from duHast.APISamples.Categories.Utility.RevitElementsByCategoryUtils import get_elements_by_category


def build_report_data_by_category(doc, dic, familyCat, mainCatName, docFilePath):
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
        elements = get_elements_by_category (doc, dic[key])
        # get properties
        dicMaterial = get_category_material(dic[key])
        row.append(str(dicMaterial[PROPERTY_MATERIAL_NAME]).encode('utf-8'))
        row.append(str(dicMaterial[PROPERTY_MATERIAL_ID]).encode('utf-8'))
        # line pattern
        dicPattern = rPat.GetLinePatternFromCategory(dic[key], doc)
        row.append(str(dicPattern[rPat.PROPERTY_PATTERN_NAME]).encode('utf-8'))
        row.append(str(dicPattern[rPat.PROPERTY_PATTERN_ID]).encode('utf-8'))
        # line weights
        dicLineWeights = get_category_line_weights(dic[key])
        row.append(str(dicLineWeights[PROPERTY_LINE_WEIGHT_PROJECTION_NAME]).encode('utf-8'))
        row.append(str(dicLineWeights[PROPERTY_LINE_WEIGHT_CUT_NAME]).encode('utf-8'))
        # category colour
        dicColour = get_category_colour(dic[key])
        row.append(str(dicColour[PROPERTY_LINE_COLOUR_RED_NAME]).encode('utf-8'))
        row.append(str(dicColour[PROPERTY_LINE_COLOUR_GREEN_NAME]).encode('utf-8'))
        row.append(str(dicColour[PROPERTY_LINE_COLOUR_BLUE_NAME]).encode('utf-8'))
        # elements
        row.append(str(len(elements[CATEGORY_GRAPHIC_STYLE_3D])).encode('utf-8'))
        row.append(str(len(elements[CATEGORY_GRAPHIC_STYLE_PROJECTION])).encode('utf-8'))
        row.append(str(len(elements[CATEGORY_GRAPHIC_STYLE_CUT])).encode('utf-8'))

        data.append(row)
    return data


def get_report_data(doc, revitFilePath):
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
    subCats = get_main_sub_categories(doc) # i/e family is specialty equipment and all its associated sub categories
    familyCat = get_family_category(doc) # any 3D element which is set to 'None' in subcategory (if family is specialty equipment so is this element)
    otherCats = get_other_sub_categories(doc) # Imports in Families cats are here
    familyCatName = list(familyCat.keys())[0]
    # build output
    data = build_report_data_by_category(doc, familyCat, familyCatName, familyCatName, revitFilePath)
    data = data + build_report_data_by_category(doc, subCats, familyCatName, familyCatName, revitFilePath)
    # check for imports
    if ('Imports in Families' in otherCats):
        data = data + build_report_data_by_category(doc, otherCats['Imports in Families'], familyCatName, 'Imports in Families', revitFilePath)
    return data