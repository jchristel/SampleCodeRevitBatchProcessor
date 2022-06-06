'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Geometry data storage class.
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

class DataGeometry():
    
    def __init__(self, j = {}
        ):
        '''
        Class constructor

        :param j:  json formatted dictionary of this class, defaults to {}
        :type j: dict, optional
        '''

        self.dataType = 'polygons'
        self.outerLoop = []        
        self.innerLoops = []
        self.translationCoord = [0.0, 0.0, 0.0] # translation as per shared coordinates in revit file
        self.rotationCoord = [[0.0, 0.0, 0.0],[0.0, 0.0, 0.0],[0.0, 0.0, 0.0]] # rotation as per shared coordinates in revit file
        if(len(j) > 0 ):
            if(type(j) == str):
                self.__dict__ = json.loads(j)
            elif(type(j) == dict):
                self.__dict__ = j
       
    def to_json(self):
        '''
        Convert the instance of this class to json.

        :return: A Json object.
        :rtype: json
        '''

        return json.dumps(self, indent = None, default=lambda o: o.__dict__)