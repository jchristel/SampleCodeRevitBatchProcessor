"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A base class used to store colour values.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


Stores colour values as rgb.

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


class ColourBase(base.Base):
    data_type = "colour"

    def __init__(self, j=None, **kwargs):
        """
        Class constructor.

        """

        super(ColourBase, self).__init__(**kwargs)

        # set defaults
        self.red = -1
        self.green = -1
        self.blue = -1

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
                self.red = j["red"]
                self.green = j["green"]
                self.blue = j["blue"]
            except Exception as e:
                raise ValueError(
                    "Node {} failed to initialise with: {}".format(
                        ColourBase.data_type, e
                    )
                )

    def __eq__(self, other):
        """
        Custom compare is equal override

        :param other: Another instance of colour class
        :type other: :class:`.ColourBase`
        :return: True if RGB values of other colour class instance equal the RGB values of this instance, otherwise False.
        :rtype: Bool
        """

        return isinstance(other, ColourBase) and (self.red, self.green, self.blue) == (
            other.red,
            other.green,
            other.blue,
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
            return hash((self.red, self.green, self.blue))
        except Exception as e:
            raise ValueError(
                "Exception {} occurred in {} with values: red:{}, green:{}, blue:{}".format(
                    e, self.data_type, self.red, self.green, self.blue
                )
            )
