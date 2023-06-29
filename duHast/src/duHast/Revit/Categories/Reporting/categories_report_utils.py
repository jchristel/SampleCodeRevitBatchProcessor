"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Revit category report functions .
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
#
# License:
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


from duHast.Revit.LinePattern import RevitLineStylesPatterns as rPat
from duHast.Revit.Categories.categories import (
    get_family_category,
    get_main_sub_categories,
    get_other_sub_categories,
)
from duHast.Revit.Categories.Utility.category_properties_get_utils import (
    get_category_colour,
    get_category_line_weights,
    get_category_material,
)
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
)
from duHast.Revit.Categories.Utility.elements_by_category_utils import (
    get_elements_by_category,
)


def build_report_data_by_category(doc, dic, family_cat, main_cat_name, doc_file_path):
    """
    Formats category properties into lists for reports
    :param doc: Current Revit family document.
    :type doc: Autodesk.Revit.DB.Document
    :param dic: dictionary containing category properties
    :type dic: _type_
    :param family_cat: The family category name.
    :type family_cat: str
    :param main_cat_name: A hard coded revit category name. Can be the same as familyCat.
    :type main_cat_name: str
    :param doc_file_path: The fully qualified family file path.
    :type doc_file_path: str
    :return: A list of list of strings. Each row represents one category.
    :rtype: list[list[str]]
    """

    data = []
    for key in dic:
        row = [
            str(doc_file_path).encode("utf-8"),
            family_cat.encode("utf-8"),
            main_cat_name.encode("utf-8"),
            key.encode("utf-8"),
            str(dic[key].Id),
        ]
        # get elements
        elements = get_elements_by_category(doc, dic[key])
        # get properties
        dic_material = get_category_material(dic[key])
        row.append(str(dic_material[PROPERTY_MATERIAL_NAME]).encode("utf-8"))
        row.append(str(dic_material[PROPERTY_MATERIAL_ID]).encode("utf-8"))
        # line pattern
        dic_pattern = rPat.GetLinePatternFromCategory(dic[key], doc)
        row.append(str(dic_pattern[rPat.PROPERTY_PATTERN_NAME]).encode("utf-8"))
        row.append(str(dic_pattern[rPat.PROPERTY_PATTERN_ID]).encode("utf-8"))
        # line weights
        dic_line_weights = get_category_line_weights(dic[key])
        row.append(
            str(dic_line_weights[PROPERTY_LINE_WEIGHT_PROJECTION_NAME]).encode("utf-8")
        )
        row.append(str(dic_line_weights[PROPERTY_LINE_WEIGHT_CUT_NAME]).encode("utf-8"))
        # category colour
        dic_colour = get_category_colour(dic[key])
        row.append(str(dic_colour[PROPERTY_LINE_COLOUR_RED_NAME]).encode("utf-8"))
        row.append(str(dic_colour[PROPERTY_LINE_COLOUR_GREEN_NAME]).encode("utf-8"))
        row.append(str(dic_colour[PROPERTY_LINE_COLOUR_BLUE_NAME]).encode("utf-8"))
        # elements
        row.append(str(len(elements[CATEGORY_GRAPHIC_STYLE_3D])).encode("utf-8"))
        row.append(
            str(len(elements[CATEGORY_GRAPHIC_STYLE_PROJECTION])).encode("utf-8")
        )
        row.append(str(len(elements[CATEGORY_GRAPHIC_STYLE_CUT])).encode("utf-8"))

        data.append(row)
    return data


def get_report_data(doc, revit_file_path):
    """
    Reports all categories, their properties and all elements belonging to them.
    :param doc: Current Revit family document.
    :type doc: Autodesk.Revit.DB.Document
    :param revit_file_path: The fully qualified family file path.
    :type revit_file_path: str
    :return: A list of list of strings. Each row represents one category.
    :rtype: list[list[str]]
    """

    data = []
    # get all sub categories in family and associates elements;
    sub_cats = get_main_sub_categories(
        doc
    )  # i/e family is specialty equipment and all its associated sub categories
    family_cat = get_family_category(
        doc
    )  # any 3D element which is set to 'None' in subcategory (if family is specialty equipment so is this element)
    other_cats = get_other_sub_categories(doc)  # Imports in Families cats are here
    family_cat_name = list(family_cat.keys())[0]
    # build output
    data = build_report_data_by_category(
        doc, family_cat, family_cat_name, family_cat_name, revit_file_path
    )
    data = data + build_report_data_by_category(
        doc, sub_cats, family_cat_name, family_cat_name, revit_file_path
    )
    # check for imports
    if "Imports in Families" in other_cats:
        data = data + build_report_data_by_category(
            doc,
            other_cats["Imports in Families"],
            family_cat_name,
            "Imports in Families",
            revit_file_path,
        )
    return data
