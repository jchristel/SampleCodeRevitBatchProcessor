"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Data storage to Category override object helper functions.
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

import clr

# used to convert integer to byte value
import System

from Autodesk.Revit.DB import (
    Color,
    ElementId,
    LinePatternElement,
    OverrideGraphicSettings,
)

from duHast.Revit.Common.Utility.revit_to_data_conversion import (
    VIEW_DETAIL_LEVEL_NAME_MAPPING_REVERSE,
    VIEW_DETAIL_LEVEL_NAME_MAPPING,
)

from duHast.Revit.LinePattern.line_patterns import build_patterns_dictionary_by_name
from duHast.Revit.LinePattern.fill_patterns import pattern_ids_by_name
from duHast.Revit.Common.Objects.Data.pattern_settings_base import PatternSettingBase


def get_colour(data_colour):
    """
    Creates a Revit Color object instance from a ColourBase object

    :param data_colour: A ColourBase instance.
    :type data_colour: :class: ColourBase
    :return: None if ColourBase values are -1, or larger then 255, otherwise a Color instance.
    :rtype: Autodesk.Revit.DB.Color
    """

    if data_colour.red == -1 and data_colour.green == -1 and data_colour.blue == -1:
        # reset to no colour value override
        return Color.InvalidColorValue
    else:
        try:
            return Color(
                System.Convert.ToByte(data_colour.red),
                System.Convert.ToByte(data_colour.green),
                System.Convert.ToByte(data_colour.blue),
            )
        except:
            return None


def get_fill_pattern_id(doc, data_pattern):
    """
    Returns the first fill pattern id in model matching name provided, or None if none was found.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param data_pattern: A pattern settings base object instance
    :type data_pattern: :class:`.PatternSettingBase`

    :return: The pattern id if a match eas found or Invalid Element Id  (-1)
    :rtype: Autodesk.Revit.DB.ElementId
    """

    all_patterns = pattern_ids_by_name(doc)
    if data_pattern.name in all_patterns:
        return all_patterns[data_pattern.name][0]
    else:
        return ElementId.InvalidElementId


def get_line_pattern_id(doc, data_pattern):
    """
    Returns the first line pattern id in model matching name provided, or None if none was found.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param data_pattern: A pattern settings base object instance
    :type data_pattern: :class:`.PatternSettingBase`

    :return: The pattern id if a match eas found or Invalid Element Id  (-1)
    :rtype: Autodesk.Revit.DB.ElementId
    """

    all_patterns = build_patterns_dictionary_by_name(doc)
    if data_pattern.name in all_patterns:
        return all_patterns[data_pattern.name][0]
    elif data_pattern.name == PatternSettingBase.SOLID_PATTERN:
        return LinePatternElement.GetSolidPatternId()
    else:
        return ElementId.InvalidElementId


