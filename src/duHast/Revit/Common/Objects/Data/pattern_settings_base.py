"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A base class used to store pattern data.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


Stores pattern base data for line and fill pattern.

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


class PatternSettingBase(base.Base):
    NO_PATTERN = "no pattern assigned"
    SOLID_PATTERN = "SOLID"

    def __init__(self, name=NO_PATTERN, id=-1, data_type="unknown", j=None, **kwargs):
        """
        Class constructor.

        """

        super(PatternSettingBase, self).__init__(**kwargs)

        # set defaults
        self.data_type = data_type
        if name == None:
            self.name = PatternSettingBase.NO_PATTERN
        else:
            self.name = name
        self.id = id

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
                self.id = j["id"]
                self.name = j["name"]
            except Exception as e:
                raise ValueError(
                    "Node {} failed to initialise with: {}".format(
                        "PatternSettingBase", e
                    )
                )

    def __eq__(self, other):
        """
        Custom compare is equal override (name comparison only!)

        :param other: Another instance of pattern class
        :type other: :class:`.PatternBase`
        :return: True if name value of other colour class instance equal the name values of this instance, otherwise False.
        :rtype: Bool
        """

        return isinstance(other, PatternSettingBase) and (self.name) == (other.name)

    # python 2.7 needs custom implementation of not equal
    def __ne__(self, other):
        return not self.__eq__(other=other)

    def __hash__(self):
        """
        Custom hash override

        Required due to custom __eq__ override present in this class
        """
        try:
            return hash((self.name))
        except Exception as e:
            raise ValueError(
                "Exception {} occurred in {} with values: name:{}".format(
                    e, self.data_type, self.name
                )
            )
