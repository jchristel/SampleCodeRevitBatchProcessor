"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A base class used to store view (template) graphic settings .
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


Stores:

- model overrides
- filter overrides


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

from duHast.Revit.Views.Objects.Data.override_by_category import OverrideByCategory
from duHast.Revit.Views.Objects.Data.override_by_filter import OverrideByFilter


class ViewGraphicsSettings(base.Base):
    def __init__(self, view_name="", view_id=-1, j=None, **kwargs):
        """
        Class constructor.

        """

        super(ViewGraphicsSettings, self).__init__(**kwargs)

        # set default values
        self.view_name = view_name
        self.view_id = view_id
        self.override_by_category = []
        self.override_by_filter = []

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
                for override in j[OverrideByCategory.data_type]:
                    self.override_by_category.append(OverrideByCategory(j=override))
                for override in j[OverrideByFilter.data_type]:
                    self.override_by_filter.append(OverrideByFilter(j=override))
                self.view_name = j["view_name"]
                self.view_id = j["view_id"]
            except Exception as e:
                raise ValueError(
                    "Node ViewGraphicsSettings failed to initialise with: {}".format(e)
                )

    def get_differing_category_overrides(self, other_view_graphic_settings):
        """
        Returns all category overrides of this category of categories  which exist in both set of settings but have different overrides applied.

        :param other_view_graphic_settings: _description_
        :type other_view_graphic_settings: _type_
        :raises TypeError: _description_
        """

        if not isinstance(other_view_graphic_settings, ViewGraphicsSettings):
            raise TypeError(
                "other_view_graphic_settings must be an instance of ViewGraphicsSettings"
            )

        difference = []

        # check category overrides
        for source_override_category in self.override_by_category:
            for (
                other_override_category
            ) in other_view_graphic_settings.override_by_category:
                if (
                    source_override_category.main_category_name
                    == other_override_category.main_category_name
                    and source_override_category.sub_category_name
                    == other_override_category.sub_category_name
                ):
                    if source_override_category != other_override_category:
                        difference.append(source_override_category)
                    break

        return difference

    def get_differing_filter_overrides(self, other_view_graphic_settings):
        """
        Returns all filter overrides which exist exist in both set of settings but have different overrides applied.

        :param other_view_graphic_settings: _description_
        :type other_view_graphic_settings: _type_
        :raises TypeError: _description_
        """

        if not isinstance(other_view_graphic_settings, ViewGraphicsSettings):
            raise TypeError(
                "other_view_graphic_settings must be an instance of ViewGraphicsSettings"
            )

        difference = []

        # check filter overrides
        for source_override_category in self.override_by_filter:
            for (
                other_override_category
            ) in other_view_graphic_settings.override_by_filter:
                if (
                    source_override_category.filter_name
                    == other_override_category.filter_name
                ):
                    if source_override_category != other_override_category:
                        difference.append(source_override_category)
                    break
        return difference

    def get_all_used_line_patterns(self):
        """
        Get all line patterns used in overrides

        :return: Dictionary of line pattern names to line pattern objects
        :rtype: {str: :class:`.LinePatternSettings`}
        """

        all_line_patterns = {}

        # check category overrides
        for override_category in self.override_by_category:
            line_pattern_override = override_category.get_all_used_line_patterns()
            all_line_patterns.update(line_pattern_override)

        # check filter overrides
        for override_filter in self.override_by_filter:
            line_pattern_override = override_filter.get_all_used_line_patterns()
            all_line_patterns.update(line_pattern_override)
        return all_line_patterns

    def get_all_used_fill_patterns(self):
        """
        Get all fill pattern used in overrides.

        :return: Dictionary of line pattern names to line pattern objects
        :rtype: {str: :class:`.FillPatternSettings`}

        :return: _description_
        :rtype: _type_
        """
        all_fill_patterns = {}

        # check category overrides
        for override_category in self.override_by_category:
            fill_pattern_override = override_category.get_all_used_fill_patterns()
            all_fill_patterns.update(fill_pattern_override)

        # check filter overrides
        for override_filter in self.override_by_filter:
            fill_pattern_override = override_filter.get_all_used_fill_patterns()
            all_fill_patterns.update(fill_pattern_override)
        return all_fill_patterns
