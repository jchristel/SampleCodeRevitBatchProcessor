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
from duHast.APISamples import IFamilyData as IFamData
from duHast.Utilities import Result as res

class IFamilyProcessor():
    
    def __init__(self, preActions = None, postActions = None):
        self.data = []
        self.dataType = 'not declared'
        self.stringReportHeaders = []
        self.preActions = preActions
        self.postActions = postActions

    # -------------------------------------- utility ----------------------

    def _updateData(self, processor, identifyByThisPropertyName, identifyByThisPropertyValue, updateByPropertyName, updatedToThisPropertyValue):
        updateStatus = processor.update_Data(identifyByThisPropertyName, identifyByThisPropertyValue, updateByPropertyName, updatedToThisPropertyValue)
        return updateStatus


    def _findRootFamilyProcessor(self):
        '''
        Finds the processor instance which processed the root family.

        :return: Processor instance
        :rtype: IFamilyProcessor
        '''

        for processor in self.data:
            for d in processor.get_Data():
                if ' :: ' not in d[IFamData.ROOT]:
                    return processor

    def _findRootFamilyData(self):
        '''
        Returns all data from root families (top most in tree) from all processor instances.

        :param data: List of dictionaries.
        :type data: [{}]

        :return: List of dictionaries.
        :rtype: [{}]
        '''

        familyData = []
        for processor in self.data:
            for d in processor.get_Data():
                if ' :: ' not in d[IFamData.ROOT]:
                    familyData.append (d)
        return familyData
    
    def _findNestedFamiliesData(self):
        '''
        Returns all data from nested families from each processor instances.

        :param data: List of dictionaries.
        :type data: [{}]

        :return: List of dictionaries.
        :rtype: [{}]
        '''

        nestedFamilyData = []
        for processor in self.data:
            for d in processor.get_Data():
                if ' :: ' in d[IFamData.ROOT]:
                    nestedFamilyData.append (d)
        return nestedFamilyData

    def _fixDataTypes(self, flattenedDic):
        '''
        Replace any ElementId and Byte values with int or string respectively to have JSON working ok.
        Any other type of values are not changed.

        :param flattenedDic: Dictionary of which values are to be converted.
        :type flattenedDic: {}
        :return: Dictionary with converted values.
        :rtype: {}
        '''
        
        dic= {}
        for key in flattenedDic:
            if(type(flattenedDic[key]) is rdb.ElementId):
                dic[key] = flattenedDic[key].IntegerValue
            elif (type(flattenedDic[key]) is System.Byte):
                dic[key] = str(flattenedDic[key])
            else:
                dic[key] = flattenedDic[key]
        return dic
    
    # -------------------------------------- pre process actions ----------------------

    def preProcessActions(self, doc):
        '''
        Actions any pre processing before family data will be collected.

        :param doc: The family document. 
        :type doc: Autodesk.Revit.DB.Document

        :return: _description_
        :rtype: _type_
        '''

        returnValue = res.Result()
        if(self.preActions != None):
            for preAction in self.preActions:
                resultAction = preAction(doc)
                returnValue.Update(resultAction)
        return returnValue
    
    # -------------------------------------- process actions ----------------------

    def process(self, doc, rootPath, rootCategoryPath):
        '''
        Gather data on the root family and any nested families

        :param doc: The family document. 
        :type doc: Autodesk.Revit.DB.Document

        :param rootPath: The path of the nested family in a tree: rootFamilyName::nestedFamilyNameOne::nestedFamilyTwo\
            This includes the actual family name as the last node.
        :type rootPath: str
        :param rootCategoryPath: The path of the nested family category in a tree: rootFamilyCategory::nestedFamilyOneCategory::nestedFamilyTwoCategory\
            This includes the actual family category as the last node.
        :type rootCategoryPath: str
        '''

        pass

    # -------------------------------------- post process actions ----------------------

    def postProcessActions(self, doc):
        '''
        Actions any post processing after family data has been collected.

        :param doc: The family document. 
        :type doc: Autodesk.Revit.DB.Document
        '''

        returnValue = res.Result()
        if(self.postActions != None):
            for postAction in self.postActions:
                resultAction = postAction(doc)
                returnValue.Update(resultAction)
        return returnValue

    # -------------------------------------- get data ----------------------

    def get_Data(self):
        '''
        Returns list of flattened dictionaries. One dictionary for each document processed.

        :return: List of dictionaries.
        :rtype: [{}]
        '''

        dataOut = []
        for data in self.data:
            for d in data.get_Data():
                dataOut.append(d)
        return dataOut

    def get_Data_JSON(self):
        '''
        Returns data objects as JSON formatted strings.

        :return: JSON formatted string.
        :rtype: str
        '''

        outValue = ''
        flattenedData = self.get_Data()
        for d in flattenedData:
            dFixedTypes = self._fixDataTypes(d)
            json_object = json.dumps(dict(dFixedTypes))
            outValue = outValue + '\n' + json_object
        return outValue

    def get_Data_StringList(self):
        '''
        Returns data objects as list of strings in order of headers list of this class.

        - Strings are UTF 8 encoded
        - Unknown header values are marked as 'null'

        :return: list of string.
        :rtype: [str]
        '''
        outValue = []
        flattenedData = self.get_Data()
        for d in flattenedData:
            row = []
            for headerKey in self.stringReportHeaders:
                if(headerKey in d):
                    value = None
                    if(type(d[headerKey]) == str):
                        # make sure string is utf-8 encoded
                        value = d[headerKey].encode('utf-8', 'ignore')
                    else:
                        value = str(d[headerKey])
                    row.append(value)
                else:
                    row.append('null')
            outValue.append(row)
        return outValue