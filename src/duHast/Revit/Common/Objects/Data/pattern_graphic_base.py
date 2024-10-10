"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A base class used to store pattern graphic settings.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


Stores pattern graphic settings:

- colour
- pattern_id
- is_visible

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
from duHast.Revit.Common.Objects.Data.colour_base import ColourBase
from duHast.Revit.LinePattern.Data.Objects.fill_pattern_settings import (
    FillPatternSettings,
)


class PatternGraphicBase(base.Base):
    def __init__(self, data_type="unknown", j=None, **kwargs):
        """
        Class constructor.

        """

        super(PatternGraphicBase, self).__init__(**kwargs)

        self.data_type = data_type

        # set default values
        self.colour = ColourBase()
        self.is_visible = True
        self.fill_pattern_setting = FillPatternSettings()

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
                self.colour = ColourBase(j=j[ColourBase.data_type])
                self.is_visible = j["is_visible"]
                self.fill_pattern_setting = FillPatternSettings(
                    j=j["fill_pattern_setting"]
                )
            except Exception as e:
                raise ValueError(
                    "Node {} failed to initialise with: {}".format(
                        "PatternGraphicBase", e
                    )
                )

    def __eq__(self, other):
        """
        Custom compare is equal override.
        The comparison ignores the pattern_id value!

        :param other: Another instance of line graphic base class
        :type other: :class:`.PatternGraphicBase`
        :return: True if is_visible, fill pattern settings and colour values of other colour class instance equal the is_visible, fill pattern settings, colour values of this instance, otherwise False.
        :rtype: Bool
        """

        return isinstance(other, PatternGraphicBase) and (
            self.is_visible,
            self.fill_pattern_setting,
            self.colour,
        ) == (
            other.is_visible,
            other.fill_pattern_setting,
            other.colour,
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
                    self.is_visible,
                    self.fill_pattern_setting,
                    self.colour,
                )
            )

        except Exception as e:
            raise ValueError(
                "Exception {} occurred in {} with values: is_visible:{}, fill_pattern_setting: {}, colour: {}".format(
                    e,
                    self.data_type,
                    self.is_visible,
                    self.fill_pattern_setting,
                    self.colour,
                )
            )
