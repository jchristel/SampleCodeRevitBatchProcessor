
'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Data storage class for Revit room properties.
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

from duHast.Data.Objects.Properties import DataDesignSetOption
from duHast.Data.Objects.Properties import DataPhasing
from duHast.Data.Objects.Properties import DataLevel
from duHast.Data.Objects.Properties import DataInstanceProperties
from duHast.Data.Objects.Properties import DataRevitModel
from duHast.Data.Utils import data_base
from duHast.Data.Objects.Properties import DataElementGeometry

class DataRoom(data_base.DataBase, DataElementGeometry.DataElementGeometryBase):
    data_type = 'room'
    
    def __init__(self, j = {}):
        '''
        Class constructor.

        :param j: A json formatted dictionary of this class, defaults to {}
        :type j: dict, optional
        '''
        
        # initialise parent classes with values
        super(DataRoom, self).__init__(data_type=DataRoom.data_type, j=j)
        
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

            if (DataInstanceProperties.DataInstanceProperties.data_type in j):
                self.instance_properties = DataInstanceProperties.DataInstanceProperties(j[DataInstanceProperties.DataInstanceProperties.data_type])
            else:
                self.instance_properties = DataInstanceProperties.DataInstanceProperties()

            if(DataDesignSetOption.DataDesignSetOption.data_type in j):
                self.design_set_and_option = DataDesignSetOption.DataDesignSetOption(j[DataDesignSetOption.DataDesignSetOption.data_type])
            else:
                self.design_set_and_option = DataDesignSetOption.DataDesignSetOption()
            
            if('associated_elements' in j ):
                self.associated_elements = j['associated_elements']
            else:
                self.associated_elements = []
            
            if(DataLevel.DataLevel.data_type in j):
                self.level = DataLevel.DataLevel(j[DataLevel.DataLevel.data_type])
            else:
                self.level = DataLevel.DataLevel()

            if(DataRevitModel.DataRevitModel.data_type in j):
                self.revit_model = DataRevitModel.DataRevitModel(j[DataRevitModel.DataRevitModel.data_type])
            else:
                self.revit_model = DataRevitModel.DataRevitModel()  

            if(DataPhasing.DataPhasing.data_type in j):
                self.phasing = DataPhasing.DataPhasing(j[DataPhasing.DataPhasing.data_type])
            else:
                self.phasing = DataPhasing.DataPhasing() 
        else:
            # initialise classes with default values
            self.associated_elements = []
            self.instance_properties = DataInstanceProperties.DataInstanceProperties()
            self.level = DataLevel.DataLevel()
            self.revit_model = DataRevitModel.DataRevitModel()
            self.phasing = DataPhasing.DataPhasing()
            self.design_set_and_option = DataDesignSetOption.DataDesignSetOption()