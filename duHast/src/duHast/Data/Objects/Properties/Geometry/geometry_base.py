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

import json
from duHast.Data.Utils import data_base

class DataGeometryBase(data_base.DataBase):

    def __init__(self, data_type, j = {}):
        '''
        Class constructor

        :param j:  json formatted dictionary of this class, defaults to {}
        :type j: dict, optional
        '''

        # store data type  in base class
        super(DataGeometryBase, self).__init__(data_type)
        
        # check if any data was past in with constructor!
        if(j != None and len(j) > 0 ):
            # check type of data that came in: 
            if(type(j) == str):
                # a string
                j = json.loads(j)
            elif(type(j) == dict):
                # no action required
                pass
            else:
                print('j', j)
                raise  ValueError ('Argument supplied must be of type string or type dictionary')
            
            # translation as per shared coordinates in revit file
            if('translation_coord' in j ):
                self.translation_coord = j['translation_coord']
            else:
                self.translation_coord = [0.0, 0.0, 0.0]
            
            # rotation as per shared coordinates in revit file
            if('rotation_coord' in j ):
                self.rotation_coord = j['rotation_coord']
            else:
                self.rotation_coord = [[0.0, 0.0, 0.0],[0.0, 0.0, 0.0],[0.0, 0.0, 0.0]] 

        else:
            # set default values
            self.translation_coord = [0.0, 0.0, 0.0] # translation as per shared coordinates in revit file
            self.rotation_coord = [[0.0, 0.0, 0.0],[0.0, 0.0, 0.0],[0.0, 0.0, 0.0]] # rotation as per shared coordinates in revit file