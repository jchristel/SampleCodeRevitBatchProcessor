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

# An item to represent a file name in a row in a grid.
class FileSelectionSettings:
    
    def __init__(self, inputDirectory, includeSubDirsInSearch, outputDirectory, outputFileNumber, revitFileExtension):
        '''
        Class constructor

        :param inputDirectory: A fully qualified directory path containing files to be shown in UI.
        :type inputDirectory: str
        :param includeSubDirsInSearch: If True include subdirectories in file search, otherwise just root directory.
        :type includeSubDirsInSearch: bool
        :param outputDirectory: A fully qualified directory path to where task files will be written.
        :type outputDirectory: str
        :param outputFileNumber: The number of task files to be written out.
        :type outputFileNumber: int
        :param revitFileExtension: A file extension filter applied to directory search.
        :type revitFileExtension: str
        '''

        self.inputDir = inputDirectory
        self.inclSubDirs = includeSubDirsInSearch
        self.outputDir = outputDirectory
        self.outputFileNum = outputFileNumber
        self.revitFileExtension = revitFileExtension