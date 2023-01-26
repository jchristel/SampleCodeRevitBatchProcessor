'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Data storage class for Revit ceiling properties.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''
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

'''
TODO: implement an interface 
'''

import json
from duHast.DataSamples import DataGeometry
from duHast.DataSamples import DataDesignSetOption

class DataCeiling():
    dataType = 'ceiling'
    def __init__(self, j = {}):
        '''
        constructor
        '''
        self.dataType = 'ceiling'
        self.id = -1
        self.typeName = '-'
        self.typeMark = '-'
        self.mark = '-'
        self.levelName = '-'
        self.levelId = '-'
        self.offsetFromLevel = 0.0
        self.modelName = '-'
        self.phaseCreated = '-'
        self.phaseDemolished = '-'
        self.geometry = [[]]
        self.designSetAndOption = DataDesignSetOption.DataDesignSetOption()
        self.associatedElements = []
        if(len(j) > 0 ):
            self.__dict__ = json.loads(j)
            # custom deserialization code...
            geoDataList = []
            for item in self.geometry:
                if('dataType' in item):
                    if(item['dataType']):
                        dummy = DataGeometry.DataGeometry(item)
                        geoDataList.append(dummy)
                    else:
                        print('no data type in item')
            self.geometry = geoDataList
            # initialise design option
            self.designSetAndOption = DataDesignSetOption.DataDesignSetOption(self.designSetAndOption)

    @property
    def DataType(self):
        '''
        Property: returns the data type of this class.

        :return: 'ceiling'
        :rtype: str
        '''

        return self.dataType

    def to_json(self):
        '''
        Convert the instance of this class to json.

        :return: A Json object.
        :rtype: json
        '''

        return json.dumps(self, indent = None, default=lambda o: o.__dict__)
        
        