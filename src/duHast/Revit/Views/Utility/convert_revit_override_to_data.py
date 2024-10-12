"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Category override to data storage class helper functions.
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

from Autodesk.Revit.DB import (
    Element,
    ElementId,
    OverrideGraphicSettings,
    LinePatternElement,
)

from duHast.Revit.Views.Objects.view_graphics_settings import ViewGraphicsSettings
from duHast.Revit.LinePattern.line_patterns import get_all_line_patterns
from duHast.Revit.LinePattern.fill_patterns import get_all_fill_pattern
from duHast.Revit.Categories.categories_model import get_categories_in_model
from duHast.Revit.Views.Objects.Data.override_by_category import OverrideByCategory
from duHast.Revit.Views.Objects.Data.override_by_filter import OverrideByFilter
from duHast.Revit.Views.Objects.Data.override_projection import OverrideProjection
from duHast.Revit.Views.Objects.Data.override_cut import OverrideCut
from duHast.Revit.Common.Objects.Data.pattern_background import PatternBackground
from duHast.Revit.Common.Objects.Data.pattern_foreground import PatternForeground
from duHast.Revit.Common.Objects.Data.line_projection import LineProjection
from duHast.Revit.Common.Objects.Data.line_cut import LineCut
from duHast.Revit.LinePattern.Data.Objects.line_pattern_settings import (
    LinePatternSettings,
)
from duHast.Revit.LinePattern.Data.Objects.fill_pattern_settings import (
    FillPatternSettings,
)
from duHast.Revit.Common.Objects.Data.pattern_settings_base import PatternSettingBase
from duHast.Revit.Common.Utility.revit_to_data_conversion import (
    to_colour,
    VIEW_DETAIL_LEVEL_NAME_MAPPING,
)


# ----------------------  utility ----------------------


def _get_name_from_pattern_id(id, pattern_list):
    """
    Returns the matching name of a pattern from the list past in by the id

    :param id: The pattern id to match
    :type id: Autodesk.Revit.DB.ElementId
    :param pattern_list: A list of pattern elements
    :type pattern_list: [PatternElement] (Can be AutoDesk.Revit.LinePatternElement or Autodesk.Revit.DB.FillPatternElement)
    :return: The pattern name if a match was found, "No pattern override assigned." when no pattern was assigned otherwise None (should nt really happen!)
    :rtype: str or None
    """
    if id == LinePatternElement.GetSolidPatternId():
        return PatternSettingBase.SOLID_PATTERN
    elif id == ElementId.InvalidElementId:
        return PatternSettingBase.NO_PATTERN
    for pat in pattern_list:
        if id == pat.Id:
            return Element.Name.GetValue(pat)
    return None


# ----------------------  overrides ----------------------


def get_projection_overrides(view_override_graphic, line_patterns, fill_patterns):
    """
    Retrieves projection override settings from an OverridesGraphicSettings object

    :param view_override_graphic: An overrides graphic setting
    :type view_override_graphic: Autodesk.Revit.DB.OverridesGraphicSettings
    :param line_patterns: All line patterns in the model
    :type line_patterns: [AutoDesk.Revit.LinePatternElement]
    :param fill_patterns: All fill patterns in the model
    :type fill_patterns: [Autodesk.Revit.DB.FillPatternElement]

    :return: An overrides projections object instance.
    :rtype: :class:`.OverrideProjection`
    """

    # set up data storage class instance
    projection_override = OverrideProjection()

    # start
    # projection line pattern
    line_pat = LineProjection()
    line_pat.colour = to_colour(view_override_graphic.ProjectionLineColor)
    line_pat.weight = view_override_graphic.ProjectionLineWeight
    # basic line pattern details
    line_pat_settings = LinePatternSettings(
        name=_get_name_from_pattern_id(
            id=view_override_graphic.ProjectionLinePatternId, pattern_list=line_patterns
        ),
        id=view_override_graphic.ProjectionLinePatternId.IntegerValue,
    )
    # store line pattern details
    line_pat.line_pattern_settings = line_pat_settings
    # store projection line pattern details
    projection_override.line_projection = line_pat

    # projection pattern foreground
    fore_pat = PatternForeground()
    fore_pat.colour = to_colour(view_override_graphic.SurfaceForegroundPatternColor)
    fore_pat.is_visible = view_override_graphic.IsSurfaceForegroundPatternVisible
    # basic foreground pattern details
    fore_pat_settings = FillPatternSettings(
        name=_get_name_from_pattern_id(
            id=view_override_graphic.SurfaceForegroundPatternId,
            pattern_list=fill_patterns,
        ),
        id=view_override_graphic.SurfaceForegroundPatternId.IntegerValue,
    )
    # store foreground pattern settings details
    fore_pat.fill_pattern_setting = fore_pat_settings
    # store foreground pattern in override
    projection_override.pattern_foreground = fore_pat

    # projection pattern background
    back_pat = PatternBackground()
    back_pat.colour = to_colour(view_override_graphic.SurfaceBackgroundPatternColor)
    back_pat.is_visible = view_override_graphic.IsSurfaceBackgroundPatternVisible
    # basic background pattern details
    back_pat_settings = FillPatternSettings(
        name=_get_name_from_pattern_id(
            id=view_override_graphic.SurfaceBackgroundPatternId,
            pattern_list=fill_patterns,
        ),
        id=view_override_graphic.SurfaceBackgroundPatternId.IntegerValue,
    )
    # store foreground pattern settings details
    back_pat.fill_pattern_setting = back_pat_settings
    # store background pattern in override
    projection_override.pattern_background = back_pat

    return projection_override


