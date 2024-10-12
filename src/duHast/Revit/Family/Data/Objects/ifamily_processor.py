"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Interface for family processing class.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

#!/usr/bin/python
# -*- coding: utf-8 -*-
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

import System
from Autodesk.Revit.DB import ElementId
import json
from duHast.Revit.Family.Data.Objects import ifamily_data as IFamData
from duHast.Revit.Family.Data.Objects.ifamily_data_storage import IFamilyDataStorage
from duHast.Utilities.Objects import result as res
from duHast.Utilities.Objects import base
from duHast.Revit.Family.Data.Objects.family_base_data_processor_defaults import (
    NESTING_SEPARATOR,
)


class IFamilyProcessor(base.Base):

    data_type_header = "Data Type"  # Data type header

    def __init__(self, data_type=None, pre_actions=None, post_actions=None, **kwargs):

        # forwards all unused arguments
        # ini super class to allow multi inheritance in children!
        super(IFamilyProcessor, self).__init__(**kwargs)

        self.data = []

        # check if data type is set
        if data_type != None:
            self.data_type = data_type
        else:
            self.data_type = "not declared"

        self.pre_actions = pre_actions
        self.post_actions = post_actions

    # -------------------------------------- utility ----------------------

    def _update_data(
        self,
        processor,
        identify_by_this_property_name,
        identify_by_this_property_value,
        update_by_property_name,
        updated_to_this_property_value,
    ):
        update_status = processor.update_Data(
            identify_by_this_property_name,
            identify_by_this_property_value,
            update_by_property_name,
            updated_to_this_property_value,
        )
        return update_status

    def _find_first_root_family_data(self):
        """
        Finds the data instance which contains the processed the root family.

        :return: data instance
        :rtype: IFamilyData
        """

        for data in self.data:
            if isinstance(data, IFamData.IFamilyData):

                data_stored = data.get_data()
                if isinstance(data_stored, list):
                    for storage_entry in data_stored:
                        if isinstance(storage_entry, IFamilyDataStorage):
                            if NESTING_SEPARATOR not in storage_entry.root_name_path:
                                return data
                        else:
                            raise ValueError(
                                "Data must be of type IFamilyDataStorage but is of type: [{}]".format(
                                    type(storage_entry)
                                )
                            )
                else:
                    raise ValueError(
                        "Data must be of type list but is of type: [{}]".format(
                            type(data_stored)
                        )
                    )
            else:
                raise ValueError(
                    "Data must be of type IFamilyData but is of type: [{}]".format(
                        type(data)
                    )
                )

    def _find_root_family_data(self):
        """
        Returns all data instances from root families (top most in tree) .

        :return: List of data instances.
        :rtype: [IFamilyData]
        """
        family_data = []
        for data in self.data:
            if isinstance(data, IFamData.IFamilyData):
                if NESTING_SEPARATOR not in data.root_path:
                    family_data.append(data)
            else:
                raise ValueError(
                    "Data must be of type IFamilyData but is of type: [{}]".format(
                        type(data)
                    )
                )
        return family_data

    def _find_nested_families_data(self):
        """
        Returns all data instances from nested families from each processor instances.

        :return: List of dictionaries.
        :rtype: [IFamilyData]
        """

        nested_family_data = []

        for data in self.data:
            if isinstance(data, IFamData.IFamilyData):
                if NESTING_SEPARATOR in data.root_path:
                    nested_family_data.append(data)
            else:
                raise ValueError(
                    "Data must be of type IFamilyData but is of type: [{}]".format(
                        type(data)
                    )
                )

        return nested_family_data

    # -------------------------------------- pre process actions ----------------------

    def pre_process_actions(self, doc):
        """
        Actions any pre processing before family data will be collected.

        :param doc: The family document.
        :type doc: Autodesk.Revit.DB.Document

        :return: _description_
        :rtype: _type_
        """

        return_value = res.Result()
        if self.pre_actions != None:
            for pre_action in self.pre_actions:
                result_action = pre_action(doc)
                return_value.update(result_action)
        return return_value

    # -------------------------------------- process actions ----------------------

    def process(self, doc, root_path, root_category_path):
        """
        Gather data on the root family and any nested families

        :param doc: The family document. 
        :type doc: Autodesk.Revit.DB.Document

        :param root_path: The path of the nested family in a tree: rootFamilyName :: nestedFamilyNameOne :: nestedFamilyTwo\
            This includes the actual family name as the last node.
        :type root_path: str
        :param root_category_path: The path of the nested family category in a tree: rootFamilyCategory :: nestedFamilyOneCategory :: nestedFamilyTwoCategory\
            This includes the actual family category as the last node.
        :type root_category_path: str
        """

        pass

    # -------------------------------------- post process actions ----------------------

    def post_process_actions(self, doc):
        """
        Actions any post processing after family data has been collected.

        :param doc: The family document.
        :type doc: Autodesk.Revit.DB.Document
        """

        return_value = res.Result()
        if self.post_actions != None:
            for post_action in self.post_actions:
                result_action = post_action(doc)
                return_value.update(result_action)
        return return_value

    # -------------------------------------- get data ----------------------

    def get_data(self):
        """
        Returns list of data storage instances.

        :return: List of iFamilyStorage instances.
        :rtype: [iFamilyStorage]
        """

        data_out = []
        for data in self.data:
            if isinstance(data, IFamData.IFamilyData):
                data_stored = data.get_data()
                if isinstance(data_stored, list):
                    for storage_entry in data_stored:
                        if isinstance(storage_entry, IFamilyDataStorage):
                            data_out.append(storage_entry)
                        else:
                            raise ValueError(
                                "Data must be of type IFamilyDataStorage but is of type: [{}]".format(
                                    type(storage_entry)
                                )
                            )
                else:
                    raise ValueError(
                        "Data must be of type list but is of type: [{}]".format(
                            type(data_stored)
                        )
                    )
            else:
                raise ValueError(
                    "Data must be of type IFamilyData but is of type: [{}]".format(
                        type(data)
                    )
                )
        return data_out

    def get_data_json(self):
        """
        Returns data objects as JSON formatted strings.

        :return: JSON formatted string.
        :rtype: str
        """

        out_value = ""
        flattened_storage_data = self.get_data()
        for storage in flattened_storage_data:
            json_object = storage.to_json()
            out_value = out_value + "\n" + json_object
        return out_value

    def get_data_string_list(self):
        """
        Returns data storage objects as nested list of strings, where each inner list represents the values of a data storage object.

        - Strings are UTF 8 encoded


        :return: list of list of strings.
        :rtype: [str]
        """
        out_value = []

        flattened_storage_data = self.get_data()
        # print("flattened_storage_data: ", flattened_storage_data)
        for storage in flattened_storage_data:
            out_value.append(storage.get_data_values_as_list_of_strings())
            # print("out_value: ", out_value)

        # print("out_value: ", out_value)
        return out_value

    def get_data_headers(self):
        """
        Returns the headers of the data storage objects.

        :return: list of strings.
        :rtype: [str]
        """

        # get the first storage object
        if len(self.data) > 0:
            data_instance = self.data[0]
            return data_instance.get_property_names()
        else:
            return []
