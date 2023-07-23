"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Revit sub-category property set functions .
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
from duHast.Revit.Common import transaction as rTran
from duHast.Utilities.Objects import result as res
from duHast.Revit.Categories.Utility.category_property_names import (
    PROPERTY_LINE_COLOUR_BLUE_NAME,
    PROPERTY_LINE_COLOUR_GREEN_NAME,
    PROPERTY_LINE_COLOUR_RED_NAME,
    PROPERTY_LINE_WEIGHT_CUT_NAME,
    PROPERTY_LINE_WEIGHT_PROJECTION_NAME,
    PROPERTY_MATERIAL_ID,
)
from duHast.Revit.Categories.Utility.category_properties_get_utils import (
    get_saved_category_property_by_name,
)


def set_category_material(doc, cat, material_id):
    """
    Updates material property of a given category.
    :param doc: Current Revit family document.
    :type doc: Autodesk.Revit.DB.Document
    :param cat: A category.
    :type cat: Autodesk.Revit.DB.Category
    :param material_id: The new material element id.
    :type material_id: Autodesk.Revit.DB.ElementId
    :return: True if material property was updated successfully, otherwise False.
    :rtype: bool
    """

    flag = True
    try:
        mat = doc.GetElement(material_id)

        def action():
            action_return_value = res.Result()
            try:
                cat.Material = mat
                action_return_value.update_sep(
                    True, "Successfully set material value of subcategory"
                )
            except Exception as e:
                action_return_value.update_sep(
                    False,
                    "Failed to set material value of subcategory with exception: {}".format(
                        e
                    ),
                )
            return action_return_value

        transaction = rdb.Transaction(
            doc, "Updating subcategory material: " + str(rdb.Element.Name.GetValue(mat))
        )
        update_mat = rTran.in_transaction(transaction, action)
        flag = update_mat.status
    except Exception as e:
        flag = False
    return flag


def set_category_line_pattern(doc, cat, line_pattern_id, ignore_missing_cut_style):
    """
    Updates line pattern property of a given category.
    Note: in cases where the 'cut' property does not exist on a sub category this will return false even though the 'projection' property will most
    likely have been updated without a problem...
    :param doc: Current Revit family document.
    :type doc: Autodesk.Revit.DB.Document
    :param cat: A category.
    :type cat: Autodesk.Revit.DB.Category
    :param line_pattern_id: The newline pattern element id.
    :type line_pattern_id: Autodesk.Revit.DB.ElementId
    :param ignore_missing_cut_style: If true will not flag an exception if applying styles fails on missing cut style.
    :type ignore_missing_cut_style: bool
    :return: True if line pattern property was updated successfully, otherwise False.
    :rtype: bool
    """

    flag = True
    try:

        def action():
            action_return_value = res.Result()
            try:
                cat.SetLinePatternId(line_pattern_id, rdb.GraphicsStyleType.Cut)
                action_return_value.update_sep(
                    True, "Successfully set cut line pattern of subcategory"
                )
            except Exception as e:
                if ignore_missing_cut_style:
                    action_return_value.update_sep(
                        True,
                        "Failed to set cut line pattern of subcategory with exception: {}. Exception ignored!".format(
                            e
                        ),
                    )
                else:
                    action_return_value.update_sep(
                        False,
                        "Failed to set cut line pattern of subcategory with exception: {}".format(
                            e
                        ),
                    )
            try:
                cat.SetLinePatternId(line_pattern_id, rdb.GraphicsStyleType.Projection)
                action_return_value.update_sep(
                    True, "Successfully set projection line pattern of subcategory"
                )
            except Exception as e:
                action_return_value.update_sep(
                    False,
                    "Failed to set projection line pattern of subcategory with exception: {}".format(
                        e
                    ),
                )
            return action_return_value

        transaction = rdb.Transaction(doc, "Updating subcategory line pattern")
        update_line_pattern = rTran.in_transaction(transaction, action)
        flag = update_line_pattern.status
    except Exception as e:
        flag = False
    return flag


