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
from duHast.Revit.Common.Objects.colour_base import ColourBase


class PatternGraphicBase(base.Base):
    def __init__(self, data_type="unknown", j={}, **kwargs):
        """
        Class constructor.

        """

        super(PatternGraphicBase, self).__init__(**kwargs)

        self.data_type = data_type

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

            # load overrides

            if ColourBase.data_type in j:
                self.colour = ColourBase(j[ColourBase.data_type])
            else:
                self.colour = ColourBase()

            if "is_visible" in j:
                self.is_visible = j["is_visible"]
            else:
                self.is_visible = True

            if "pattern_id" in j:
                self.pattern_id = j["pattern_id"]
            else:
                self.pattern_id = -1
        else:
            # set default values
            self.colour = ColourBase()
            self.pattern_id = -1
            self.is_visible = True

    def __eq__(self, other):
        """
        Custom compare is equal override.
        The comparison ignores the pattern_id value!

        :param other: Another instance of line graphic base class
        :type other: :class:`.PatternGraphicBase`
        :return: True if is_visible and colour values of other colour class instance equal the is_visible and colour values of this instance, otherwise False.
        :rtype: Bool
        """

        return (self.is_visible, self.colour) == (other.is_visible, other.colour)