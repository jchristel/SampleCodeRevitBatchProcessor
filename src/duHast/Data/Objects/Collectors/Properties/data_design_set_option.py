"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Data storage class for Revit design option properties.
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
from duHast.Data.Objects.Collectors import data_base
from duHast.Data.Objects.Collectors.Properties.data_property_names import (
    DataPropertyNames,
)


class DataDesignSetOption(data_base.DataBase):
    data_type = "design_set_and_option"

    def __init__(self, j=None):
        """
        Class constructor.

        :param j: A json formatted dictionary of this class, defaults to {}
        :type j: dict, optional
        """

        # store data type  in base class
        super(DataDesignSetOption, self).__init__(DataDesignSetOption.data_type)

        # set default values
        self.set_name = "-"
        self.option_name = "-"
        self.is_primary = True

        json_var = None
        # check if any data was past in with constructor!
        if j is not None:
            # check type of data that came in:
            if isinstance(j, str):
                # a string
                json_var = json.loads(j)
            elif isinstance(j, dict):
                # no action required
                json_var = j.copy()
            else:
                raise TypeError(
                    "Argument j supplied must be of type string or type dictionary. Got {} instead.".format(
                        type(j)
                    )
                )

            # attempt to populate from json
            try:
                self.set_name = json_var.get(DataPropertyNames.SET_NAME, self.set_name)
                if not isinstance(self.set_name, str):
                    raise TypeError(
                        "Expected 'set_name' to be a string, got {}".format(
                            type(self.set_name)
                        )
                    )

                self.option_name = json_var.get(
                    DataPropertyNames.OPTION_NAME, self.option_name
                )
                if not isinstance(self.option_name, str):
                    raise TypeError(
                        "Expected 'option_name' to be a string, got {}".format(
                            type(self.option_name)
                        )
                    )

                self.is_primary = json_var.get(
                    DataPropertyNames.IS_PRIMARY, self.is_primary
                )
                if not isinstance(self.is_primary, bool):
                    raise TypeError(
                        "Expected 'is_primary' to be a boolean, got {}".format(
                            type(self.is_primary)
                        )
                    )

            except Exception as e:
                raise type(e)(
                    "Node {} failed to initialise with: {}".format(self.data_type, e)
                )

    def __eq__(self, other):
        if not isinstance(other, DataDesignSetOption):
            return NotImplemented
        return (
            self.set_name == other.set_name
            and self.option_name == other.option_name
            and self.is_primary == other.is_primary
        )

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.set_name, self.option_name, self.is_primary))
