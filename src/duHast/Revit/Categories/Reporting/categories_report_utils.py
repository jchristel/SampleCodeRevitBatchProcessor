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
# BSD License
# Copyright 2023, Jan Christel
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


from duHast.Revit.LinePattern.line_patterns import (
    get_line_pattern_from_category,
    PROPERTY_PATTERN_NAME,
    PROPERTY_PATTERN_ID,
)

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

from duHast.Utilities.utility import encode_utf8


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
            encode_utf8(str(doc_file_path)),
            encode_utf8(family_cat),
            encode_utf8(main_cat_name),
            encode_utf8(key),
            str(dic[key].Id),
        ]
        # get elements
        elements = get_elements_by_category(doc, dic[key])
        # get properties
        dic_material = get_category_material(dic[key])
        row.append(encode_utf8(str(dic_material[PROPERTY_MATERIAL_NAME])))
        row.append(encode_utf8(str(dic_material[PROPERTY_MATERIAL_ID])))
        # line pattern
        dic_pattern = get_line_pattern_from_category(dic[key], doc)
        row.append(encode_utf8(str(dic_pattern[PROPERTY_PATTERN_NAME])))
        row.append(encode_utf8(str(dic_pattern[PROPERTY_PATTERN_ID])))
        # line weights
        dic_line_weights = get_category_line_weights(dic[key])
        row.append(
            encode_utf8(str(dic_line_weights[PROPERTY_LINE_WEIGHT_PROJECTION_NAME]))
        )
        row.append(encode_utf8(str(dic_line_weights[PROPERTY_LINE_WEIGHT_CUT_NAME])))
        # category colour
        dic_colour = get_category_colour(dic[key])
        row.append(encode_utf8(str(dic_colour[PROPERTY_LINE_COLOUR_RED_NAME])))
        row.append(encode_utf8(str(dic_colour[PROPERTY_LINE_COLOUR_GREEN_NAME])))
        row.append(encode_utf8(str(dic_colour[PROPERTY_LINE_COLOUR_BLUE_NAME])))
        # elements
        row.append(encode_utf8(str(len(elements[CATEGORY_GRAPHIC_STYLE_3D]))))
        row.append(encode_utf8(str(len(elements[CATEGORY_GRAPHIC_STYLE_PROJECTION]))))
        row.append(encode_utf8(str(len(elements[CATEGORY_GRAPHIC_STYLE_CUT]))))

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
