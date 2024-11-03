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
from duHast.Revit.Common.Objects.Data import (
    pattern_foreground,
    pattern_background,
    line_cut,
)


class OverrideCut(base.Base):
    data_type = "override_cut"

    def __init__(self, j=None, **kwargs):
        """
        Class constructor.

        """

        super(OverrideCut, self).__init__(**kwargs)

        # set defaults
        self.pattern_background = pattern_background.PatternBackground()
        self.pattern_foreground = pattern_foreground.PatternForeground()
        self.line_cut = line_cut.LineCut()

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

            # load overrides and throw exception if something is missing!
            try:
                self.pattern_background = pattern_background.PatternBackground(
                    j=j[pattern_background.PatternBackground.data_type]
                )
                self.pattern_foreground = pattern_foreground.PatternForeground(
                    j=j[pattern_foreground.PatternForeground.data_type]
                )
                self.line_cut = line_cut.LineCut(j=j[line_cut.LineCut.data_type])
            except Exception as e:
                raise ValueError(
                    "Node {} failed to initialise with: {}".format(
                        OverrideCut.data_type, e
                    )
                )

    def __eq__(self, other):
        """
        Custom compare is equal override.

        :param other: Another instance of OverrideCut class
        :type other: :class:`.OverrideCut`
        :return: True if all properties of compared class instances are equal, otherwise False.
        :rtype: Bool
        """

        return isinstance(other, OverrideCut) and (
            self.pattern_background,
            self.pattern_foreground,
            self.line_cut,
        ) == (
            other.pattern_background,
            other.pattern_foreground,
            other.line_cut,
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
                (self.pattern_background, self.pattern_foreground, self.line_cut)
            )
        except Exception as e:
            raise ValueError(
                "Exception {} occurred in {} with values: pattern background:{}, pattern fore: {}, line cut: {}".format(
                    e,
                    self.data_type,
                    self.pattern_background,
                    self.pattern_foreground,
                    self.line_cut,
                )
            )
