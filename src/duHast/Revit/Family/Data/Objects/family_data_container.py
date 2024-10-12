"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Family data container class.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- contains all instances of the following storage classes from reports read from files:

    - FamilyBaseDataStorage
    - CategoryDataStorage
    - WarningsDataStorage
    - LinePatternDataStorage
    - SharedParameterDataStorage

- These storage instances belong to a specific family only identified by unique combination of family name nesting path and family category nesting path
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

from duHast.Utilities.Objects import base

import System
import json
from duHast.Revit.Family.Data.Objects.family_base_data_storage import (
    FamilyBaseDataStorage,
)
from duHast.Revit.Categories.Data.Objects.category_data_storage import (
    FamilyCategoryDataStorage,
)
from duHast.Revit.LinePattern.Data.Objects.line_pattern_data_storage import (
    FamilyLinePatternDataStorage,
)
from duHast.Revit.SharedParameters.Data.Objects.shared_parameter_data_storage import (
    FamilySharedParameterDataStorage,
)
from duHast.Revit.Warnings.Data.Objects.warnings_data_storage import (
    FamilyWarningsDataStorage,
)
from duHast.Revit.Family.Data.Objects.ifamily_data_storage import IFamilyDataStorage
from duHast.Revit.Family.Data.Objects.family_base_data_processor_defaults import (
    NESTING_SEPARATOR,
)


