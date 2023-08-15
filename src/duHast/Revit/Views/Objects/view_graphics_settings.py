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
    def __init__(self, view_name="", view_id=-1, j={}, **kwargs):
        """
        Class constructor.

        """

        super(ViewGraphicsSettings, self).__init__(**kwargs)

        # set default values
        self.view_name = view_name.encode("utf-8") # utf 8 encoding just in case
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

            # load settings
            if OverrideByCategory.data_type in j:
                for override in j[OverrideByCategory.data_type]:
                    self.override_by_category.append(OverrideByCategory(override))

            if OverrideByFilter.data_type in j:
                for override in j[OverrideByFilter.data_type]:
                    self.override_by_filter.append(OverrideByFilter(override))

            if "view_name" in j:
                self.view_name = j["view_name"]

            if "view_id" in j:
                self.view_id = j["view_id"]

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
