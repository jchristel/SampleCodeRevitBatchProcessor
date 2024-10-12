"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Revit category graphics helper functions for project files.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

#
#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2024, Jan Christel
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

import duHast.Utilities.Objects.result as res
from duHast.Revit.LinePattern.line_patterns import get_all_line_patterns
from duHast.Revit.Categories.categories_model import get_categories_in_model
from duHast.Revit.Categories.Objects.object_style import ObjectStyle

from duHast.Revit.Common.Objects.Data.line_projection import LineProjection
from duHast.Revit.Common.Objects.Data.line_cut import LineCut

from duHast.Revit.LinePattern.Data.Objects.line_pattern_settings import (
    LinePatternSettings,
)
from duHast.Revit.Views.Utility.convert_revit_override_to_data import (
    _get_name_from_pattern_id,
)
from duHast.Revit.Common.Utility.revit_to_data_conversion import to_colour
from duHast.Revit.Common.transaction import in_transaction
from duHast.Revit.Materials.materials import get_material_by_id


from Autodesk.Revit.DB import (
    Category,
    Color,
    Document,
    ElementId,
    GraphicsStyleType,
    Transaction,
)


def set_cut_style(doc, category, line_cut_style):
    """
    Sets line cut settings for a category object.

    :param doc: A Revit Document object
    :type doc: Autodesk.Revit.DB.Document
    :param category: A Revit Category object
    :type category: Autodesk.Revit.DB.Category
    :param line_patterns: All line patterns in the model
    :type line_patterns: [AutoDesk.Revit.LinePatternElement]
    :param line_cut_style: An overrides projections object instance.
    :type line_cut_style: :class:`.LineCut`
    """

    return_value = res.Result()
    try:

        # check if doc is a Revit Document object
        if isinstance(doc, Document) == False:
            raise TypeError("doc must be a Revit Document object")

        # check if category is a Revit Category object
        if isinstance(category, Category) == False:
            raise TypeError("category must be a Revit Category object")

        # check if line_cut_style is a LineCut object
        if isinstance(line_cut_style, LineCut) == False:
            raise TypeError("line_cut_style must be a LineCut object")

        # start
        def action():
            action_return_value = res.Result()
            try:
                # set cut line settings
                category.SetLineWeight(line_cut_style.weight, GraphicsStyleType.Cut)
                new_colour = Color(
                    line_cut_style.colour.red,
                    line_cut_style.colour.green,
                    line_cut_style.colour.blue,
                )

                # set the colour value
                category.LineColor = new_colour

                # set line pattern by id
                # use projection as graphics style since cut is not available (?)
                category.SetLinePatternId(
                    ElementId(line_cut_style.line_pattern_settings.id),
                    GraphicsStyleType.Projection,
                )
                action_return_value.update_sep(
                    True,
                    "Successfully updated cut style of category: {}".format(
                        category.Name
                    ),
                )
            except Exception as e:
                action_return_value.update_sep(
                    False,
                    "Failed to set cut style of category {} with exception: {}".format(
                        category.Name, e
                    ),
                )
            return action_return_value

        transaction = Transaction(doc, "Updating cut style: {}".format(category.Name))
        update_colour = in_transaction(transaction, action)
        return_value.update(update_colour)
    except Exception as e:
        return_value.update_sep(
            "failed to update cut style with exception: {}".format(e)
        )
    return return_value


def get_cut_style(category, line_patterns):
    """
    Retrieves line cut settings from a category object.

    :param category: A Revit Category object
    :type category: Autodesk.Revit.DB.Category
    :param line_patterns: All line patterns in the model
    :type line_patterns: [AutoDesk.Revit.LinePatternElement]

    :return: An overrides projections object instance.
    :rtype: :class:`.LineCut`
    """

    # start
    # cut line settings
    line_cut_style = LineCut()
    line_cut_style.colour = to_colour(category.LineColor)
    line_cut_style.weight = category.GetLineWeight(GraphicsStyleType.Cut)
    # basic line pattern details
    # using projection as graphics style since cut is not available
    line_pat_settings = LinePatternSettings(
        name=_get_name_from_pattern_id(
            id=category.GetLinePatternId(GraphicsStyleType.Projection),
            pattern_list=line_patterns,
        ),
        id=category.GetLinePatternId(GraphicsStyleType.Projection).IntegerValue,
    )
    # store line pattern details
    line_cut_style.line_pattern_settings = line_pat_settings

    return line_cut_style


