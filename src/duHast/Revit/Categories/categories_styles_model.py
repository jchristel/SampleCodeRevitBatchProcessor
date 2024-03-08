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

from Autodesk.Revit.DB import Category, GraphicsStyleType


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
            object_style.line_projection = get_projection_style(category, line_pattern_elements)
            object_style.line_cut = get_cut_style(category, line_pattern_elements)

            # add to overall list
            object_styles_in_model.append(object_style)
    
        return_value.update_sep(True, "Successfully retrieved category graphics settings")
        return_value.result = object_styles_in_model

    except Exception as e:
        return_value.update_sep(False, "Failed to get category graphics settings with exception: {}".format(e))
    
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
    if isinstance(categories, list) is False or all(isinstance(elem, ObjectStyle) for elem in categories) is False:
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