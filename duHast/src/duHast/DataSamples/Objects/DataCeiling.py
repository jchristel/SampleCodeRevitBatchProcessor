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

import json

#from duHast.DataSamples import DataGeometry
from duHast.DataSamples.Objects.Properties import DataDesignSetOption
from duHast.DataSamples.Objects.Properties import DataPhasing
from duHast.DataSamples.Objects.Properties import DataLevel
from duHast.DataSamples.Objects.Properties import DataTypeProperties
from duHast.DataSamples.Objects.Properties import DataInstanceProperties
from duHast.DataSamples.Objects.Properties import DataRevitModel
from duHast.DataSamples.Utils import DataBase
from duHast.DataSamples.Objects.Properties import DataElementGeometry

class DataCeiling(DataBase.DataBase, DataElementGeometry.DataElementGeometryBase):

    dataType = 'ceiling'
    
    def __init__(self, j = {}):
        '''
        Class constructor.

        :param j: A json formatted dictionary of this class, defaults to {}
        :type j: dict, optional
        '''

        # store data type  in base class
        super(DataCeiling, self).__init__(data_type=DataCeiling.dataType, j=j)
        
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
            
            if ('instanceProperties' in j):
                self.instanceProperties = DataInstanceProperties.DataInstanceProperties(j['instanceProperties'])
            else:
                self.instanceProperties = DataInstanceProperties.DataInstanceProperties()
            
            if('designSetAndOption' in j):
                self.designSetAndOption = DataDesignSetOption.DataDesignSetOption(j['designSetAndOption'])
            else:
                self.designSetAndOption = DataDesignSetOption.DataDesignSetOption()            
            
            if('typeProperties' in j):
                self.typeProperties = DataTypeProperties.DataTypeProperties(j['typeProperties'])
            else:
                self.typeProperties = DataTypeProperties.DataTypeProperties()       

            if('level' in j):
                self.level = DataLevel.DataLevel(j['level'])
            else:
                self.level = DataLevel.DataLevel()

            if('revitModel' in j):
                self.revitModel = DataRevitModel.DataRevitModel(j['revitModel'])
            else:
                self.revitModel = DataRevitModel.DataRevitModel()  

            if('phasing' in j):
                self.phasing = DataPhasing.DataPhasing(j['phasing'])
            else:
                self.phasing = DataPhasing.DataPhasing() 

            # load associated elements
            if('associatedElements' in j):
                self.associatedElements = j['associatedElements']
            else:
                self.associatedElements =[] 

        else:
            self.associatedElements = []
            # initialise classes with default values
            self.instanceProperties = DataInstanceProperties.DataInstanceProperties()
            self.typeProperties = DataTypeProperties.DataTypeProperties()
            self.level = DataLevel.DataLevel()
            self.revitModel = DataRevitModel.DataRevitModel()
            self.phasing = DataPhasing.DataPhasing()
            self.designSetAndOption = DataDesignSetOption.DataDesignSetOption()