class FamilyDataContainer(base.Base):
    def __init__(
        self,
        family_base_data_storage=None,
        category_data_storage=None,
        line_pattern_data_storage=None,
        shared_parameter_data_storage=None,
        warnings_data_storage=None,
        **kwargs
    ):
        """
        Family data container class.

        Contains all instances of the following storage classes from reports read from files:

                - FamilyBaseDataStorage
                - CategoryDataStorage
                - WarningsDataStorage
                - LinePatternDataStorage
                - SharedParameterDataStorage

        Note: There is the possibility that only one of the storage classes is populated, this is due to the fact that the data is read from separate files and not all data is always present in each file.

        :param family_base_data_storage: a list of FamilyBaseDataStorage instances
        :type family_base_data_storage: [:class:`.FamilyBaseDataStorage`]
        :param category_data_storage: a list of FamilyCategoryDataStorage instances
        :type category_data_storage: [:class:`.FamilyCategoryDataStorage`]
        :param line_pattern_data_storage: a list of FamilyLinePatternDataStorage instances
        :type line_pattern_data_storage: [:class:`.FamilyLinePatternDataStorage`]
        :param shared_parameter_data_storage: a list of FamilySharedParameterDataStorage instances
        :type shared_parameter_data_storage: [:class:`.FamilySharedParameterDataStorage`]
        :param warnings_data_storage: a list of FamilyWarningsDataStorage instances
        :type warnings_data_storage: [:class:`.FamilyWarningsDataStorage`]
        :param kwargs: _description_
        :type kwargs: _type_
        :raises ValueError: type mismatch if any of the past in lists are not of the correct type
        """

        # forwards all unused arguments
        # ini super class to allow multi inheritance in children!
        super(FamilyDataContainer, self).__init__(**kwargs)

        # set some base properties to their default values
        self.family_name = None
        self.family_nesting_path = None
        self.family_category = None
        self.family_category_nesting_path = None
        self.is_root_family = False
        self.family_file_path = None

        # populate class from past in data
        # start with family base data storage
        # if a valid family base data storage instance is passed in this will also set the following properties:
        # family_name, family_nesting_path, family_category, family_category_nesting_path, is_root_family, family_file_path

        # family base data default is an empty list
        self.family_base_data_storage = []
        if family_base_data_storage is None:
            # no change required
            pass
        else:
            if isinstance(family_base_data_storage, list):
                # should only ever be one entry!
                if len(family_base_data_storage) > 1:
                    raise ValueError(
                        "family_base_data_storage can only ever have one entry"
                    )
                # add to class property
                for storage_instance in family_base_data_storage:
                    self.add_family_base_data_storage(storage_instance)
            elif isinstance(family_base_data_storage, FamilyBaseDataStorage):
                # add to class property
                self.add_family_base_data_storage(family_base_data_storage)
            else:
                raise ValueError(
                    "family_base_data_storage must be a list or FamilyBaseDataStorage"
                )

        # category data storage default is an empty list
        self.category_data_storage = []
        if category_data_storage is None:
            # no change required
            pass
        else:
            if isinstance(category_data_storage, list):
                # add to class property
                for storage_instance in category_data_storage:
                    self.add_category_data_storage(storage_instance)
            else:
                self.add_category_data_storage(category_data_storage)

        # line pattern data storage default is an empty list
        self.line_pattern_data_storage = []
        if line_pattern_data_storage is None:
            # no change required
            pass
        elif isinstance(line_pattern_data_storage, list):
            # add to class property
            for storage_instance in line_pattern_data_storage:
                self.add_line_pattern_data_storage(storage_instance)
        else:
            self.add_line_pattern_data_storage(line_pattern_data_storage)

        # shared parameter data storage default is an empty list
        self.shared_parameter_data_storage = []
        if shared_parameter_data_storage is None:
            # no change required
            pass
        elif isinstance(shared_parameter_data_storage, list):
            # add to class property
            for storage_instance in shared_parameter_data_storage:
                self.add_shared_parameter_data_storage(storage_instance)
        else:
            self.add_shared_parameter_data_storage(shared_parameter_data_storage)

        # warnings data storage default is an empty list
        self.warnings_data_storage = []
        if warnings_data_storage is None:
            # no change required
            pass
        elif isinstance(warnings_data_storage, list):
            # add to class property
            for storage_instance in warnings_data_storage:
                self.add_warnings_data_storage(storage_instance)
        else:
            self.add_warnings_data_storage(warnings_data_storage)

    def _update_base_properties_from_storage(self, storage_instance):
        """
        Will update the base properties of the class from a family base data storage instance.

        :param storage_instance: a family data storage instance
        :type storage_instance: :class:`.IFamilyDataStorage`
        """

        # set other class properties based on storage
        self.family_name = storage_instance.family_name
        self.family_file_path = storage_instance.family_file_path
        self.family_nesting_path = storage_instance.root_name_path
        self.family_category_nesting_path = storage_instance.root_category_path

        # set the category property based on the last entry in root category path
        category_chunks = storage_instance.root_category_path.split(NESTING_SEPARATOR)
        self.family_category = category_chunks[-1]

        # check if this is a root family
        if NESTING_SEPARATOR in storage_instance.root_name_path:
            self.is_root_family = False
        else:
            self.is_root_family = True

    def add_family_base_data_storage(self, other):
        """
        Will add a family base data storage instance and infer some other class properties from it.

        Note: if storage data properties root_name_path and root_category_path are different to the current values
        all other storage properties will be wiped to avoid mismatches!

        :param other: A family base data storage instance added to this class
        :type other: :class:`.FamilyBaseDataStorage`
        :raises TypeError: If other is not an instance of FamilyBaseDataStorage a type error will be raised.
        """
        # check is correct object type
        if isinstance(other, FamilyBaseDataStorage) == False:
            raise TypeError("other must be a list of FamilyBaseDataStorage")

        # only add if not already in list
        if other not in self.family_base_data_storage:
            # there is always only going to be one entry in list, pop the existing one if there is one
            if len(self.family_base_data_storage) > 0:
                self.family_base_data_storage.pop()

            # add new one to class property
            self.family_base_data_storage.append(other)

            # check if nesting path and category nesting path are different to the current values but not None!
            # if so wipe the other storage properties to avoid mismatches!
            if (
                self.family_nesting_path != other.root_name_path
                and self.family_nesting_path != None
                or self.family_category_nesting_path != other.root_category_path
                and self.family_category_nesting_path != None
            ):
                self.category_data_storage = []
                self.line_pattern_data_storage = []
                self.shared_parameter_data_storage = []
                self.warnings_data_storage = []

            # set other class properties based on storage
            self._update_base_properties_from_storage(other)
        else:
            raise ValueError(
                "Base storage is not unique: family nesting path: {} category nesting path: {}".format(
                    other.root_name_path, other.root_category_path
                )
            )

    def add_category_data_storage(self, other):
        """
        Will add a category data storage instance.

        Note: an exception will be raised if family_nesting_path and family_category_nesting_path do not match the current values!

        :param other: a data storage instance
        :type other: :class:`.FamilyCategoryDataStorage`
        :raises TypeError: If other is not an instance of FamilyCategoryDataStorage a type error will be raised.
        """
        # check is correct object type
        if isinstance(other, FamilyCategoryDataStorage) == False:
            raise TypeError("other must be a list of FamilyCategoryDataStorage")

        # only add if not already in list
        if other not in self.category_data_storage:
            # check if nesting path and category nesting path are different to the current values but not None!
            # if so  throw error!
            if (
                self.family_nesting_path != other.root_name_path
                and self.family_nesting_path != None
                or self.family_category_nesting_path != other.root_category_path
                and self.family_category_nesting_path != None
            ):
                raise ValueError(
                    "other root_name_path and root_category_path must match current values"
                )
            elif (
                self.family_nesting_path == None
                and self.family_category_nesting_path == None
            ):
                # looks like this might be the only storage class added or
                # family base data storage is absent and this is the first storage class added
                self._update_base_properties_from_storage(other)

            # add to class property only if unique (unique is if category name, sub category name and sub category id are unique)
            if len(self.category_data_storage) == 0:
                # add to class property
                self.category_data_storage.append(other)
            else:
                found_match = False
                for entry in self.category_data_storage:
                    if (
                        entry.category_name == other.category_name
                        and entry.sub_category_name == other.sub_category_name
                        and entry.sub_category_id == other.sub_category_id
                    ):
                        found_match = True
                        break
                if not found_match:
                    # add to class property
                    self.category_data_storage.append(other)
                else:
                    raise ValueError(
                        "Category storage is not unique: category: {} sub category: {} id: {}".format(
                            other.category_name,
                            other.sub_category_name,
                            other.sub_category_id,
                        )
                    )
        else:
            raise ValueError(
                "Category storage is not unique: category: {} sub category: {} id: {}".format(
                    other.category_name, other.sub_category_name, other.sub_category_id
                )
            )

    def add_line_pattern_data_storage(self, other):
        """
        Will add a line pattern data storage instance.

        Note: an exception will be raised if family_nesting_path and family_category_nesting_path do not match the current values!

        :param other: a data storage instance
        :type other: :class:`.FamilyLinePatternDataStorage`
        :raises TypeError: If other is not an instance of FamilyLinePatternDataStorage a type error will be raised.
        """
        # check is correct object type
        if isinstance(other, FamilyLinePatternDataStorage) == False:
            raise TypeError("other must be a list of FamilyLinePatternDataStorage")

        # only add if not already in list
        if other not in self.line_pattern_data_storage:
            # check if nesting path and category nesting path are different to the current values but not None!
            # if so throw error!
            if (
                self.family_nesting_path != other.root_name_path
                and self.family_nesting_path != None
                or self.family_category_nesting_path != other.root_category_path
                and self.family_category_nesting_path != None
            ):
                raise ValueError(
                    "other root_name_path and root_category_path must match current values"
                )
            elif (
                self.family_nesting_path == None
                and self.family_category_nesting_path == None
            ):
                # looks like this might be the only storage class added or
                # family base data storage is absent and this is the first storage class added
                self._update_base_properties_from_storage(other)

            # add to class property only if unique (unique is if pattern name and pattern id are unique)
            if len(self.line_pattern_data_storage) == 0:
                # add to class property
                self.line_pattern_data_storage.append(other)
            else:
                found_match = False
                for entry in self.line_pattern_data_storage:
                    if (
                        entry.pattern_name == other.pattern_name
                        and entry.pattern_id == other.pattern_id
                    ):
                        found_match = True
                        break
                if not found_match:
                    # add to class property
                    self.line_pattern_data_storage.append(other)
                else:
                    raise ValueError(
                        "Line pattern storage is not unique: name: {} id: {}".format(
                            other.pattern_name, other.pattern_id
                        )
                    )
        else:
            raise ValueError(
                "Line pattern storage is not unique: name: {} id: {}".format(
                    other.pattern_name, other.pattern_id
                )
            )

    def add_shared_parameter_data_storage(self, other):
        """
        Will add a shared parameter data storage instance.

        Note: an exception will be raised if family_nesting_path and family_category_nesting_path do not match the current values!

        :param other: a data storage instance
        :type other: :class:`.FamilySharedParameterDataStorage`
        :raises TypeError: If other is not an instance of FamilySharedParameterDataStorage a type error will be raised.
        """
        # check is correct object type
        if isinstance(other, FamilySharedParameterDataStorage) == False:
            raise TypeError("other must be a list of FamilySharedParameterDataStorage")

        # only add if not already in list
        if other not in self.shared_parameter_data_storage:
            # check if nesting path and category nesting path are different to the current values but not None!
            # if so wipe throw error!
            if (
                self.family_nesting_path != other.root_name_path
                and self.family_nesting_path != None
                or self.family_category_nesting_path != other.root_category_path
                and self.family_category_nesting_path != None
            ):
                raise ValueError(
                    "other root_name_path and root_category_path must match current values"
                )
            elif (
                self.family_nesting_path == None
                and self.family_category_nesting_path == None
            ):
                # looks like this might be the only storage class added or
                # family base data storage is absent and this is the first storage class added
                self._update_base_properties_from_storage(other)

            # add to class property only if unique (unique is if parameter name and parameter id are unique)
            if len(self.shared_parameter_data_storage) == 0:
                # add to class property
                self.shared_parameter_data_storage.append(other)
            else:
                found_match = False
                for entry in self.shared_parameter_data_storage:
                    if (
                        entry.parameter_name == other.parameter_name
                        and entry.parameter_id == other.parameter_id
                    ):
                        found_match = True
                        break
                if not found_match:
                    # add to class property
                    self.shared_parameter_data_storage.append(other)
                else:
                    raise ValueError(
                        "Shared parameter storage is not unique: name: {} id: {}".format(
                            other.parameter_name, other.parameter_id
                        )
                    )
        else:
            raise ValueError(
                "Shared parameter storage is not unique: name: {} id: {}".format(
                    other.parameter_name, other.parameter_id
                )
            )

    def add_warnings_data_storage(self, other):
        """
        Will add a warnings data storage instance.

        Note: an exception will be raised if family_nesting_path and family_category_nesting_path do not match the current values!

        :param other: a data storage instance
        :type other: :class:`.FamilyWarningsDataStorage`
        :raises TypeError: If other is not an instance of FamilyWarningsDataStorage a type error will be raised.
        """
        # check is correct object type
        if isinstance(other, FamilyWarningsDataStorage) == False:
            raise TypeError("other must be type of FamilyWarningsDataStorage")

        # only add if not already in list
        if other not in self.warnings_data_storage:
            # check if nesting path and category nesting path are different to the current values but not None!
            # if so wipe throw error!
            if (
                self.family_nesting_path != other.root_name_path
                and self.family_nesting_path != None
                or self.family_category_nesting_path != other.root_category_path
                and self.family_category_nesting_path != None
            ):
                raise ValueError(
                    "other root_name_path and root_category_path must match current values"
                )
            elif (
                self.family_nesting_path == None
                and self.family_category_nesting_path == None
            ):
                # looks like this might be the only storage class added or
                # family base data storage is absent and this is the first storage class added
                self._update_base_properties_from_storage(other)

            # add to class property only if unique (unique is if warning text and warning guid are unique)
            if len(self.warnings_data_storage) == 0:
                # add to class property
                self.warnings_data_storage.append(other)
            else:
                found_match = False
                for entry in self.warnings_data_storage:
                    if (
                        entry.warning_text == other.warning_text
                        and entry.warning_guid == other.warning_guid
                    ):
                        found_match = True
                        break
                if not found_match:
                    # add to class property
                    self.warnings_data_storage.append(other)
                else:
                    raise ValueError(
                        "Warnings storage is not unique: text: {} guid: {}".format(
                            other.warning_text, other.warning_guid
                        )
                    )
        else:
            raise ValueError(
                "Warnings storage is not unique: text: {} guid: {}".format(
                    other.warning_text, other.warning_guid
                )
            )

    def add_data_storage(self, other):
        """
        Adds a new data storage instance to this container.

        :param other: The new data storage instance.
        :type other: :class:`.IFamilyDataStorage`
        :raises TypeError: If other is not an instance of IFamilyDataStorage a type error will be raised.
        """

        # check is correct object type
        if isinstance(other, IFamilyDataStorage) == False:
            raise TypeError(
                "other must be a type of IFamilyDataStorage but is: {}".format(
                    type(other)
                )
            )

        if other.data_type == FamilyBaseDataStorage.data_type:
            self.add_family_base_data_storage(other=other)
        elif other.data_type == FamilyCategoryDataStorage.data_type:
            self.add_category_data_storage(other=other)
        elif other.data_type == FamilyLinePatternDataStorage.data_type:
            self.add_line_pattern_data_storage(other=other)
        elif other.data_type == FamilySharedParameterDataStorage.data_type:
            self.add_shared_parameter_data_storage(other=other)
        elif other.data_type == FamilyWarningsDataStorage.data_type:
            self.add_warnings_data_storage(other=other)
        else:
            raise TypeError(
                "Data storage type : {} is not supported.".format(other.data_type)
            )

    def _get_storage_of_type(storage_property):
        """
        Loops of the storage instances saved in the storage property of this class and returns their string values

        :param storage_property: a property of this class containing IFamilyDataStorage instances
        :type storage_property: :class:`.Result` IFamilyDataStorage
        :return: A nested list of strings representing each storage instance
        :rtype: [[str]]
        """
        data = []
        for storage in storage_property:
            if isinstance(storage, IFamilyDataStorage) == False:
                raise TypeError(
                    "Storage should of type IFamilyDataStorage but is [{}]".format(
                        type(storage)
                    )
                )
            data.append(storage.get_data_values_as_list_of_strings())
        return data

    def get_family_base_data_storage_as_string(self):
        """
        Returns all family base data instance storage as string

        :return: A dictionary where key is the storage data type, and value is a nested list of strings representing each storage instance
        :rtype: {str:[[str]]}
        """
        data = self._get_storage_of_type(storage_property=self.family_base_data_storage)
        return {FamilyBaseDataStorage.data_type: data}

    def get_family_category_data_storage_as_string(self):
        """
        Returns all family category data instance storage as string

        :return: A dictionary where key is the storage data type, and value is a nested list of strings representing each storage instance
        :rtype: {str:[[str]]}
        """
        data = self._get_storage_of_type(storage_property=self.category_data_storage)
        return {FamilyCategoryDataStorage.data_type: data}

    def get_line_pattern_data_storage_as_string(self):
        """
        Returns all family line pattern data instance storage as string

        :return: A dictionary where key is the storage data type, and value is a nested list of strings representing each storage instance
        :rtype: {str:[[str]]}
        """
        data = self._get_storage_of_type(
            storage_property=self.line_pattern_data_storage
        )
        return {FamilyLinePatternDataStorage.data_type: data}

    def get_shared_parameter_data_storage_as_string(self):
        """
        Returns all family shared parameter data instance storage as string

        :return: A dictionary where key is the storage data type, and value is a nested list of strings representing each storage instance
        :rtype: {str:[[str]]}
        """
        data = self._get_storage_of_type(
            storage_property=self.shared_parameter_data_storage
        )
        return {FamilySharedParameterDataStorage.data_type: data}

    def get_warnings_data_storage_as_string(self):
        """
        Returns all family warnings data instance storage as string

        :return: A dictionary where key is the storage data type, and value is a nested list of strings representing each storage instance
        :rtype: {str:[[str]]}
        """
        data = self._get_storage_of_type(storage_property=self.warnings_data_storage)
        return {FamilyWarningsDataStorage.data_type: data}

    def get_data_string_list(self):
        """
        returns a dictionary where key is the storage data type and value is a list of string representing the data storage
        """

        return_value = {}
        storage_as_strings = []

        # get all storage data as string ( represented in dictionary where key is the data type and values list of lists containing the storage data)
        storage_as_strings.append(self.get_family_base_data_storage_as_string())
        storage_as_strings.append(self.get_family_category_data_storage_as_string())
        storage_as_strings.append(self.get_line_pattern_data_storage_as_string())
        storage_as_strings.append(self.get_shared_parameter_data_storage_as_string())
        storage_as_strings.append(self.get_warnings_data_storage_as_string())

        # build single dictionary by data type:
        for d in storage_as_strings:
            return_value[d.key] = d.value
        return return_value

    def _get_storage_headers_of_type(storage_property):
        """
        Loops of the storage instances saved in the storage property names of this class.

        :param storage_property: a property of this class containing IFamilyDataStorage instances
        :type storage_property: :class:`.Result` IFamilyDataStorage
        :return: A single nested list of strings representing storage instance property names
        :rtype: [[str]]
        """
        data = []
        for storage in storage_property:
            if isinstance(storage, IFamilyDataStorage) == False:
                raise TypeError(
                    "Storage should of type IFamilyDataStorage but is [{}]".format(
                        type(storage)
                    )
                )
            data.append(storage.get_property_names())
            # we only need one entry
            break
        return data

    def get_family_base_data_storage_headers_as_string(self):
        """
        Returns all family base data instance storage property as string

        :return: A dictionary where key is the storage data type, and value is a nested list of strings representing each storage property name
        :rtype: {str:[[str]]}
        """
        data = self._get_storage_headers_of_type(
            storage_property=self.family_base_data_storage
        )
        return {FamilyBaseDataStorage.data_type: data}

    def get_family_category_data_storage_headers_as_string(self):
        """
        Returns all family category data instance storage as string

        :return: A dictionary where key is the storage data type, and value is a nested list of strings representing each storage property name
        :rtype: {str:[[str]]}
        """
        data = self._get_storage_headers_of_type(
            storage_property=self.category_data_storage
        )
        return {FamilyCategoryDataStorage.data_type: data}

    def get_line_pattern_data_storage_headers_as_string(self):
        """
        Returns all family line pattern data instance storage as string

        :return: A dictionary where key is the storage data type, and value is a nested list of strings representing each storage property name
        :rtype: {str:[[str]]}
        """
        data = self._get_storage_headers_of_type(
            storage_property=self.line_pattern_data_storage
        )
        return {FamilyLinePatternDataStorage.data_type: data}

    def get_shared_parameter_data_storage_headers_as_string(self):
        """
        Returns all family shared parameter data instance storage as string

        :return: A dictionary where key is the storage data type, and value is a nested list of strings representing each storage property name
        :rtype: {str:[[str]]}
        """
        data = self._get_storage_headers_of_type(
            storage_property=self.shared_parameter_data_storage
        )
        return {FamilySharedParameterDataStorage.data_type: data}

    def get_warnings_data_storage_headers_as_string(self):
        """
        Returns all family warnings data instance storage as string

        :return: A dictionary where key is the storage data type, and value is a nested list of strings representing each storage property name
        :rtype: {str:[[str]]}
        """
        data = self._get_storage_headers_of_type(
            storage_property=self.warnings_data_storage
        )
        return {FamilyWarningsDataStorage.data_type: data}

    def get_data_headers_list(self):
        """
        returns a dictionary where key is the storage data type and value is a nested list of list of string representing the data storage property names

        :return: Dictionary
        :rtype: {str:[[str]]}
        """
        return_value = {}
        storage_as_strings = []

        # get all storage data as string ( represented in dictionary where key is the data type and values list of lists containing the storage data)
        storage_as_strings.append(self.get_family_base_data_storage_headers_as_string())
        storage_as_strings.append(
            self.get_family_category_data_storage_headers_as_string()
        )
        storage_as_strings.append(
            self.get_line_pattern_data_storage_headers_as_string()
        )
        storage_as_strings.append(
            self.get_shared_parameter_data_storage_headers_as_string()
        )
        storage_as_strings.append(self.get_warnings_data_storage_headers_as_string())

        # build single dictionary by data type:
        for d in storage_as_strings:
            return_value[d.key] = d.value
        return return_value
