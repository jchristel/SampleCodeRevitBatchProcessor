"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Helper functions relating to system processes.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright © 2023, Jan Christel
# All rights reserved.

# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

# - Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# - Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# - Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
#
# This software is provided by the copyright holder "as is" and any express or implied warranties, including, but not limited to, the implied warranties of merchantability and fitness for a particular purpose are disclaimed. 
# In no event shall the copyright holder be liable for any direct, indirect, incidental, special, exemplary, or consequential damages (including, but not limited to, procurement of substitute goods or services; loss of use, data, or profits; 
# or business interruption) however caused and on any theory of liability, whether in contract, strict liability, or tort (including negligence or otherwise) arising in any way out of the use of this software, even if advised of the possibility of such damage.
#
#
#
import subprocess
import os, signal

from duHast.Utilities import date_stamps as dateStamp


def get_all_running_processes():
    """
    Retrieves a list of all currently running processes.

    :return: a list in format: [[HandleCount, Name, Priority, ProcessId, ThreadCount, WorkingSetSize]]
    :rtype: list of list
    """

    # traverse the software list
    Data = subprocess.check_output(["wmic", "process", "list", "brief"])
    a = str(Data)
    #  arrange the string
    processUnfiltered = []
    # list of all processes running... process ID is at index 3
    processFiltered = []
    try:
        processUnfiltered = a.split("\r\r\n")
        counter = 0
        columnNumber = 0
        for i in range(len(processUnfiltered)):
            if counter == 0:
                counter = +1
                columnNumber = len(processUnfiltered[i].split())
            else:
                dummyList = processUnfiltered[i].split()
                if len(dummyList) == columnNumber:
                    processFiltered.append(dummyList)
                else:
                    dif = len(dummyList) - columnNumber
                    processName = ""
                    for i in range(dif + 1):
                        processName = processName + " " + dummyList[i + 1]
                    fixedProcessData = []
                    fixedProcessData.append(dummyList[0])
                    fixedProcessData.append(processName)
                    for i in range(dif + 2, len(dummyList), 1):
                        fixedProcessData.append(dummyList[i])
                    processFiltered.append(fixedProcessData)
    except IndexError as e:
        # print ('Got all running processes')
        pass
    return processFiltered


def filter_by_process_name(processNames, processList, returnMatch=True):
    """
    Filters a provided list of processes by process name

    :param processNames: List of names to filter by
    :type processNames: list of str
    :param processList: List of processes running.
    :type processList: [[HandleCount, Name, Priority, ProcessId, ThreadCount, WorkingSetSize]]
    :param returnMatch: If true only matches will be returned, if false any non matches will be returned, defaults to True
    :type returnMatch: bool, optional

    :return: List of processes
    :rtype: [[HandleCount, Name, Priority, ProcessId, ThreadCount, WorkingSetSize]]
    """

    processFilteredByName = []
    for process in processList:
        match = False
        for processName in processNames:
            if process[1] == processName:
                match = True
                break
        if returnMatch == True and match == True:
            processFilteredByName.append(process)
        if returnMatch == False and match == False:
            processFilteredByName.append(process)
    return processFilteredByName


def filter_by_process_ids(processIds, processList, returnMatch=True):
    """
    Filters a provided list of processes by process ids

    :param processIds: List of ids to filter by
    :type processIds: _type_
    :param processList: List of processes running
    :type processList: [[HandleCount, Name, Priority, ProcessId, ThreadCount, WorkingSetSize]]
    :param returnMatch: If true only matches will be returned, if false any non matches will be returned, defaults to True
    :type returnMatch: bool, optional
    :return: List of processes
    :rtype: [[HandleCount, Name, Priority, ProcessId, ThreadCount, WorkingSetSize]]
    """

    processFilteredByName = []
    for process in processList:
        match = False
        for processId in processIds:
            if process[3] == processId:
                match = True
                break
        if returnMatch == True and match == True:
            processFilteredByName.append(process)
        if returnMatch == False and match == False:
            processFilteredByName.append(process)
    return processFilteredByName


def kill_processes(processList):
    """
    Kills all processes in list provided

    :param processList: List of processes to be killed.
    :type processList: [[HandleCount, Name, Priority, ProcessId, ThreadCount, WorkingSetSize]]

    :return: True if all past in processes have been killed, otherwise False.
    :rtype: bool
    """

    status = True
    for process in processList:
        try:
            os.kill(int(process[3]), signal.SIGTERM)
            print(str(process[1]) + " " + str(process[3]) + " killed")
        except Exception as e:
            status = False
            print(e)
    return status


def write_out_process_data(directoryPath, processList, fileName, fileExtension):
    """
    Writes out process data to file

    :param directoryPath: The directory path to where the export is being saved.
    :type directoryPath: str
    :param processList: List of processes to be written to file.
    :type processList: [[HandleCount, Name, Priority, ProcessId, ThreadCount, WorkingSetSize]]
    :param fileName:  The file name under which the export is being saved (excluding file extension).
    :type fileName: str
    :param fileExtension: in format '.extension'
    :type fileExtension: str

    :return: True if the process data was written to file without an exception, otherwise False.
    :rtype: bool
    """

    status = True
    # setup file name
    filePath = (
        directoryPath
        + "\\"
        + dateStamp.get_file_date_stamp(dateStamp.FILE_DATE_STAMP_YYYY_MM_DD_HH_MM_SEC)
        + fileName
        + fileExtension
    )
    try:
        f = open(filePath, "w")
        for p in processList:
            f.writelines(",".join(p))
        f.close()
    except:
        status = False
    return status