def set_category_line_weights(
    doc, cat, line_thick_ness_cut, line_thickness_projection, ignore_missing_cut_style
):
    """
    Updates line weight properties of a given category.
    :param doc: Current Revit family document.
    :type doc: Autodesk.Revit.DB.Document
    :param cat: A category.
    :type cat: Autodesk.Revit.DB.Category
    :param line_thick_ness_cut: The cut line weight.
    :type line_thick_ness_cut: int
    :param line_thickness_projection: The projection line weight.
    :type line_thickness_projection: int
    :param ignore_missing_cut_style: If true will not flag an exception if applying styles fails on missing cut style.
    :type ignore_missing_cut_style: bool
    :return: True if line weight property was updated successfully, otherwise False.
    :rtype: bool
    """

    flag = True
    try:

        def action():
            action_return_value = res.Result()
            try:
                cat.SetLineWeight(line_thick_ness_cut, rdb.GraphicsStyleType.Cut)
                action_return_value.update_sep(
                    True, "Successfully set cut line weight of subcategory"
                )
            except Exception as e:
                if ignore_missing_cut_style:
                    action_return_value.update_sep(
                        True,
                        "Failed to set cut line weight of subcategory with exception: {}. Exception ignored!".format(
                            e
                        ),
                    )
                else:
                    action_return_value.update_sep(
                        False,
                        "Failed to set cut line weight of subcategory with exception: {}".format(
                            e
                        ),
                    )
            try:
                cat.SetLineWeight(
                    line_thickness_projection, rdb.GraphicsStyleType.Projection
                )
                action_return_value.update_sep(
                    True, "Successfully set projection line weight of subcategory"
                )
            except Exception as e:
                action_return_value.update_sep(
                    False,
                    "Failed to set projection line weight of subcategory with exception: {}".format(
                        e
                    ),
                )
            return action_return_value

        transaction = rdb.Transaction(doc, "Updating subcategory line weights")
        update_line_weights = rTran.in_transaction(transaction, action)
        flag = update_line_weights.status
    except Exception as e:
        flag = False
    return flag


def set_category_colour(doc, cat, red, green, blue):
    """
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
    """

    flag = True
    try:

        def action():
            action_return_value = res.Result()
            try:
                new_colour = rdb.Color(red, green, blue)
                cat.LineColor = new_colour
                action_return_value.update_sep(
                    True, "Successfully set colour value of subcategory"
                )
            except Exception as e:
                action_return_value.update_sep(
                    False,
                    "Failed to set colour value of subcategory with exception: {}".format(
                        e
                    ),
                )
            return action_return_value

        transaction = rdb.Transaction(doc, "Updating subcategory colour")
        update_colour = rTran.in_transaction(transaction, action)
        flag = update_colour.status
    except Exception as e:
        flag = False
    return flag


def set_category_properties(doc, cat, properties, ignore_missing_cut_style):
    """
    Updates varies property values of a given category.
    :param doc: Current Revit family document.
    :type doc: Autodesk.Revit.DB.Document
    :param cat: A category.
    :type cat: Autodesk.Revit.DB.Category
    :param properties: List of property values to be applied to category.
    :type properties: list of dictionaries in format as per GetCategoryProperties(cat) method.
    :param ignore_missing_cut_style: If true will not flag an exception if applying styles fails on missing cut style.
    :type ignore_missing_cut_style: bool
    :return: True if all properties where updated successfully, otherwise False.
    :rtype: bool
    """

    # material
    mat_id = get_saved_category_property_by_name(properties, [PROPERTY_MATERIAL_ID])
    flag_mat = set_category_material(doc, cat, mat_id[0])

    # line pattern
    line_pattern_id = get_saved_category_property_by_name(
        properties, [rPat.PROPERTY_PATTERN_ID]
    )
    flag_pattern = set_category_line_pattern(
        doc, cat, line_pattern_id[0], ignore_missing_cut_style
    )

    # line weights
    line_weights = get_saved_category_property_by_name(
        properties,
        [PROPERTY_LINE_WEIGHT_CUT_NAME, PROPERTY_LINE_WEIGHT_PROJECTION_NAME],
    )
    flag_line_weights = set_category_line_weights(
        doc, cat, line_weights[0], line_weights[1], ignore_missing_cut_style
    )

    # category colour
    colour_rgb = get_saved_category_property_by_name(
        properties,
        [
            PROPERTY_LINE_COLOUR_RED_NAME,
            PROPERTY_LINE_COLOUR_GREEN_NAME,
            PROPERTY_LINE_COLOUR_BLUE_NAME,
        ],
    )
    flag_colours = set_category_colour(
        doc, cat, colour_rgb[0], colour_rgb[1], colour_rgb[2]
    )

    return flag_mat & flag_pattern & flag_line_weights & flag_colours
