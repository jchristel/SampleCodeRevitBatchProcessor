"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Class for family line pattern data storage class.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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

from duHast.Revit.Family.Data.Objects import ifamily_data_storage as IFamDataStorage
from duHast.Revit.LinePattern.Data.Objects.line_pattern_storage_used_by import (
    FamilyLinePatternDataStorageUsedBy,
)


class FamilyLinePatternDataStorage(IFamDataStorage.IFamilyDataStorage):

    # data type for this class ( used in reports as first entry per row )
    data_type = "LinePattern"

    # number of properties in this class ( used in report reader function )
    number_of_properties = 9

    def __init__(
        self,
        root_name_path,
        root_category_path,
        family_name,
        family_file_path,
        use_counter,
        used_by,
        pattern_name,
        pattern_id,
        **kwargs
    ):

        # store args in base class
        super(FamilyLinePatternDataStorage, self).__init__(
            data_type=FamilyLinePatternDataStorage.data_type,
            root_name_path=root_name_path,
            root_category_path=root_category_path,
            family_name=family_name,
            family_file_path=family_file_path,
        )

        # check whether used by is a json list as a string
        if used_by is not None and used_by != "None":
            # check type of data that came in:
            # check if string was passed in
            if isinstance(used_by, str):
                # a string
                used_by_json = json.loads(used_by)
                # if used by was converted into a json object successfully it should now be a list of dictionaries!
                converted_used_by = []
                if isinstance(used_by_json, list):
                    for i in range(len(used_by_json)):
                        try:
                            # convert to  FamilyLinePatternDataStorageUsedBy object
                            dummy = FamilyLinePatternDataStorageUsedBy(
                                j=used_by_json[i]
                            )
                            converted_used_by.append(dummy)
                        except Exception as e:
                            raise ValueError(
                                "Failed to convert string {} to  FamilyLinePatternDataStorageUsedBy object: {}".format(
                                    used_by_json[i], e
                                )
                            )
                    # override string with converted data
                    used_by = converted_used_by
            # check if a list of family category data storage used by objects was passed in
            elif isinstance(used_by, list):
                # check if every list item is of type  FamilyLinePatternDataStorageUsedBy
                for i in range(len(used_by)):
                    if not isinstance(used_by[i], FamilyLinePatternDataStorageUsedBy):
                        raise ValueError(
                            "used_by list must contain only FamilyLinePatternDataStorageUsedBy objects"
                        )
            elif isinstance(used_by, FamilyLinePatternDataStorageUsedBy):
                # convert to a list
                used_by = [used_by]
            else:
                raise ValueError(
                    "used_by argument supplied must be of type string or type  FamilyLinePatternDataStorageUsedBy or a list of FamilyLinePatternDataStorageUsedBy"
                )
        else:
            # default is an empty list
            used_by = []

        # store other args in this class
        self.use_counter = use_counter
        self.used_by = used_by
        self.pattern_name = pattern_name
        self.pattern_id = pattern_id

    def __eq__(self, other):
        """
        Custom compare is equal override.

        :param other: Another instance of FamilyLinePatternDataStorage base class
        :type other: :class:`.FamilyLinePatternDataStorage`
        :return: True if all properties of compared class instances are equal, otherwise False.
        :rtype: Bool
        """

        return isinstance(other, FamilyLinePatternDataStorage) and (
            self.data_type,
            self.root_name_path,
            self.root_category_path,
            self.family_name,
            self.family_file_path,
            self.use_counter,
            self.used_by,
            self.pattern_name,
            self.pattern_id,
        ) == (
            other.data_type,
            other.root_name_path,
            other.root_category_path,
            other.family_name,
            other.family_file_path,
            other.use_counter,
            other.used_by,
            other.pattern_name,
            other.pattern_id,
        )

    # python 2.7 needs custom implementation of not equal
    def __ne__(self, other):
        return not self.__eq__(other=other)