def set_projection_style(doc, category, line_projection_style):
    """
    Sets line projection settings for a category object.

    :param doc: A Revit Document object
    :type doc: Autodesk.Revit.DB.Document
    :param category: A Revit Category object
    :type category: Autodesk.Revit.DB.Category
    :param line_patterns: All line patterns in the model
    :type line_patterns: [AutoDesk.Revit.LinePatternElement]
    :param line_projection_style: An overrides projections object instance.
    :type line_projection_style: :class:`.LineProjection`
    """

    return_value = res.Result()
    try:
        # check if doc is a Revit Document object
        if isinstance(doc, Document) == False:
            raise TypeError("doc must be a Revit Document object")

        # check if category is a Revit Category object
        if isinstance(category, Category) == False:
            raise TypeError("category must be a Revit Category object")

        # check if line_cut_style is a LineCut object
        if isinstance(line_projection_style, LineProjection) == False:
            raise TypeError("line_projection_style must be a LineProjection object")

        # start
        def action():
            action_return_value = res.Result()
            try:
                # set cut line settings
                category.SetLineWeight(
                    line_projection_style.weight,
                    GraphicsStyleType.Projection,
                )

                # set the color value
                new_colour = Color(
                    line_projection_style.colour.red,
                    line_projection_style.colour.green,
                    line_projection_style.colour.blue,
                )
                category.LineColor = new_colour

                # set line pattern by id
                category.SetLinePatternId(
                    ElementId(line_projection_style.line_pattern_settings.id),
                    GraphicsStyleType.Projection,
                )
                action_return_value.update_sep(
                    True,
                    "Successfully updated projection style of category: {}".format(
                        category.Name
                    ),
                )
            except Exception as e:
                action_return_value.update_sep(
                    False,
                    "Failed to set projection style of category {} with exception: {}".format(
                        category.Name, e
                    ),
                )
            return action_return_value

        transaction = Transaction(
            doc, "Updating projection style: {}".format(category.Name)
        )
        update_colour = in_transaction(transaction, action)
        return_value.update(update_colour)
    except Exception as e:
        return_value.update_sep(
            "failed to update projection style with exception: {}".format(e)
        )
    return return_value


def get_projection_style(category, line_patterns):
    """
    Retrieves line projection settings from a category object.

    :param category: A Revit Category object
    :type category: Autodesk.Revit.DB.Category
    :param line_patterns: All line patterns in the model
    :type line_patterns: [AutoDesk.Revit.LinePatternElement]

    :return: An overrides projections object instance.
    :rtype: :class:`.LineProjection`
    """

    # start
    # projection line settings
    line_projection_style = LineProjection()
    line_projection_style.colour = to_colour(category.LineColor)
    line_projection_style.weight = category.GetLineWeight(GraphicsStyleType.Projection)
    # basic line pattern details
    line_pat_settings = LinePatternSettings(
        name=_get_name_from_pattern_id(
            id=category.GetLinePatternId(GraphicsStyleType.Projection),
            pattern_list=line_patterns,
        ),
        id=category.GetLinePatternId(GraphicsStyleType.Projection).IntegerValue,
    )
    # store line pattern details
    line_projection_style.line_pattern_settings = line_pat_settings

    return line_projection_style


