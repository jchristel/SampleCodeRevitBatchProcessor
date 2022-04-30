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
import subprocess
import os, signal

import Utility as util

# return a list of lists of all processes running
#[
#    [HandleCount, Name, Priority, ProcessId, ThreadCount, WorkingSetSize]
#]
def GetAllRunningProcesses():
    # traverse the software list
    Data = subprocess.check_output(['wmic', 'process', 'list', 'brief'])
    a = str(Data)
    #  arrange the string
    processUnfiltered = []
    # list of all processes running... process ID is at index 3
    processFiltered = []
    try:
        processUnfiltered = a.split('\r\r\n')
        counter = 0
        columnNumber = 0
        for i in range(len(processUnfiltered)):
            if (counter == 0):
                counter =+ 1
                columnNumber = len(processUnfiltered[i].split())
            else:
                dummyList = processUnfiltered[i].split()
                if (len(dummyList) == columnNumber):
                    processFiltered.append(dummyList)
                else:
                    dif = len(dummyList) - columnNumber
                    processName = ''
                    for i in range(dif+1):
                        processName = processName + ' ' + dummyList[i+1]
                    fixedProcessData = []
                    fixedProcessData.append(dummyList[0])
                    fixedProcessData.append(processName)
                    for i in range(dif + 2, len(dummyList),1):
                        fixedProcessData.append(dummyList[i])
                    processFiltered.append(fixedProcessData)
    except IndexError as e:
        print ('Got all running processes')
    return processFiltered

# filters a provided list of processes by process name
# processNames  list of names to filter by
# processList   list of processes running ([HandleCount, Name, Priority, ProcessId, ThreadCount, WorkingSetSize])
# returnMatch   if true only matches will be returned, if false any non matches will be returned
def FilterByProcessName (processNames, processList, returnMatch = True):
    processFilteredByName = []
    for process in  processList:
        match = False
        for processName in processNames:
            if(process[1] == processName):
                match = True
                break
        if (returnMatch == True and match == True):
            processFilteredByName.append(process)
        if (returnMatch == False and match == False):
            processFilteredByName.append(process)
    return processFilteredByName

# filters a provided list of processes by process ids
# processIds    list of ids to filter by
# processList   list of processes running ([HandleCount, Name, Priority, ProcessId, ThreadCount, WorkingSetSize])
# returnMatch   if true only matches will be returned, if false any non matches will be returned
def FilterByProcessIds (processIds, processList, returnMatch = True):
    processFilteredByName = []
    for process in  processList:
        match = False
        for processId in processIds:
            if(process[3] == processId):
                match = True
                break
        if (returnMatch == True and match == True):
            processFilteredByName.append(process)
        if (returnMatch == False and match == False):
            processFilteredByName.append(process)
    return processFilteredByName

# kills all processes in list provided
# processList   list of processes running ([HandleCount, Name, Priority, ProcessId, ThreadCount, WorkingSetSize])
def KillProcesses(processList):
    status = True
    for process in  processList:
        try:
            os.kill(int(process[3]), signal.SIGTERM)
            print (str(process[1]) + ' ' + str(process[3]) + ' killed')
        except Exception as e:
            status = False
            print (e)
    return status

# writes out process data to file
def WriteOutProcessData(directoryPath, processList, fileName, fileExtension):
    status = True
    # setup file name
    filePath = directoryPath + '\\' + util.GetFileDateStamp(util.FILE_DATE_STAMP_YYYY_MM_DD_HH_MM_SEC) + fileName + fileExtension
    try:
        f = open(filePath, "w")
        for p in processList:
            f.writelines(','.join(p))
        f.close()
    except:
        status = False
    return status
