'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A class to store file information.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

#
#License:
#
#
# Revit Batch Processor Sample Code
#
# Copyright (c) 2020  Jan Christel
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

# An item to represent a file name in a row in a grid.

from duHast.Utilities import Base

class MyFileItem(Base.Base):
    
    def __init__(self, name, size,  BIM360ProjectGuid = None , BIM360FileGuid = None, BIM360RevitVersion = '-'):
        '''
        Class constructor.

        :param name: The fully qualified file path.
        :type name: str
        :param size: The file size.
        :type size: int
        :param  BIM360ProjectGuid: The BIM360 project GUID, defaults to None
        :type  BIM360ProjectGuid: str, optional
        :param BIM360FileGuid: The BIM360 file GUID, defaults to None
        :type BIM360FileGuid: str, optional
        :param BIM360RevitVersion: The revit file version (year only), defaults to '-'
        :type BIM360RevitVersion: str, optional
        '''

        # ini super class to allow multi inheritance in children!
        super(MyFileItem, self).__init__() 
        
        self.name = name
        self.size = size
        self.bim_360_project_guid =  BIM360ProjectGuid
        self.bim_360_file_guid = BIM360FileGuid
        self.bim_360_revit_version = BIM360RevitVersion