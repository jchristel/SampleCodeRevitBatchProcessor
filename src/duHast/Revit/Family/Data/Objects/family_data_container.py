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
        :type family_base_data_storage: list
        :param category_data_storage: a list of FamilyCategoryDataStorage instances
        :type category_data_storage: list
        :param line_pattern_data_storage: a list of FamilyLinePatternDataStorage instances
        :type line_pattern_data_storage: list
        :param shared_parameter_data_storage: a list of FamilySharedParameterDataStorage instances
        :type shared_parameter_data_storage: list
        :param warnings_data_storage: a list of FamilyWarningsDataStorage instances
        :type warnings_data_storage: list
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

        # set other class properties based on storage
        self.family_name = storage_instance.family_name
        self.family_file_path = storage_instance.family_file_path
        self.family_nesting_path = storage_instance.root_name_path
        self.family_category_nesting_path = storage_instance.root_category_path

        # check if this is a root family
        if "::" in storage_instance.root_name_path:
            self.is_root_family = False
        else:
            self.is_root_family = True


    def add_family_base_data_storage(self, other):
        """
        Will add a family base data storage instance and infer some other class properties from it.

        Note: if storage data properties root_name_path and root_category_path are different to the current values
        all other storage properties will be wiped to avoid mismatches!

        :param other: _description_
        :type other: _type_
        :raises ValueError: _description_
        """
        # check is correct object type
        if isinstance(other, FamilyBaseDataStorage) == False:
            raise ValueError("other must be a list of FamilyBaseDataStorage")

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
        

    def add_category_data_storage(self, other):
        """
        Will add a category data storage instance.

        Note: an exception will be raised if family_nesting_path and family_category_nesting_path do not match the current values!

        :param other: a data storage instance
        :type other: FamilyCategoryDataStorage
        :raises ValueError: Type mismatch
        """
        # check is correct object type
        if isinstance(other, FamilyCategoryDataStorage) == False:
            raise ValueError("other must be a list of FamilyCategoryDataStorage")

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
        elif(self.family_nesting_path == None and self.family_category_nesting_path == None):
            # looks like this might be the only storage class added or 
            # family base data storage is absent and this is the first storage class added
            self._update_base_properties_from_storage(other)

        # add to class property
        self.category_data_storage.append(other)

    def add_line_pattern_data_storage(self, other):
        """
        Will add a line pattern data storage instance.

        Note: an exception will be raised if family_nesting_path and family_category_nesting_path do not match the current values!

        :param other: a data storage instance
        :type other: FamilyLinePatternDataStorage
        :raises ValueError: Type mismatch
        """
        # check is correct object type
        if isinstance(other, FamilyLinePatternDataStorage) == False:
            raise ValueError("other must be a list of FamilyLinePatternDataStorage")

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

        # add to class property
        self.line_pattern_data_storage.append(other)

    def add_shared_parameter_data_storage(self, other):
        """
        Will add a shared parameter data storage instance.

        Note: an exception will be raised if family_nesting_path and family_category_nesting_path do not match the current values!

        :param other: a data storage instance
        :type other: FamilySharedParameterDataStorage
        :raises ValueError: Type mismatch
        """
        # check is correct object type
        if isinstance(other, FamilySharedParameterDataStorage) == False:
            raise ValueError("other must be a list of FamilySharedParameterDataStorage")

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

        # add to class property
        self.shared_parameter_data_storage.append(other)

    def add_warnings_data_storage(self, other):
        """
        Will add a warnings data storage instance.

        Note: an exception will be raised if family_nesting_path and family_category_nesting_path do not match the current values!

        :param other: a data storage instance
        :type other: FamilyWarningsDataStorage
        :raises ValueError: Type mismatch
        """
        # check is correct object type
        if isinstance(other, FamilyWarningsDataStorage) == False:
            raise ValueError("other must be a list of FamilyWarningsDataStorage")

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

        # add to class property
        self.warnings_data_storage.append(other)
