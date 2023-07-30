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
    def __init__(self, data_type="unknown", j={}, **kwargs):
        """
        Class constructor.

        """

        super(OverrideByBase, self).__init__(**kwargs)

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
            if "halftone" in j:
                self.halftone = j["halftone"]
            else:
                self.halftone = False

            if "transparency" in j:
                self.transparency = j["transparency"]
            else:
                self.transparency = 0

            if "is_visible" in j:
                self.is_visible = j["is_visible"]
            else:
                self.is_visible = True
            
            if OverrideProjection.data_type in j:
                self.override_projection = OverrideProjection(
                    j[OverrideProjection.data_type]
                )
            else:
                self.override_projection = OverrideProjection()

            if OverrideCut.data_type in j:
                self.override_cut = OverrideCut(j[OverrideCut.data_type])
            else:
                self.override_cut = OverrideCut()
        else:
            self.halftone = False
            self.transparency = 0
            self.override_projection = OverrideProjection()
            self.override_cut = OverrideCut()
            self.is_visible = True

    def __eq__(self, other):
        """
        Custom compare is equal override.

        :param other: Another instance of OverrideByBase base class
        :type other: :class:`.OverrideByBase`
        :return: True if all properties of compared class instances are equal, otherwise False.
        :rtype: Bool
        """

        return (
            self.halftone,
            self.transparency,
            self.is_visible,
            self.override_projection,
            self.override_cut,
        ) == (
            other.halftone,
            other.transparency,
            other.is_visible,
            other.override_projection,
            other.override_cut,
        )
