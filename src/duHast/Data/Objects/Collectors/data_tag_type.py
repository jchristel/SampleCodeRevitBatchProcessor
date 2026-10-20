"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Data storage class for the type of a tag: its category, family name and type name.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2024, Jan Christel
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


class DataTagType(data_base.DataBase):

    data_type = "tag_type"

    def __init__(self, j=None):
        """
        Class constructor for the type of a tag.

        Family name and type name are what a tag rule is keyed by (a tag type's element id
        means nothing in another model), so they are stored as read and never derived.

        :param j: A json formatted dictionary of this class, defaults to None
        :type j: dict, optional
        """

        super(DataTagType, self).__init__(data_type=DataTagType.data_type)

        # empty string is unread, never guessed
        self.category = ""
        self.family_name = ""
        self.type_name = ""

        if j is not None:
            if isinstance(j, str):
                json_var = json.loads(j)
            elif isinstance(j, dict):
                json_var = j.copy()
            else:
                raise TypeError(
                    "Argument j supplied must be of type string or type dictionary. Got {} instead.".format(
                        type(j)
                    )
                )
            try:
                self.category = json_var.get(DataPropertyNames.CATEGORY, self.category)
                self.family_name = json_var.get(DataPropertyNames.FAMILY_NAME, self.family_name)
                self.type_name = json_var.get(DataPropertyNames.TYPE_NAME, self.type_name)
            except Exception as e:
                raise type(e)(
                    "Node {} failed to initialise with: {}".format(self.data_type, e)
                )

    def __eq__(self, other):
        if not isinstance(other, DataTagType):
            return NotImplemented
        return (
            self.category == other.category
            and self.family_name == other.family_name
            and self.type_name == other.type_name
        )

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.category, self.family_name, self.type_name))
