'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module is a pre - processing module renaming family files on a (network) drive
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module:

- Renames family files and associated catalogue files as per directives found in a given folder.
- Sets up a task list file containing all host families which have nested families requiring a rename.
- File format:

    - comma separated, file extension .task

'''

#!/usr/bin/python
# -*- coding: utf-8 -*-

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



# --------------------------
# default file path locations
# --------------------------

import sys, os

import utilModifyBVN as utilR # sets up all commonly used variables and path locations!
# import file list module
import RevitFamilyRenameFiles as renameFiles
import RevitFamilyRenameFindHostFamilies as rFamFindHostFams
import Utility as util
import utilModifyBVN as utilM
import RevitFamilyRenameFilesUtils as rFamRenameUtils
import Result as res
# -------------
# my code here:
# -------------

# output messages 
def Output(message = ''):
    print (message)

def _getNewPath(renameDirectives, currentFilePath):
    '''
    Checks wether the current file path exists in one of the rename directives. If so it will return the file path of the renamed file,
    otherwise it will return the past in file path.

    :param renameDirectives: list of tuples representing rename directives
    :type renameDirectives: [named tuple]
    :param currentFilePath: The fully qualified file path to a revit family file.
    :type currentFilePath: str
    
    :return: _description_
    :rtype: str
    '''

    for renameDirective in renameDirectives:
        # check if the rename directive got a file path, if not ignore it!
        if(len(renameDirective.filePath) > 0 and  renameDirective.filePath == currentFilePath):
            newFilePath = renameDirective.filePath[:len(renameDirective.filePath) - len(renameDirective.name + '.rfa')] + renameDirective.newName + '.rfa'
            return newFilePath
    return currentFilePath

def _writeOverAllTaskFile(resultGetHosts):
    '''
    Writes a task file to disk. Task file comprises of fully qualified file path of every family containing a family which requires renaming.

    :param resultGetHosts: _description_
    :type resultGetHosts: _type_
    
    :return: 
        Result class instance.

        - result.status. True if task file was written successfully, otherwise False.
        - result.message will contain message in format: 'Writing to: ' + taskFileName
        - result.result empty list
        
        On exception:
        
        - result.status (bool) will be False.
        - result.message will contain the exception message in format: 'Failed to write family rename task file with exception: exception'
        - result.result will be empty

    :rtype: :class:`.Result`
    '''

    result = res.Result()
    # overall task file 
    taskFileName = utilM.INPUT_DIRECTORY + '\\' + utilM.PREDEFINED_TASK_FILE_NAME_PREFIX + '_FamilyRename' + utilM.PREDEFINED_TASK_FILE_EXTENSION
    # data to be written to task file
    data = []
    # write out the actual task file
    if(resultGetHosts and len(resultGetHosts.result) > 0):
        # get rename directives just in case a host family containing fams to be renamed got renamed itself
        # and the path must therefore be adjusted
        renameDirectivesResult = rFamRenameUtils.GetRenameDirectives(rootPath_)
        
        for fam in resultGetHosts.result:
            # check whether fam got renamed
            filePath = _getNewPath (renameDirectivesResult.result, fam.filePath)
            if( filePath != fam.filePath):
                result.append_message('Changed path from: ' + fam.filePath + ' to: ' + filePath)
            else:
                result.append_message('Kept path: ' + fam.filePath)
            row = [filePath]
            data.append(row)
        
        result.append_message ('Writing to: ' + taskFileName)
        try:
            util.writeReportDataAsCSV(
                taskFileName, 
                [], 
                data
            )
            result.update_sep(True, 'Created task files.')
        except Exception as e:
            result.update_sep(False, 'Failed to write family rename task file with exception: ' + str(e))
    else:
        # write out empty task list since no host files where found
        try:
            util.writeReportDataAsCSV(
                taskFileName, 
                [], 
                data
            )
            result.update_sep(True, 'Created empty task files.')
        except Exception as e:
            result.update_sep(False, 'Failed to write family rename task file with exception: ' + str(e))
    return result

# -------------
# main:
# -------------

result_ = res.Result()
print( 'Python pre process script Rename Files ...')
# check if a folder path was past in...otherwise go with default and exit
if (len(sys.argv) == 2):
    rootPath_ = sys.argv[1]
    Output ('Renaming files as per directives saved here: ' + rootPath_)
    result_ = renameFiles.RenameFamilyFiles(rootPath_)
    Output (result_.message)
    Output('Renamed files .... status: ' + str(result_.status))
   
    # create task file for family reload action
    Output ('Creating task files for rename action of nested families ...')
    resultGetHosts_ = rFamFindHostFams.FindHostFamiliesWithNestedFamsRequiringRename(rootPath_)
    Output (resultGetHosts_.message)
    # update overall status
    result_.update(resultGetHosts_)
    
    # write task file
    resultWriteTaskFile_ = _writeOverAllTaskFile(resultGetHosts_)
    Output (resultWriteTaskFile_.message)
    # update overall status
    result_.update(resultWriteTaskFile_)
    
    # check how to exit
    if(result_.status):
        sys.exit(0)
    else:
        sys.exit(2)
else:
    rootPath_ = r'C:\Users\jchristel\Documents\DebugRevitBP\FamReload'
    Output ("Using default file path!")
    sys.exit(2)