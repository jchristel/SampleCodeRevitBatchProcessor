'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Interface for family processing class.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#License:
#
#
# Revit Batch Processor Sample Code
#
# Copyright (c) 2022  Jan Christel
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#

import System
import Autodesk.Revit.DB as rdb
import json
from duHast.APISamples.Family.Data import ifamily_data as IFamData
from duHast.Utilities import Result as res
from duHast.Utilities import Base

class IFamilyProcessor(Base.Base):
    
    def __init__(self, data_type = 'not declared', pre_actions = None, post_actions = None, string_report_headers = [], **kwargs):
        
        # forwards all unused arguments
        # ini super class to allow multi inheritance in children!
        super(IFamilyProcessor, self).__init__(**kwargs) 

        self.data = []
        self.data_type = data_type
        self.string_report_headers = string_report_headers
        self.pre_actions = pre_actions
        self.post_actions = post_actions

    # -------------------------------------- utility ----------------------

    def _update_Data(self, processor, identify_by_this_property_name, identify_by_this_property_value, update_by_property_name, updated_to_this_property_value):
        update_status = processor.update_Data(identify_by_this_property_name, identify_by_this_property_value, update_by_property_name, updated_to_this_property_value)
        return update_status


    def _find_root_family_processor(self):
        '''
        Finds the processor instance which processed the root family.

        :return: Processor instance
        :rtype: IFamilyProcessor
        '''

        for processor in self.data:
            for d in processor.get_Data():
                if ' :: ' not in d[IFamData.ROOT]:
                    return processor

    def _find_root_family_data(self):
        '''
        Returns all data from root families (top most in tree) from all processor instances.

        :param data: List of dictionaries.
        :type data: [{}]

        :return: List of dictionaries.
        :rtype: [{}]
        '''

        family_data = []
        for processor in self.data:
            for d in processor.get_Data():
                if ' :: ' not in d[IFamData.ROOT]:
                    family_data.append (d)
        return family_data
    
    def _find_nested_families_data(self):
        '''
        Returns all data from nested families from each processor instances.

        :param data: List of dictionaries.
        :type data: [{}]

        :return: List of dictionaries.
        :rtype: [{}]
        '''

        nested_family_data = []
        for processor in self.data:
            for d in processor.get_Data():
                if ' :: ' in d[IFamData.ROOT]:
                    nested_family_data.append (d)
        return nested_family_data

    def _fix_data_types(self, flattened_dic):
        '''
        Replace any ElementId and Byte values with int or string respectively to have JSON working ok.
        Any other type of values are not changed.

        :param flattened_dic: Dictionary of which values are to be converted.
        :type flattened_dic: {}
        :return: Dictionary with converted values.
        :rtype: {}
        '''
        
        dic= {}
        for key in flattened_dic:
            if(type(flattened_dic[key]) is rdb.ElementId):
                dic[key] = flattened_dic[key].IntegerValue
            elif (type(flattened_dic[key]) is System.Byte):
                dic[key] = str(flattened_dic[key])
            else:
                dic[key] = flattened_dic[key]
        return dic
    
    # -------------------------------------- pre process actions ----------------------

    def pre_process_actions(self, doc):
        '''
        Actions any pre processing before family data will be collected.

        :param doc: The family document. 
        :type doc: Autodesk.Revit.DB.Document

        :return: _description_
        :rtype: _type_
        '''

        return_value = res.Result()
        if(self.pre_actions != None):
            for pre_action in self.pre_actions:
                result_action = pre_action(doc)
                return_value.update(result_action)
        return return_value
    
    # -------------------------------------- process actions ----------------------

    def process(self, doc, root_path, root_category_path):
        '''
        Gather data on the root family and any nested families

        :param doc: The family document. 
        :type doc: Autodesk.Revit.DB.Document

        :param root_path: The path of the nested family in a tree: rootFamilyName::nestedFamilyNameOne::nestedFamilyTwo\
            This includes the actual family name as the last node.
        :type root_path: str
        :param root_category_path: The path of the nested family category in a tree: rootFamilyCategory::nestedFamilyOneCategory::nestedFamilyTwoCategory\
            This includes the actual family category as the last node.
        :type root_category_path: str
        '''

        pass

    # -------------------------------------- post process actions ----------------------

    def post_process_actions(self, doc):
        '''
        Actions any post processing after family data has been collected.

        :param doc: The family document. 
        :type doc: Autodesk.Revit.DB.Document
        '''

        return_value = res.Result()
        if(self.post_actions != None):
            for post_action in self.post_actions:
                result_action = post_action(doc)
                return_value.update(result_action)
        return return_value

    # -------------------------------------- get data ----------------------

    def get_data(self):
        '''
        Returns list of flattened dictionaries. One dictionary for each document processed.

        :return: List of dictionaries.
        :rtype: [{}]
        '''

        data_out = []
        for data in self.data:
            for d in data.get_Data():
                data_out.append(d)
        return data_out

    def get_data_json(self):
        '''
        Returns data objects as JSON formatted strings.

        :return: JSON formatted string.
        :rtype: str
        '''

        out_value = ''
        flattened_data = self.get_data()
        for d in flattened_data:
            d_fixed_types = self._fix_data_types(d)
            json_object = json.dumps(dict(d_fixed_types))
            out_value = out_value + '\n' + json_object
        return out_value

    def get_data_string_list(self):
        '''
        Returns data objects as list of strings in order of headers list of this class.

        - Strings are UTF 8 encoded
        - Unknown header values are marked as 'null'

        :return: list of string.
        :rtype: [str]
        '''
        out_value = []
        flattened_data = self.get_data()
        for d in flattened_data:
            row = []
            for header_key in self.string_report_headers:
                if(header_key in d):
                    value = None
                    if(type(d[header_key]) == str):
                        # make sure string is utf-8 encoded
                        value = d[header_key].encode('utf-8', 'ignore')
                    else:
                        value = str(d[header_key])
                    row.append(value)
                else:
                    row.append('null')
            out_value.append(row)
        return out_value