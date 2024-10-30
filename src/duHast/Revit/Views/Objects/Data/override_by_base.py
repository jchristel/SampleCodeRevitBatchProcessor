"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A base class used to store category overrides.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


Stores common overrides between categories and filters

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

import json

from duHast.Utilities.Objects import base
from duHast.Revit.Views.Objects.Data.override_projection import OverrideProjection
from duHast.Revit.Views.Objects.Data.override_cut import OverrideCut


class OverrideByBase(base.Base):
    def __init__(self, data_type="unknown", j=None, **kwargs):
        """
        Class constructor.

        """

        super(OverrideByBase, self).__init__(**kwargs)

        self.data_type = data_type
        self.halftone = False
        self.transparency = 0
        self.is_visible = True
        self.override_projection = OverrideProjection()
        self.override_cut = OverrideCut()
        self.are_overrides_present = False

        # check if any data was past in with constructor!
        if j is not None:
            # check type of data that came in:
            if type(j) == str:
                # a string
                j = json.loads(j)
            elif type(j) == dict:
                # no action required
                pass
            else:
                raise ValueError(
                    "Argument supplied must be of type string or type dictionary"
                )

            # load values and throw exception if something is missing!
            try:
                self.halftone = j["halftone"]
                self.transparency = j["transparency"]
                self.is_visible = j["is_visible"]
                self.override_projection = OverrideProjection(
                    j=j[OverrideProjection.data_type]
                )
                self.override_cut = OverrideCut(j=j[OverrideCut.data_type])
                self.are_overrides_present = j["are_overrides_present"]
            except Exception as e:
                raise ValueError(
                    "Node {} failed to initialise with: {}".format(
                        "OverrideByBase.data_type", e
                    )
                )

    def compare_overrides(self, other):
        """
        Ignores visibility property when comparing! (ignores is_visible and are_overrides_present)

        :param other: An instance of OverrideByBase
        :type other: :class:`.OverrideByBase`
        :return: True if all graphical properties of compared class instances are equal, otherwise False.
        :rtype: Bool
        """
        return isinstance(other, OverrideByBase) and (
            self.halftone,
            self.transparency,
            self.override_projection,
            self.override_cut,
        ) == (
            other.halftone,
            other.transparency,
            other.override_projection,
            other.override_cut,
        )

    def __eq__(self, other):
        """
        Custom compare is equal override.

        :param other: Another instance of OverrideByBase base class
        :type other: :class:`.OverrideByBase`
        :return: True if all properties of compared class instances are equal, otherwise False.
        :rtype: Bool
        """

        return isinstance(other, OverrideByBase) and (
            self.halftone,
            self.transparency,
            self.is_visible,
            self.override_projection,
            self.override_cut,
            self.are_overrides_present,
        ) == (
            other.halftone,
            other.transparency,
            other.is_visible,
            other.override_projection,
            other.override_cut,
            other.are_overrides_present,
        )

    # python 2.7 needs custom implementation of not equal
    def __ne__(self, other):
        return not self.__eq__(other=other)

    def __hash__(self):
        """
        Custom hash override

        Required due to custom __eq__ override present in this class
        """
        try:
            return hash(
                (
                    self.halftone,
                    self.transparency,
                    self.is_visible,
                    self.override_projection,
                    self.override_cut,
                    self.are_overrides_present,
                )
            )
        except Exception as e:
            raise ValueError(
                "Exception {} occurred in {} with values: halftone:{}, transparency: {}, is visible: {}, override projection: {}, override cut: {}".format(
                    e,
                    self.data_type,
                    self.halftone,
                    self.transparency,
                    self.is_visible,
                    self.override_projection,
                    self.override_cut,
                )
            )

    def get_all_used_line_patterns(self):
        """
        Extract dictionary of line pattern names to line pattern objects

        :return: Dictionary of line pattern names to line pattern objects
        :rtype: {str: :class:`.LinePatternSettings`}
        """

        used_line_patterns = {}

        # from projection
        if (
            self.override_projection.line_projection.line_pattern_settings.name
            not in used_line_patterns
        ):
            used_line_patterns[
                self.override_projection.line_projection.line_pattern_settings.name
            ] = self.override_projection.line_projection.line_pattern_settings

        # from cut
        if (
            self.override_cut.line_cut.line_pattern_settings.name
            not in used_line_patterns
        ):
            used_line_patterns[
                self.override_cut.line_cut.line_pattern_settings.name
            ] = self.override_cut.line_cut.line_pattern_settings

        return used_line_patterns

    def get_all_used_fill_patterns(self):
        """
        Extract dictionary of fill pattern names to fill pattern objects

        :return: Dictionary of fill pattern names to fill pattern objects
        :rtype: {str: :class:`.FillPatternSettings`}
        """
        used_fill_patterns = {}
        # from projection
        if (
            self.override_projection.pattern_background.fill_pattern_setting.name
            not in used_fill_patterns
        ):
            used_fill_patterns[
                self.override_projection.pattern_background.fill_pattern_setting.name
            ] = self.override_projection.pattern_background.fill_pattern_setting

        if (
            self.override_projection.pattern_foreground.fill_pattern_setting
            not in used_fill_patterns
        ):
            used_fill_patterns[
                self.override_projection.pattern_foreground.fill_pattern_setting.name
            ] = self.override_projection.pattern_foreground.fill_pattern_setting

        # from cut
        if (
            self.override_cut.pattern_background.fill_pattern_setting.name
            not in used_fill_patterns
        ):
            used_fill_patterns[
                self.override_cut.pattern_background.fill_pattern_setting.name
            ] = self.override_cut.pattern_background.fill_pattern_setting

        if (
            self.override_cut.pattern_foreground.fill_pattern_setting.name
            not in used_fill_patterns
        ):
            used_fill_patterns[
                self.override_cut.pattern_foreground.fill_pattern_setting.name
            ] = self.override_cut.pattern_foreground.fill_pattern_setting

        return used_fill_patterns
