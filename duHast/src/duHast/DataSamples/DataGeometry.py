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
from duHast.DataSamples import DataBase

class DataGeometry(DataBase.DataBase):
    dataType = 'polygons'

    def __init__(self, j = {}):
        '''
        Class constructor

        :param j:  json formatted dictionary of this class, defaults to {}
        :type j: dict, optional
        '''

        # store data type  in base class
        super(DataGeometry, self).__init__('polygons')
        
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
                raise  ValueError ('Argument supplied must be of type string or type dictionary')
        
            if('outerLoop' in j ):
                self.outerLoop = j['outerLoop']
            else:
                self.outerLoop = []

            if('innerLoops' in j ):
                self.innerLoops = j['innerLoops']
            else:
                self.innerLoops = []
            
            # translation as per shared coordinates in revit file
            if('translationCoord' in j ):
                self.translationCoord = j['translationCoord']
            else:
                self.translationCoord = [0.0, 0.0, 0.0]
            
            # rotation as per shared coordinates in revit file
            if('rotationCoord' in j ):
                self.rotationCoord = j['rotationCoord']
            else:
                self.rotationCoord = [[0.0, 0.0, 0.0],[0.0, 0.0, 0.0],[0.0, 0.0, 0.0]] 

        else:
            # set default values
            self.outerLoop = []        
            self.innerLoops = []
            self.translationCoord = [0.0, 0.0, 0.0] # translation as per shared coordinates in revit file
            self.rotationCoord = [[0.0, 0.0, 0.0],[0.0, 0.0, 0.0],[0.0, 0.0, 0.0]] # rotation as per shared coordinates in revit file