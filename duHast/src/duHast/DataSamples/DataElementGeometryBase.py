'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Data geometry storage base class for Revit elements.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- contains 

    - polygon
    - topology cell (WIP)
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

import json

from duHast.DataSamples import DataGeometryPolygon
from duHast.DataSamples import DataGeometryTopoCell

class DataElementGeometryBase(object):
    
    def __init__(self, j , **kwargs):
        '''
        Class constructor

        :param j: Json formatted string or dictionary
        :type j: str or dic

        :raises ValueError: 'Argument supplied must be of type string or type dictionary'
        '''

        # ini super class to allow multi inheritance in children!
        super(DataElementGeometryBase, self).__init__(**kwargs)  # forwards all unused arguments
        # check valid j input
        if(j != None and len(j) > 0 ):
            # check type of data that came in: 
            if(type(j) == str):
                # a string
                j = json.loads(j)
            elif(type(j) == dict):
                # no action required
                pass
            else:
                raise  ValueError ('Argument supplied must be of type string or type dictionary')
            
            # check for polygon data
            geometry_data_list = []
            if('geometryPolygon' in j):
                for item in j['geometryPolygon']:
                    if('dataType' in item):
                        if(item['dataType']):
                            dummy = DataGeometryPolygon.DataPolygon(item)
                            geometry_data_list.append(dummy)
                    else:
                        print('no data type in item')
            self.geometryPolygon = geometry_data_list

            # check for topo cell data
            if('geometryTopologicCell' in j):
                self.geometryTopologicCell = DataGeometryTopoCell.DataTopologyCell(j['geometryTopologicCell'])
            else:
                self.geometryTopologicCell = DataGeometryTopoCell.DataTopologyCell()

        else:
            # initialise classes with default values
            self.geometryPolygon = []
            self.geometryTopologicCell = DataGeometryTopoCell.DataTopologyCell()

    def __repr__(self):
        '''
        Enables detailed debug output of all class properties using: rep(obj)

        :return: A string listing class properties and their respective values.
        :rtype: string
        '''

        return '{}({})'.format(self.__class__.__name__, ', '.join('{}={!r}'.format(k, v) for k, v in self.__dict__.items()))
    
    def to_json(self):
        '''
        Convert the instance of this class to json.
        
        :return: A Json object.
        :rtype: json
        '''

        return json.dumps(self, indent = None, default=lambda o: o.__dict__)
    