def convert_to_revit_graphic_override(doc, data_override, is_filter_override=False):
    """
    Creates a Revit OverrideGraphicSettings instance from settings stored in an OverrideByCategory object.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param data_override: An OverrideByCategory object
    :type data_override: :class:`.OverrideByCategory`
    :param is_filter_override: Flag indicating an override for a filter (True), defaults to False
    :type is_filter_override: bool, optional
    :return: An OverrideGraphicSettings instance
    :rtype: Autodesk.Revit.DB.OverrideGraphicSettings
    """

    # set up a new revit api override settings instance
    revit_override_setting = OverrideGraphicSettings()

    # set values based on data override if one is present
    if data_override.are_overrides_present:
        # Sets the override color of the background pattern of cut faces.
        revit_override_setting.SetCutBackgroundPatternColor(
            get_colour(data_override.override_cut.pattern_background.colour)
        )
        # Sets the ElementId of the cut face background pattern override. The fill pattern must be a drafting pattern.
        # A value of InvalidElementId means no override is set.
        revit_override_setting.SetCutBackgroundPatternId(
            get_fill_pattern_id(
                doc, data_override.override_cut.pattern_background.fill_pattern_setting
            )
        )
        # Sets the visibility of the cut face background fill pattern.
        revit_override_setting.SetCutBackgroundPatternVisible(
            (data_override.override_cut.pattern_background.is_visible)
        )
        # Sets the override color of the foreground pattern of cut faces.
        revit_override_setting.SetCutForegroundPatternColor(
            get_colour(data_override.override_cut.pattern_foreground.colour)
        )
        # Sets the ElementId of the cut face foreground pattern override. The fill pattern must be a drafting pattern.
        # A value of InvalidElementId means no override is set.
        revit_override_setting.SetCutForegroundPatternId(
            get_fill_pattern_id(
                doc, data_override.override_cut.pattern_foreground.fill_pattern_setting
            )
        )
        # Sets the visibility of the cut face foreground fill pattern.
        revit_override_setting.SetCutForegroundPatternVisible(
            (data_override.override_cut.pattern_foreground.is_visible)
        )
        # Sets the cut surface line color.
        revit_override_setting.SetCutLineColor(
            get_colour(data_override.override_cut.line_cut.colour)
        )
        # Sets the ElementId of the cut surface line pattern.
        revit_override_setting.SetCutLinePatternId(
            get_line_pattern_id(
                doc, data_override.override_cut.line_cut.line_pattern_settings
            )
        )
        # Sets the cut surface line weight.
        revit_override_setting.SetCutLineWeight(
            data_override.override_cut.line_cut.weight
        )

        # detail override only exists on category overrides
        if is_filter_override == False:
            # Sets the detail level if required
            if data_override.detail_level != -1:
                revit_override_setting.SetDetailLevel(
                    VIEW_DETAIL_LEVEL_NAME_MAPPING_REVERSE[data_override.detail_level]
                )
        # Sets the halftone value.
        revit_override_setting.SetHalftone(data_override.halftone)

        # Sets the projection surface line color.
        revit_override_setting.SetProjectionLineColor(
            get_colour(data_override.override_projection.line_projection.colour)
        )
        # Sets the ElementId of the projection surface line pattern.
        revit_override_setting.SetProjectionLinePatternId(
            get_line_pattern_id(
                doc,
                data_override.override_projection.line_projection.line_pattern_settings,
            )
        )
        # Sets the projection surface line weight.
        revit_override_setting.SetProjectionLineWeight(
            data_override.override_projection.line_projection.weight
        )
        # Sets the override color of the surface background pattern.
        revit_override_setting.SetSurfaceBackgroundPatternColor(
            get_colour(data_override.override_projection.pattern_background.colour)
        )
        # Sets the ElementId of the surface background pattern override. The fill pattern must be a drafting pattern.
        # A value of InvalidElementId means no override is set.
        revit_override_setting.SetSurfaceBackgroundPatternId(
            get_fill_pattern_id(
                doc,
                data_override.override_projection.pattern_background.fill_pattern_setting,
            )
        )
        # Sets the visibility of the surface background fill pattern.
        revit_override_setting.SetSurfaceBackgroundPatternVisible(
            data_override.override_projection.pattern_background.is_visible
        )
        # Sets the override color of the surface foreground pattern.
        revit_override_setting.SetSurfaceForegroundPatternColor(
            get_colour(data_override.override_projection.pattern_foreground.colour)
        )
        # Sets the ElementId of the surface foreground pattern override. The fill pattern must be a drafting pattern.
        # A value of InvalidElementId means no override is set.
        revit_override_setting.SetSurfaceForegroundPatternId(
            get_fill_pattern_id(
                doc,
                data_override.override_projection.pattern_foreground.fill_pattern_setting,
            )
        )
        # Sets the visibility of the surface foreground fill pattern.
        revit_override_setting.SetSurfaceForegroundPatternVisible(
            data_override.override_projection.pattern_foreground.is_visible
        )
        # Sets the projection surface transparency
        revit_override_setting.SetSurfaceTransparency(data_override.transparency)

    return revit_override_setting
