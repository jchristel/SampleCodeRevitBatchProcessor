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
from duHast.Revit.Family.Data.Objects.family_base_data_storage import FamilyBaseDataStorage
from duHast.Revit.Categories.Data.Objects.category_data_storage import FamilyCategoryDataStorage
from duHast.Revit.LinePattern.Data.Objects.line_pattern_data_storage import FamilyLinePatternDataStorage
from duHast.Revit.SharedParameters.Data.Objects.shared_parameter_data_storage import FamilySharedParameterDataStorage
from duHast.Revit.Warnings.Data.Objects.warnings_data_storage import FamilyWarningsDataStorage


class FamilyDataContainer(base.Base):
    def __init__(
        self,
        family_base_data_storage = None,
        category_data_storage = None,
        line_pattern_data_storage = None,
        shared_parameter_data_storage = None,
        warnings_data_storage = None,
        **kwargs
    ):

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
        self.family_base_data_storage = []
        if family_base_data_storage is None:
            # no change required 
            pass
        else:
            if isinstance(family_base_data_storage, list):
                # check if every member of the list is an instance of FamilyBaseDataStorage
                if all(isinstance(x, FamilyBaseDataStorage) for x in family_base_data_storage):
                    # should only ever be one entry!
                    if(len(family_base_data_storage)>1):
                        raise ValueError ("family_base_data_storage can only ever have one entry")
                    else:
                        self.add_family_base_data_storage(family_base_data_storage)
                else:
                    raise ValueError("family_base_data_storage must be a list of FamilyBaseDataStorage")
            elif isinstance(family_base_data_storage, FamilyBaseDataStorage):
                self.add_family_base_data_storage(family_base_data_storage)
            else:
                raise ValueError("family_base_data_storage must be a list or FamilyBaseDataStorage")
        
        # category data storage
        if category_data_storage is None:
            self.category_data_storage = []
        else:
            if isinstance(category_data_storage, list):
                # check if every member of the list is an instance of FamilyCategoryDataStorage
                if all(isinstance(x, FamilyCategoryDataStorage) for x in category_data_storage):
                    self.category_data_storage = category_data_storage
                else:
                    raise ValueError("category_data_storage must be a list of FamilyCategoryDataStorage")
            elif isinstance(category_data_storage, FamilyCategoryDataStorage):
                self.category_data_storage = [category_data_storage]
            else:
                raise ValueError("category_data_storage must be a list or FamilyCategoryDataStorage")
        
        # line pattern data storage
        if line_pattern_data_storage is None:
            self.line_pattern_data_storage = []
        elif isinstance(line_pattern_data_storage, list):
            # check if every member of the list is an instance of FamilyLinePatternDataStorage
            if all(isinstance(x, FamilyLinePatternDataStorage) for x in line_pattern_data_storage):
                self.line_pattern_data_storage = line_pattern_data_storage
            else:
                raise ValueError("line_pattern_data_storage must be a list of FamilyLinePatternDataStorage")
        elif isinstance(line_pattern_data_storage, FamilyLinePatternDataStorage):
            self.line_pattern_data_storage = [line_pattern_data_storage]
        else:
            raise ValueError("line_pattern_data_storage must be a list or FamilyLinePatternDataStorage")
        
        # shared parameter data storage
        if shared_parameter_data_storage is None:
            self.shared_parameter_data_storage = []
        elif isinstance(shared_parameter_data_storage, list):
            # check if every member of the list is an instance of FamilySharedParameterDataStorage
            if all(isinstance(x, FamilySharedParameterDataStorage) for x in shared_parameter_data_storage):
                self.shared_parameter_data_storage = shared_parameter_data_storage
            else:
                raise ValueError("shared_parameter_data_storage must be a list of FamilySharedParameterDataStorage")
        elif isinstance(shared_parameter_data_storage, FamilySharedParameterDataStorage):
            self.shared_parameter_data_storage = [shared_parameter_data_storage]
        else:
            raise ValueError("shared_parameter_data_storage must be a list or FamilySharedParameterDataStorage")
        
        # warnings data storage
        if warnings_data_storage is None:
            self.warnings_data_storage = []
        elif isinstance(warnings_data_storage, list):
            # check if every member of the list is an instance of FamilyWarningsDataStorage
            if all(isinstance(x, FamilyWarningsDataStorage) for x in warnings_data_storage):
                self.warnings_data_storage = warnings_data_storage
            else:
                raise ValueError("warnings_data_storage must be a list of FamilyWarningsDataStorage")
        elif isinstance(warnings_data_storage, FamilyWarningsDataStorage):
            self.warnings_data_storage = [warnings_data_storage]
        else:
            raise ValueError("warnings_data_storage must be a list or FamilyWarningsDataStorage")
    
    def add_family_base_data_storage(self, other):
        """
        Will add a family base data storage instance and infere some other class properties from it.

        Note: if storage data properties root_name_path and root_category_path are different to the current values
        all other storage properties will be wiped to avoid mismatches!

        :param other: _description_
        :type other: _type_
        :raises ValueError: _description_
        """
        # check is correct object type
        if isinstance(other, FamilyBaseDataStorage)==False:
            raise ValueError("other must be a list of FamilyBaseDataStorage")
        
        # there is always only going to be one entry in list!
        if (len(self.family_base_data_storage)>0):
            self.family_base_data_storage.pop()
        
        # add to class property
        self.family_base_data_storage.append(other)

        # set other class properties based on storage:
        # check if nesting path and category nesting path are different to the current values
        # if so wipe the other storage properties to avoid mismatches!
        

        self.family_name = other.family_name
        self.family_file_path = other.family_file_path
        self.family_nesting_path = other.root_name_path
        self.family_category_nesting_path = other.root_category_path
        
        
        