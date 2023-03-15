'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Data base class for Revit object properties.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

#
#License:
#
#
# Revit Batch Processor Sample Code
#
# Copyright (c) 2023  Jan Christel
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

class DataBase(object):

    def __init__(self, data_type):
        self.dataType = data_type

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
    
    @property
    def DataType(self):
        '''
        Property: returns the data type of this class.

        :return: 'ceiling'
        :rtype: str
        '''

        return self.dataType