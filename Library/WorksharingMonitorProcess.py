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

import Utility as util
import Result as res

''' 
process name of work sharing monitor
'''

PROCESS_NAME_WSM = 'WorksharingMonitor.exe'
PROCESS_MARKER_FILENAME = 'WSMProcessList'
PROCESS_MARKER_FILEEXTENSION = '.plist'

import SystemProcess as sp

# --------------------------------- worksharing monitor specific ---------------------------------------

# get all curently running wsm processes
def GetWorkSharingMonitorProcesses():
    allProcesses = sp.GetAllRunningProcesses()
    wsmProcesses = sp.FilterByProcessName([PROCESS_NAME_WSM], allProcesses)
    return wsmProcesses

# writes out all running worksharing monitor processes data to file
# directorypath: directory where to write the file to
def WriteOutWSMDataToFile(directoryPath):
    status = res.Result()
    processList = GetWorkSharingMonitorProcesses()
    statusWriteOut = sp.WriteOutProcessData(directoryPath, processList, PROCESS_MARKER_FILENAME, PROCESS_MARKER_FILEEXTENSION)
    if(statusWriteOut):
        status.UpdateSep(True, 'Successfully wrote WSM process marker file to: ' + str(directoryPath))
    else:
        status.UpdateSep(False, 'Failed to write WSM process marker file to: ' + str(directoryPath))
    return status

# deletes all WSM marker files in a directory
def DeleteWSMDataFiles(directoryPath):
    status = True
    # get files in directory
    filesToDelete = util.GetFilesWithFilter(directoryPath, PROCESS_MARKER_FILEEXTENSION)
    if(len(filesToDelete) > 0):
        statusDelete = True
        for file in filesToDelete:
            statusDelete = statusDelete and util.FileDelete(file)
    return status

# reads in all worksharing monitor processes data from file in a given directory
# directorypath: directory where to read the data from files
def ReadWSMDataFromFile(directoryPath):
    processData = []
    files = util.GetFilesWithFilter(directoryPath, PROCESS_MARKER_FILEEXTENSION)
    if(len(files) > 0):
        for file in files:
            rows = util.ReadCSVfile(file)
            if(len(rows)>0):
                processData = processData + rows
    return processData

# returns WSM sessions filtered by provided list (not in list)
# WSMsToKeep: list of worksharing monitor sessions to keep
def GetWSMSessionsToDelete(WSMsToKeep):
    allRunningWSMProcesses = GetWorkSharingMonitorProcesses()
    if(len(WSMsToKeep) > 0):
        # get ids from list
        ids= []
        for wsmP in WSMsToKeep:
            ids.append(wsmP[3])
        filteredProcesses = sp.FilterByProcessIds(ids, WSMsToKeep, False)
        return filteredProcesses
    else:
        return allRunningWSMProcesses

# removes all wsm data marker files in a given directory
# directoryPath     directory where WSM marker file(s) are stored. These files contain wsm processes already running
#                   when batch processor started
def CleanUpWSMDataFiles(directoryPath):
    status = res.Result()
    # attempt to delete old marker files
    statusDelete = DeleteWSMDataFiles(directoryPath)
    if(statusDelete):
        status.UpdateSep(True,'Successfully deleted WSM marker file(s)!')
    else:
        status.UpdateSep(False,'Failed to delete WSM marker file(s)!')
    return status

# kills all WM processes started by Revit during the run of Revit Batch Processor
# directoryPath     directory where WSM marker file(s) are stored. These files contain wsm processes already running
#                   when batch processor started
# ignoreMarkerFiles if true all running WSM sessions will be killed 
def DieWSMDie(directoryPath, ignoreMarkerFiles = False):
    status = res.Result()
    try:
        wsmRunningPrior = []
        if(ignoreMarkerFiles == False):
            # read out wsms running before script started
            wsmRunningPrior = ReadWSMDataFromFile(directoryPath)
        wsmToDelete = GetWSMSessionsToDelete(wsmRunningPrior)
        statusKill = sp.KillProcesses(wsmToDelete)
        if(statusKill):
            status.UpdateSep(True, 'All WSM sessions where killed.')
        else:
            status.UpdateSep(False, 'Failed to kill all WSM sessions.')
    except Exception as e:
        status.UpdateSep(False,'Failedd to kill wsm sessions with exceptions: ' + str(e))
    return status