def set_category_material_by_material_id(doc, category, material_id):
    """
    Sets the material of a category object.

    :param doc: A Revit Document object
    :type doc: Autodesk.Revit.DB.Document
    :param category: A Revit Category object
    :type category: Autodesk.Revit.DB.Category
    :param material_id: The id of the material to be set
    :type material_id: int
    """

    return_value = res.Result()
    try:
        # check if doc is a Revit Document object
        if isinstance(doc, Document) == False:
            raise TypeError("doc must be a Revit Document object")

        # check if category is a Revit Category object
        if isinstance(category, Category) == False:
            raise TypeError("category must be a Revit Category object")

        # check if material_id is an integer
        if isinstance(material_id, int) == False:
            raise TypeError("material_id must be an integer")

        # get material by id
        material = get_material_by_id(doc, ElementId(material_id))

        # check if material with this id exists in model
        if material == None and material_id != -1:
            raise ValueError(
                "Material with id {} not found in model".format(material_id)
            )

        # start
        def action():
            action_return_value = res.Result()
            try:
                category.Material = material
                action_return_value.update_sep(
                    True,
                    "Successfully updated material of category: {}".format(
                        category.Name
                    ),
                )
            except Exception as e:
                action_return_value.update_sep(
                    False,
                    "Failed to set material of category {} with exception: {}".format(
                        category.Name, e
                    ),
                )
            return action_return_value

        transaction = Transaction(doc, "Updating material: {}".format(category.Name))
        update_material = in_transaction(transaction, action)
        return_value.update(update_material)
    except Exception as e:
        return_value.update_sep(
            "failed to update material with exception: {}".format(e)
        )
    return return_value


def set_category_style(doc, category_style_source, category_style_target):
    """
    Sets category graphics settings for a Revit model.

    :param doc: A Revit Document object
    :type doc: Autodesk.Revit.DB.Document
    :param category_style_source: A list of category graphics settings
    :type category_style_source: [:class:`.ObjectStyle`]
    :param category_style_target: A list of category graphics settings
    :type category_style_target: [:class:`.ObjectStyle`]

    :return: A result object with the success status and the comparison result
    :rtype: :class:`.Result`
    """

    return_value = res.Result()

    try:
        # check if doc is a Revit Document object
        if isinstance(doc, Document) == False:
            raise TypeError("doc must be a Revit Document object")

        # check if category_style_source is a list of ObjectStyle instances
        if isinstance(category_style_source, ObjectStyle) is False:
            raise TypeError("category_style_source must be an ObjectStyle instance")

        # check if category_style_target is a list of ObjectStyle instances
        if isinstance(category_style_target, ObjectStyle) is False:
            raise TypeError("category_style_target must be an ObjectStyle instance")

        # get the revit category object
        target_category = Category.GetCategory(
            doc, ElementId(category_style_target.category_id)
        )

        # set cut style
        result_cut_style_update = set_cut_style(
            doc, target_category, category_style_source.line_cut
        )
        return_value.update(result_cut_style_update)

        # set projection style
        result_projection_style_update = set_projection_style(
            doc, target_category, category_style_source.line_projection
        )
        return_value.update(result_projection_style_update)

        # material
        result_material_update = set_category_material_by_material_id(
            doc, target_category, category_style_source.material_id
        )
        return_value.update(result_material_update)

    except Exception as e:
        return_value.update_sep(
            False,
            "Failed to set category graphics settings with exception: {}".format(e),
        )

    return return_value


def get_category_styles(doc):
    """
    Retrieves all category graphics settings from a Revit model.

    :param doc: A Revit Document object
    :type doc: Autodesk.Revit.DB.Document

    :return: A result object with the success status and the category graphics settings
    :rtype: :class:`.Result`
    """

    return_value = res.Result()

    # get all pattern element since they will be required in the category settings
    # get all line pattern in model
    line_pattern_elements = get_all_line_patterns(doc=doc)

    # retrieve all categories available in model
    categories_in_model = get_categories_in_model(doc=doc)

    try:
        # set up container for all object styles in model
        object_styles_in_model = []

        # get object styles for each category
        for model_cat in categories_in_model:

            # get the revit category object
            category = Category.GetCategory(doc, model_cat.id)

            # set up storage class
            object_style = ObjectStyle(
                main_category_name=model_cat.category_name,
                sub_category_name=model_cat.sub_category_name,
                category_id=model_cat.id.IntegerValue,
            )

            # get overrides for projection and cut
            object_style.line_projection = get_projection_style(
                category, line_pattern_elements
            )
            object_style.line_cut = get_cut_style(category, line_pattern_elements)

            # get the material id
            category_material = category.Material
            if category_material != None:
                object_style.material_id = category.Material.Id.IntegerValue
            else:
                object_style.material_id = -1

            # add to overall list
            object_styles_in_model.append(object_style)

        return_value.update_sep(
            True, "Successfully retrieved category graphics settings"
        )
        return_value.result = object_styles_in_model

    except Exception as e:
        return_value.update_sep(
            False,
            "Failed to get category graphics settings with exception: {}".format(e),
        )

    return return_value


