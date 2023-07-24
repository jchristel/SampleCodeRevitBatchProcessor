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

from duHast.Revit.Views.Objects.override_by_category import OverrideByCategory
from duHast.Revit.Views.Objects.override_by_filter import OverrideByFilter


class ViewGraphicsSettings(base.Base):
    def __init__(self, view_name="", view_id=-1, j={}, **kwargs):
        """
        Class constructor.

        """

        super(ViewGraphicsSettings, self).__init__(**kwargs)

        self.view_name = view_name
        self.view_id = view_id

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
            else:
                self.override_by_category = []

            if OverrideByFilter.data_type in j:
                for override in j[OverrideByFilter.data_type]:
                    self.override_by_filter.append(OverrideByFilter(override))
            else:
                self.override_by_filter = []

        else:
            self.override_by_category = []
            self.override_by_filter = []

    def add_overrides_by_category(self, override):
        """
        Add overrides by category settings

        :param override: _description_
        :type override: _type_
        """

        self.override_by_category.append(override)

    def add_overrides_by_filter(self, override):
        """
        Add overrides by filter settings

        :param override: _description_
        :type override: _type_
        """

        self.override_by_filter.append(override)
