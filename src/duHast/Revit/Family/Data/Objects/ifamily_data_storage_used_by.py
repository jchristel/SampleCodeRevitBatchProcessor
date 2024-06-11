"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Interface for family data storage used by class.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


Notes:

used to store used by other nested families data in root family data storage class.


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


from duHast.Utilities.Objects import base


class IFamilyDataStorageUsedBy(base.Base):
    def __init__(self, data_type, family_name, element_id, j, **kwargs):

        # forwards all unused arguments
        # ini super class to allow multi inheritance in children!
        super(IFamilyDataStorageUsedBy, self).__init__(**kwargs)

        if isinstance(data_type, str):
            self.data_type = data_type
        else:
            raise ValueError("data_type must be a string")

        if isinstance(family_name, str):
            self.root_name_path = family_name
        else:
            raise ValueError("family_name must be a string")

        if isinstance(element_id, int):
            self.element_id = element_id
        else:
            raise ValueError(
                "element_id [{}] must be an int but is {}".format(
                    element_id, type(element_id)
                )
            )

        # ini using JSON data
        if isinstance(j, dict):
            try:
                self.root_name_path = j.get("root_name_path", self.root_name_path)
                self.element_id = j.get("element_id", self.element_id)
                self.data_type = j.get("data_type", self.data_type)
            except Exception as e:
                print("Failed to initialise object with JSON data: {}".format(e))
                raise ValueError(
                    "Node {} failed to initialise with: {}".format(self.data_type, e)
                )

    def __eq__(self, other):
        """
        Custom compare is equal override.

        :param other: Another instance of IFamilyDataStorageUsedBy base class
        :type other: :class:`.IFamilyDataStorageUsedBy`
        :return: True if all properties of compared class instances are equal, otherwise False.
        :rtype: Bool
        """

        return isinstance(other, IFamilyDataStorageUsedBy) and (
            self.data_type,
            self.root_name_path,
            self.element_id,
        ) == (
            other.data_type,
            other.root_name_path,
            other.element_id,
        )

    # python 2.7 needs custom implementation of not equal
    def __ne__(self, other):
        return not self.__eq__(other=other)