def get_all_used_line_patterns_ids_from_categories(categories):
    """
    Retrieves all line pattern ids as integer values from list of category graphics settings.

    :param categories: A list of category graphics settings
    :type categories: [:class:`.ObjectStyle`]

    :return: A list of line pattern ids
    :rtype: [int]
    """

    # check if categories is a list of ObjectStyle instances
    if (
        isinstance(categories, list) is False
        or all(isinstance(elem, ObjectStyle) for elem in categories) is False
    ):
        raise TypeError("categories must be a list of ObjectStyle instances")

    # start
    used_line_pattern_ids = []

    # get all line patterns used in categories
    for category in categories:
        used_patterns = category.get_all_used_line_patterns()
        for pattern_name, pattern in used_patterns.items():
            if pattern.id not in used_line_pattern_ids:
                used_line_pattern_ids.append(pattern.id)

    return used_line_pattern_ids


def get_not_equal_category_styles(category_styles_1, category_styles_2):
    """
    Compares two lists of category graphics settings.

    Notes:

    - The comparison is based on the main category name and sub category name.
    - if a style exists in list 1 but not in list 2 it will be reported as an equal style.
    - if a style exists in list 2 but not in list 1 it will not be reported.

    :param category_styles_1: A list of category graphics settings
    :type category_styles_1: [:class:`.ObjectStyle`]
    :param category_styles_2: A list of category graphics settings
    :type category_styles_2: [:class:`.ObjectStyle`]

    :return: A result object with the success status and the comparison result

            . result is a list of dictionaries with the main and sub category names as keys and the category graphics settings from both lists as values.
    :rtype: :class:`.Result`
    """

    return_value = res.Result()

    try:
        # check if categories is a list of ObjectStyle instances
        if (
            isinstance(category_styles_1, list) is False
            or all(isinstance(elem, ObjectStyle) for elem in category_styles_1) is False
        ):
            raise TypeError("category_styles_1 must be a list of ObjectStyle instances")
        if (
            isinstance(category_styles_2, list) is False
            or all(isinstance(elem, ObjectStyle) for elem in category_styles_2) is False
        ):
            raise TypeError("category_styles_2 must be a list of ObjectStyle instances")

        is_not_equal = []
        # outer loop
        for cat_style_1 in category_styles_1:
            matching_cat_style = [
                x
                for x in category_styles_2
                if x.main_category_name == cat_style_1.main_category_name
                and x.sub_category_name == cat_style_1.sub_category_name
            ]
            if len(matching_cat_style) == 0:
                return_value.append_message(
                    "Category style {} not found in second list".format(cat_style_1)
                )
            else:
                if cat_style_1 != matching_cat_style[0]:
                    is_not_equal.append(
                        {
                            "{}::{}".format(
                                cat_style_1.main_category_name,
                                cat_style_1.sub_category_name,
                            ): [cat_style_1, matching_cat_style[0]]
                        }
                    )

        return_value.update_sep(
            True, "Successfully compared category graphics settings"
        )
        return_value.result = is_not_equal
    except Exception as e:
        return_value.update_sep(
            False,
            "Failed to compare category graphics settings with exception: {}".format(e),
        )
    return return_value
