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

# this sample demonstrate how to use the solibri IFC optimizer based on documenation providedon stackoverflow.com
# https://stackoverflow.com/questions/54981866/script-for-controlling-exe-without-using-its-gui-unknown-api

commonlibraryDebugLocation_ = r'C:\temp'
# set path to common library
import sys
sys.path.append(commonlibraryDebugLocation_)

import subprocess
from System.IO import Path

# custom result class
import Result as res
import Common_Post as cp
from Common_Post import GetFiles

# default install path for solibri ifc optimizer
solibriInstallPath_ = r'C:\Program Files\Solibri\IFCOptimizer\Solibri IFC Optimizer.exe'

# this will optimize all IFC files in a give folder
# will delete the original files
# rename the new (optimized) files so file name is the same as original file
def OptimizeAllIFCFilesinFolder(directoryPath):
    returnvalue = res.Result()
    # check if ifc optimizer is installed:
    if(cp.FileExist(solibriInstallPath_)):
        returnvalue.message = 'Solibri IFC optimizer is installed.'
        ifcFiles = cp.GetFiles(directoryPath, '.ifc')
        filesToDelete = []
        filesToRename = []
        if(len(ifcFiles) > 0):
            returnvalue.AppendMessage('found ifc files: ' + str(len(ifcFiles)))
            for ifcFile in ifcFiles:
                s = subprocess.check_call([r'C:\Program Files\Solibri\IFCOptimizer\Solibri IFC Optimizer.exe', '-in=' + ifcFile, '-out=' + directoryPath, '-ifc', '-force'])
                # check what came back
                if (s == 0):
                    #all went ok:
                    returnvalue.AppendMessage('Optimized file: '+str(ifcFile))
                    filesToDelete.append(ifcFile) # full file path
                    # get the rename information
                    # contains old and new file name
                    rename = []
                    p = cp.GetFolderPathFromFile(ifcFile)
                    if(p != ''):
                        newFilePath = str(p)+'\\'+ str(Path.GetFileNameWithoutExtension(ifcFile))+'_optimized.ifc'
                        rename.append(newFilePath)
                        rename.append(ifcFile)
                        filesToRename.append(rename)
                else:
                    # something went wrong
                    returnvalue.UpdateSep(False, 'Failed to optimize file: '+ str(ifcFile))
            # clean up
            for fileToDelete in filesToDelete:
                statusDelete = cp.FileDelete(fileToDelete)
                if(statusDelete):
                    returnvalue.AppendMessage('Deleted original file: ' + str(fileToDelete))
                else:
                    returnvalue.UpdateSep(False,'Failed to delete original file: '+ str(fileToDelete))
            for fileToRename in filesToRename:
                statusRename = cp.RenameFile(fileToRename[0], fileToRename[1])
                if(statusRename):
                    returnvalue.AppendMessage('Renamed original file: ' + str(fileToRename[0]) + ' to: ' + str(fileToRename[1]))
                else:
                    returnvalue.UpdateSep(False,'Failed to rename original file: '+ str(fileToRename[0]))
        else:
            returnvalue.AppendMessage('No IFC files found in directory: '+ str(directoryPath))
    else:
        returnvalue.UpdateSep(False, 'No IFC optimizer installed at: '+ str(solibriInstallPath_))
    return returnvalue