def get_cut_overrides(view_override_graphic, line_patterns, fill_patterns):
    """
    Retrieves cut override settings from an OverridesGraphicSettings object

    :param view_override_graphic: An overrides graphic setting
    :type view_override_graphic: Autodesk.Revit.DB.OverridesGraphicSettings
    :param line_patterns: All line patterns in the model
    :type line_patterns: [AutoDesk.Revit.LinePatternElement]
    :param fill_patterns: All fill patterns in the model
    :type fill_patterns: [Autodesk.Revit.DB.FillPatternElement]

    :return: An overrides projections object instance.
    :rtype: :class:`.OverrideCut`
    """

    # set up data storage class instance
    cut_override = OverrideCut()

    # start
    # cut line pattern
    line_pat = LineCut()
    line_pat.colour = to_colour(view_override_graphic.CutLineColor)
    line_pat.weight = view_override_graphic.CutLineWeight
    # basic line pattern details
    line_pat_settings = LinePatternSettings(
        name=_get_name_from_pattern_id(
            id=view_override_graphic.CutLinePatternId, pattern_list=line_patterns
        ),
        id=view_override_graphic.CutLinePatternId.IntegerValue,
    )
    # store line pattern details
    line_pat.line_pattern_settings = line_pat_settings
    # store projection line pattern details
    cut_override.line_cut = line_pat

    # cut pattern foreground
    fore_pat = PatternForeground()
    fore_pat.colour = to_colour(view_override_graphic.CutForegroundPatternColor)
    fore_pat.is_visible = view_override_graphic.IsCutForegroundPatternVisible
    # basic foreground pattern details
    fore_pat_settings = FillPatternSettings(
        name=_get_name_from_pattern_id(
            id=view_override_graphic.CutForegroundPatternId, pattern_list=fill_patterns
        ),
        id=view_override_graphic.CutForegroundPatternId.IntegerValue,
    )
    # store foreground pattern settings details
    fore_pat.fill_pattern_setting = fore_pat_settings
    # store foreground pattern in override
    cut_override.pattern_foreground = fore_pat

    # cut pattern background
    back_pat = PatternBackground()
    back_pat.colour = to_colour(view_override_graphic.CutBackgroundPatternColor)
    back_pat.is_visible = view_override_graphic.IsCutBackgroundPatternVisible
    # basic background pattern details
    back_pat_settings = FillPatternSettings(
        name=_get_name_from_pattern_id(
            id=view_override_graphic.CutBackgroundPatternId, pattern_list=fill_patterns
        ),
        id=view_override_graphic.CutBackgroundPatternId.IntegerValue,
    )
    # store foreground pattern settings details
    back_pat.fill_pattern_setting = back_pat_settings
    # store background pattern in override
    cut_override.pattern_background = back_pat

    return cut_override


# ----------------------  by category overrides ----------------------


def get_view_category_overrides(
    view, categories_in_model, line_patterns, fill_patterns
):
    """
    Returns the category overrides for all categories past in for a given view.

    :param view: The view from which to retrieve the category overrides.
    :type view: Autodesk.Revit.DB.View
    :param categories_in_model: All categories in the model.
    :type categories_in_model: _type_
    :param line_patterns: All line patterns in the model
    :type line_patterns: [AutoDesk.Revit.LinePatternElement]
    :param fill_patterns: All fill patterns in the model
    :type fill_patterns: [Autodesk.Revit.DB.FillPatternElement]

    :return: A list of all category overrides for a view.
    :rtype: [:class:`.OverrideByCategory`]
    """

    overrides_data = []
    for model_cat in categories_in_model:
        # set up storage class
        override = OverrideByCategory(
            main_category_name=model_cat.category_name,
            sub_category_name=model_cat.sub_category_name,
            category_id=model_cat.id.IntegerValue,
        )

        # get the overrides by category
        view_override = view.GetCategoryOverrides(model_cat.id)

        # get general overrides settings
        override.halftone = view_override.Halftone
        override.transparency = view_override.Transparency

        # get cut overrides for category
        override.override_cut = get_cut_overrides(
            view_override_graphic=view_override,
            line_patterns=line_patterns,
            fill_patterns=fill_patterns,
        )

        # get projection for category
        override.override_projection = get_projection_overrides(
            view_override_graphic=view_override,
            line_patterns=line_patterns,
            fill_patterns=fill_patterns,
        )

        # check if category is hidden ( need to inverse since I'm storing ( is visible) the exact opposite (is hidden) of what is returned)
        override.is_visible = not (view.GetCategoryHidden(model_cat.id))

        # get the detail level as an integer
        override.detail_level = VIEW_DETAIL_LEVEL_NAME_MAPPING[
            view_override.DetailLevel
        ]

        # check if any override has been applied by comparing the retrieved override
        # with a default one
        default_override = OverrideByCategory()
        if default_override.compare_overrides(override):
            override.are_overrides_present = False
        else:
            override.are_overrides_present = True

        # save overrides in list to be returned
        overrides_data.append(override)

    return overrides_data


