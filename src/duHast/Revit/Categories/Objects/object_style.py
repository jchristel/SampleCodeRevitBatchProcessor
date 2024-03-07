"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A class used to store category graphics styles.
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

import json

from duHast.Utilities.Objects import base
from duHast.Revit.Views.Objects.Data.override_projection import OverrideProjection
from duHast.Revit.Views.Objects.Data.override_cut import OverrideCut


class ObjectStyle(base.Base):
    def __init__(self, data_type="unknown", j=None, **kwargs):
        """
        Class constructor.

        """

        super(ObjectStyle, self).__init__(**kwargs)

        self.data_type = data_type
        self.material_id = -1
        self.projection = OverrideProjection()
        self.cut = OverrideCut()
        

        # check if any data was past in with constructor!
        if j != None and len(j) > 0:
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
                self.material_id = j["material_id"]
                self.projection = OverrideProjection(
                    j=j[OverrideProjection.data_type]
                )
                self.cut = OverrideCut(j=j[OverrideCut.data_type])
            except Exception as e:
                raise ValueError(
                    "Node {} failed to initialise with: {}".format(
                        "ObjectStyle.data_type", e
                    )
                )

    def compare_object_styles(self, other):
        """
        Ignores material property when comparing!

        :param other: An instance of ObjectStyle
        :type other: :class:`.ObjectStyle`
        :return: True if all graphical properties of compared class instances are equal, otherwise False.
        :rtype: Bool
        """
        return isinstance(other, ObjectStyle) and (
            self.projection,
            self.cut,
        ) == (
            other.projection,
            other.cut,
        )

    def __eq__(self, other):
        """
        Custom compare is equal override.

        :param other: Another instance of ObjectStyle base class
        :type other: :class:`.ObjectStyle`
        :return: True if all properties of compared class instances are equal, otherwise False.
        :rtype: Bool
        """

        return isinstance(other, ObjectStyle) and (
            self.projection,
            self.cut,
            self.material_id,
        ) == (
            other.projection,
            other.cut,
            other.material_id,
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
                    self.projection,
                    self.cut,
                    self.material_id,
                )
            )
        except Exception as e:
            raise ValueError(
                "Exception {} occurred in {} object style projection: {}, object style cut: {}, object style material id: {}".format(
                    e,
                    self.data_type,
                    self.projection,
                    self.cut,
                    self.material_id
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
            self.projection.line_projection.line_pattern_settings.name
            not in used_line_patterns
        ):
            used_line_patterns[
                self.projection.line_projection.line_pattern_settings.name
            ] = self.projection.line_projection.line_pattern_settings

        # from cut
        if (
            self.cut.line_cut.line_pattern_settings.name
            not in used_line_patterns
        ):
            used_line_patterns[
                self.cut.line_cut.line_pattern_settings.name
            ] = self.cut.line_cut.line_pattern_settings

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
            self.projection.pattern_background.fill_pattern_setting.name
            not in used_fill_patterns
        ):
            used_fill_patterns[
                self.projection.pattern_background.fill_pattern_setting.name
            ] = self.projection.pattern_background.fill_pattern_setting

        if (
            self.projection.pattern_foreground.fill_pattern_setting
            not in used_fill_patterns
        ):
            used_fill_patterns[
                self.projection.pattern_foreground.fill_pattern_setting.name
            ] = self.projection.pattern_foreground.fill_pattern_setting

        # from cut
        if (
            self.cut.pattern_background.fill_pattern_setting.name
            not in used_fill_patterns
        ):
            used_fill_patterns[
                self.cut.pattern_background.fill_pattern_setting.name
            ] = self.cut.pattern_background.fill_pattern_setting

        if (
            self.cut.pattern_foreground.fill_pattern_setting.name
            not in used_fill_patterns
        ):
            used_fill_patterns[
                self.cut.pattern_foreground.fill_pattern_setting.name
            ] = self.cut.pattern_foreground.fill_pattern_setting

        return used_fill_patterns
