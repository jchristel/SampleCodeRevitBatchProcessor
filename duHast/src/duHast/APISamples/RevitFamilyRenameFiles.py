'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Helper functions to rename family files on a local or network drive.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This helper function expect a folder containing rename directive files. For format of those files refer to module RevitFamilyRenameFilesUtils

Note:

- The revit category is not used when renaming files but when renaming nested families.
- Any associated type catalogue files will also be renamed to match the new family name.
- Rename directives may not have the filePath property set if the directive is only meant to be used on loaded families.

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
import os

from duHast.APISamples import RevitFamilyRenameFilesUtils as rFamRenameUtils
from duHast.Utilities import Result as res
from duHast.Utilities import Utility as util

def _renameFiles(renameDirectives):
    '''
    Renames family files and any associated catalogue files based on rename directives.
    
    :param renameDirectives: List of tuples representing rename directives.
    :type renameDirectives: [renameDirective]

    :return: 
        Result class instance.

        - result.status. True if files where renamed successfully, otherwise False.
        - result.message will contain each rename messages in format 'old name -> new name'.
        - result.result empty list
        
        On exception:
        
        - result.status (bool) will be False.
        - result.message will contain an exception message.
        - result.result will be empty

    :rtype: :class:`.Result`
    '''

    returnValue = res.Result()
    returnValue.UpdateSep(True, 'Renaming families:')

    for renameDirective in renameDirectives:
        try:
            # check if rename directive includes a file path ( might be empty if nested families only are to be renamed)
            if(renameDirective.filePath != ''):
                # attempt to rename family file
                try:
                    # build the new file name
                    newFullName = os.path.join(os.path.dirname(renameDirective.filePath), renameDirective.newName + '.rfa')
                    if(util.FileExist(renameDirective.filePath)):
                        os.rename(renameDirective.filePath, newFullName)
                        returnValue.AppendMessage(renameDirective.name + ' -> ' + renameDirective.newName)
                    else:
                        returnValue.UpdateSep(False, 'File not found: '+ renameDirective.name)
                except Exception as e:
                    returnValue.UpdateSep(False, 'Failed to rename file: ' + renameDirective.name + ' with exception: ' + str(e))

                # take care of catalogue files as well
                oldFullName = renameDirective.filePath[:-4] + '.txt'
                newFullName = os.path.join(os.path.dirname(renameDirective.filePath), renameDirective.newName + '.txt')
                oldname = renameDirective.name + '.txt'
                newname = renameDirective.newName + '.txt'
                try:
                    if(util.FileExist(oldFullName)):
                        os.rename(oldFullName, newFullName)
                        returnValue.AppendMessage(oldname + ' -> ' + newname)
                    else:
                        returnValue.UpdateSep(True, 'No catalogue file found: ' + oldname) # nothing gone wrong here...just no catalogue file present
                except Exception as e:
                    returnValue.UpdateSep(False, 'Failed to rename file: ' + oldFullName + ' with exception: ' + str(e))
            else:
                returnValue.UpdateSep(True, 'No file path found: ' + renameDirective.name) # nothing gone wrong here...just not required to rename a file
        except Exception as e:
            returnValue.UpdateSep(False, 'Failed to rename files with exception: ' + str(e))
    return returnValue

def RenameFamilyFiles(directoryPath):
    '''
    Entry point for this module. Will read rename directives files in given directory and attempt to rename
    family files and any associated catalogue files accordingly.

    Note: Rename directive may not include a file path in situations where a loaded family only is to be renamed. This \
        will still return True in such a case.

    :param directoryPath: Fully qualified directory path to where rename directive files are located.
    :type directoryPath: str
    :return: 
        Result class instance.

        - result.status. True if files where renamed successfully, otherwise False.
        - result.message will contain each rename messages in format 'old name -> new name'.
        - result.result empty list
        
        On exception:
        
        - result.status (bool) will be False.
        - result.message will contain an exception message.
        - result.result will be empty

    :rtype: :class:`.Result`
    '''

    returnValue = res.Result()
    # get directives from folder
    renameDirectivesResult = rFamRenameUtils.GetRenameDirectives(directoryPath)
    # check if anything came back
    if(renameDirectivesResult.status):
        renameDirectives = renameDirectivesResult.result
        # rename files as per directives
        returnValue = _renameFiles(renameDirectives)
    else:
        returnValue = renameDirectivesResult

    return returnValue