# ----------------------  by filter overrides ----------------------


def get_view_filter_overrides(doc, view, line_patterns, fill_patterns):
    """
    Returns the filter overrides for all filter applied to a given view.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param view: The view from which to retrieve the category overrides.
    :type view: Autodesk.Revit.DB.View
    :param line_patterns: All line patterns in the model
    :type line_patterns: [AutoDesk.Revit.LinePatternElement]
    :param fill_patterns: All fill patterns in the model
    :type fill_patterns: [Autodesk.Revit.DB.FillPatternElement]

    :return: A list of all filter overrides for a view.
    :rtype: [:class:`.OverrideByFilter`]
    """

    overrides_data = []

    # get all filters applied to a view
    filter_ids_applied = view.GetFilters()

    for filter_id in filter_ids_applied:
        # get the actual filter element
        filter = doc.GetElement(filter_id)
        # set up storage class
        override = OverrideByFilter(
            filter_name=Element.Name.GetValue(filter),
            filter_id=filter_id.IntegerValue,
        )

        # get the overrides by filter
        view_override = view.GetFilterOverrides(filter_id)
        # get general overrides settings
        override.halftone = view_override.Halftone
        override.transparency = view_override.Transparency

        # get cut overrides for filter
        override.override_cut = get_cut_overrides(
            view_override_graphic=view_override,
            line_patterns=line_patterns,
            fill_patterns=fill_patterns,
        )

        # get projection for filter
        override.override_projection = get_projection_overrides(
            view_override_graphic=view_override,
            line_patterns=line_patterns,
            fill_patterns=fill_patterns,
        )

        # check if filter switches things off
        override.is_visible = view.GetFilterVisibility(filter_id)

        # check if filter is enabled
        override.is_enabled = view.GetIsFilterEnabled(filter_id)

        # check if any override has been applied by comparing the retrieved override
        # with a default one
        default_override = OverrideByFilter()
        if default_override.compare_overrides(override):
            override.are_overrides_present = False
        else:
            override.are_overrides_present = True

        # save overrides in list to be returned
        overrides_data.append(override)

    return overrides_data


def get_view_settings(doc, view):
    """
    retrieves the filter and category graphic overrides from a view

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param view: _description_
    :type view: _type_
    :return: A ViewGraphicsSettings instance with retrieved setting.
    :rtype: :class:`.ViewGraphicsSettings`
    """

    # set up class to store view graphic settings
    view_data = ViewGraphicsSettings(
        view_name=Element.Name.GetValue(view),
        view_id=view.Id.IntegerValue,
    )

    # get all pattern element since they will be required in the override settings
    # get all line pattern and fill patterns in model
    line_pattern_elements = get_all_line_patterns(doc=doc)

    # get all fill pattern elements in model
    fill_pattern_elements = get_all_fill_pattern(doc=doc)

    # retrieve all categories available in model
    categories_in_model = get_categories_in_model(doc=doc)

    # get category graphic overrides
    category_overrides = get_view_category_overrides(
        view=view,
        categories_in_model=categories_in_model,
        line_patterns=line_pattern_elements,
        fill_patterns=fill_pattern_elements,
    )
    view_data.override_by_category = category_overrides

    # get filter graphic overrides
    filter_overrides = get_view_filter_overrides(
        doc=doc,
        view=view,
        line_patterns=line_pattern_elements,
        fill_patterns=fill_pattern_elements,
    )
    view_data.override_by_filter = filter_overrides

    return view_data


def get_views_graphic_settings_data(doc, views):
    """
    Gets view data graphic settings from the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param views: Views of which to report graphical overrides on. (View must support graphical overrides, otherwise an exception will be thrown!)
    :type views: [Autodesk.Revit.DB.View]
    :return: list of ViewGraphicsSettings instances
    :rtype: [:class:`.ViewGraphicsSettings`]
    """

    views_settings = []

    # loop over past in views and retrieve settings
    for view in views:
        view_setting = get_view_settings(
            doc=doc,
            view=view,
        )
        views_settings.append(view_setting)

    return views_settings
