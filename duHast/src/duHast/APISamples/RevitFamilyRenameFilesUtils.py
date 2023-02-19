'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Helper functions to read rename directives file(s) and return them as a tuple to the caller
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

These helper function expect a text file in csv format with 4 columns:

- Current family name: with out the file extension
- File path	: fully qualified file path to the family file.
- Family category: the Revit category of the family.
- New family name: the new family name without the file extension.

Note:

- First row is treated as a header row and its content is ignored.

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

import clr
import System
from collections import namedtuple
from duHast.Utilities.timer import Timer

from duHast.Utilities import Result as res
from duHast.Utilities import Utility as util
from duHast.APISamples import RevitFamilyBaseDataUtils as rFamBaseDUtils

# tuples containing rename directive read from file
renameDirective = namedtuple('renameDirective', 'name filePath category newName')

# row structure of rename directive file
_RENAME_DIRECTIVE_LIST_INDEX_CURRENT_FAMILY_NAME = 0
_RENAME_DIRECTIVE_INDEX_FAMILY_FILE_PATH = 1
_RENAME_DIRECTIVE_INDEX_CATEGORY = 2
_RENAME_DIRECTIVE_LIST_INDEX_NEW_FAMILY_NAME = 3

# file name identifiers for rename directives
_RENAME_DIRECTIVE_FILE_NAME_PREFIX = 'RenameDirective'
_RENAME_DIRECTIVE_FILE_EXTENSION = '.csv'

# exceptions
_EXCEPTION_NO_RENAME_DIRECTIVE_FILES = 'Rename directive file does not exist.'
_EXCEPTION_EMPTY_RENAME_DIRECTIVE_FILES = 'Empty rename directive file!'

def _readRenameDirectives(files):
    '''
    Reads list of rename directives from file into named tuples.

    :param filePath: Fully qualified file path to rename directives file.
    :type filePath: str
    :return: List of named tuples containing rename directives.
    :rtype: [renameDirective]
    '''

    renameDirectives = []
    for file in files:
        rows = util.ReadCSVfile(file)
        # read rows in tuples ignoring the header row
        for i in range (1, len(rows)):
            if (len(rows[i]) >= 4):
                data = renameDirective(
                    rows[i][_RENAME_DIRECTIVE_LIST_INDEX_CURRENT_FAMILY_NAME], 
                    rows[i][_RENAME_DIRECTIVE_INDEX_FAMILY_FILE_PATH], 
                    rows[i][_RENAME_DIRECTIVE_INDEX_CATEGORY],
                    rows[i][_RENAME_DIRECTIVE_LIST_INDEX_NEW_FAMILY_NAME]
                )
            renameDirectives.append(data)
    return renameDirectives

def GetRenameDirectives(directoryPath):
    '''
    Retrieves file rename  directives from a given folder location.

    :param directoryPath: Fully qualified folder path to folder containing directives.
    :type directoryPath: str
    
    :return: 
        Result class instance.

        - result.status. True if rename directives where found and loaded successfully, otherwise False.
        - result.message will contain number of directives found in format:'Found rename directives: ' + number
        - result.result list of directives
        
        On exception:
        
        - result.status (bool) will be False.
        - result.message will contain an exception message.
        - result.result will be empty

    :rtype: :class:`.Result`
    '''

    returnValue = res.Result()
    # check whether csv files matching file name filter exist in directory path
    renameDirectiveFiles = util.GetFilesFromDirectoryWalkerWithFilters(
        directoryPath,
        _RENAME_DIRECTIVE_FILE_NAME_PREFIX,
        '',
        _RENAME_DIRECTIVE_FILE_EXTENSION
    )

    # check whether any files where found?
    if(len(renameDirectiveFiles) > 0):
        # attempt to re rename directives from files
        renameDirectives = _readRenameDirectives(renameDirectiveFiles)
        # check whether any rename directives where found in files
        if(len(renameDirectives) > 0):
            returnValue.UpdateSep(True, 'Found rename directives: ' + str(len(renameDirectives)))
            # attempt to rename files
            returnValue.result = renameDirectives
        else:
            returnValue.UpdateSep(False, _EXCEPTION_EMPTY_RENAME_DIRECTIVE_FILES)
    else:
        returnValue.UpdateSep(False, _EXCEPTION_NO_RENAME_DIRECTIVE_FILES)
    
    return returnValue