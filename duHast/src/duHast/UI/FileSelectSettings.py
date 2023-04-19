'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A class to store file select UI settings.
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

from duHast.Utilities import Base

# An item to represent a file name in a row in a grid.
class FileSelectionSettings(Base.Base):
    
    def __init__(self, inputDirectory, include_sub_dirs_in_search, output_directory, output_file_number, revitFileExtension):
        '''
        Class constructor

        :param inputDirectory: A fully qualified directory path containing files to be shown in UI.
        :type inputDirectory: str
        :param include_sub_dirs_in_search: If True include subdirectories in file search, otherwise just root directory.
        :type include_sub_dirs_in_search: bool
        :param output_directory: A fully qualified directory path to where task files will be written.
        :type output_directory: str
        :param output_file_number: The number of task files to be written out.
        :type output_file_number: int
        :param revitFileExtension: A file extension filter applied to directory search.
        :type revitFileExtension: str
        '''

        self.input_directory = inputDirectory
        self.incl_sub_dirs = include_sub_dirs_in_search
        self.output_dir = output_directory
        self.output_file_num = output_file_number
        self.revit_file_extension = revitFileExtension

        # ini super class to allow multi inheritance in children!
        super(FileSelectionSettings, self).__init__() 