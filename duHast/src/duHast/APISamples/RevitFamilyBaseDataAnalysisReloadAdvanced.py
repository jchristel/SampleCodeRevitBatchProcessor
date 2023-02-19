'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Family Base data analysis module containing functions to build a reload tree.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- read change list:
-   text file (tab separated) with columns:familyName	familyFilePath	categoryName
- read overall family base data list
- get direct parents of change list families
- get next level parents of direct parents

- loop direct parent list until empty:
-   - remove any direct parents which also exist in next level parents
-   - write direct parents to file
-   - set next level parents as direct parents
-   - find all direct parents of changed families in base data list

- those reload lists will then be separated into work chunks by file list writer...

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


from duHast.Utilities.timer import Timer
from duHast.Utilities import Result as res
from duHast.Utilities import Utility as util
from duHast.APISamples import RevitFamilyBaseDataUtils as rFamBaseDataUtils
from duHast.APISamples import RevitFamilyReloadAdvancedUtils as rFamReloadAdvUtils

_TASK_COUNTER_FILE_PREFIX = 'TaskOutput'


def _WriteReloadListToFile(reloadFamilies, directoryPath, counter = 0):
    '''
    Writes task list file to disk. File contains single column of fully qualified file path.

    :param reloadFamilies: List of tuples representing families requiring their nested families to be re-loaded.
    :type reloadFamilies: [rootFamily]
    :param directoryPath: Fully qualified directory path to which the task files will be written.
    :type directoryPath: str
    :param counter: Task file name suffix, defaults to 0
    :type counter: int, optional
    
    :return: True if file was written successfully, otherwise False.
    :rtype: bool
    '''

    # write out file list without header
    header = []
    # data to be written to file
    overallData = []
    fileName = directoryPath + '\\' + _TASK_COUNTER_FILE_PREFIX + str(counter)+ ".txt"
    # loop over families to get file path
    for r in reloadFamilies:
        # row data
        data = []
        data.append(r.filePath)
        overallData.append(data)
    try:
        # write data
        util.writeReportData(fileName, header, overallData, writeType = 'w')
        return True
    except Exception:
        return False

def _DeleteOldTaskLists(directoryPath):
    '''
    Deletes all overall task files in given directory.

    :param directoryPath: Fully qualified directory path containing the task files to be deleted.
    :type directoryPath: str
    :return: True if all files got deleted successfully, otherwise False.
    :rtype: bool
    '''

    flag = True
    # find all files in folder starting with and delete them
    files = util.GetFiles(directoryPath, '.txt')
    if (len(files) > 0):
        for f in files:
            if (util.GetFileNameWithoutExt(f).startswith(_TASK_COUNTER_FILE_PREFIX)):
                flag = flag & util.FileDelete(f)
    return flag

def _WriteOutEmptyTaskList(directoryPath, counter = 0):
    '''
    Writes out an empty task list in case nothing is to be reloaded.

    :param directoryPath: Fully qualified directory path to which the task files will be written.
    :type directoryPath: str
    :param counter: Task file name suffix, defaults to 0
    :type counter: int, optional
    
    :return: True if file was written successfully, otherwise False.
    :rtype: bool
    '''

    fileName = directoryPath + '\\' + 'TaskOutput' + str(counter)+ ".txt"
    # write out file list without header
    header = []
    # write out empty data
    overallData = []
    try:
        # write data
        util.writeReportData(fileName, header, overallData, writeType = 'w')
        return True
    except Exception:
        return False

def _removeDuplicates(listOne, listTwo):
    '''
    Removes any item from list one which is present in list two.

    :param listOne: List of tuples containing root family data.
    :type listOne: [rFamBaseDataUtils.rootFamily]
    :param listTwo: List of tuples containing root family data.
    :type listTwo: [rFamBaseDataUtils.rootFamily]

    :return: _description_
    :rtype: _type_
    '''

    newList = []
    duplicatesList = []
    for lOneItem in listOne:
        if lOneItem not in listTwo:
            newList.append(lOneItem)
        else:
            duplicatesList.append(lOneItem)
    return newList, duplicatesList

def _getHosts(currentFamilies, overallFamilyBaseNestedData, overallFamilyBaseRootData):
    '''
    Returns the direct ( one level up) host families of the current families.

    :param currentFamilies: A list of current families represented as tuples (tuple need to have properties 'name' and 'category').
    :type currentFamilies: [rFamBaseDataUtils.rootFamily] or [rFamBaseDataUtils.nestedFamily] or [rFamReloadAdvUtils.changedFamily]
    :param overallFamilyBaseNestedData: List of tuples containing nested family data.
    :type overallFamilyBaseNestedData: [rFamBaseDataUtils.nestedFamily]
    :param overallFamilyBaseRootData: List of tuples containing root family data.
    :type overallFamilyBaseRootData: [rFamBaseDataUtils.rootFamily]
    
    :return: A list of root families.
    :rtype: [rFamBaseDataUtils.rootFamily]
    '''

    # get current change list host files
    directHosts = rFamBaseDataUtils.FindRootFamsFromHosts(
        rFamBaseDataUtils.FindAllDirectHostFamilies(currentFamilies, overallFamilyBaseNestedData), 
        overallFamilyBaseRootData)
    return directHosts

def BuildWorkLists(changeListFilePath, familyBaseDataReportFilePath, loadListsOutputDirectoryPath):
    '''
    Processes a file change list and a family base data report. From both reports it builds a lists for reloading families bottom up in their nesting hierarchy.

    :param changeListFilePath: Fully qualified file path to family change list report file. 
    :type changeListFilePath: str
    :param familyBaseDataReportFilePath: Fully qualified file path to family base data report file. 
    :type familyBaseDataReportFilePath: str
    :param loadListsOutputDirectoryPath: Fully qualified directory path to which the task output files will be written
    :type loadListsOutputDirectoryPath: str
    :raises Exception: "Infinite loop." Will be raised if more then 20 task output files are written (representing a family nesting level of 20 deep...unlikely)
    '''

    # set up a timer
    tProcess = Timer()
    tProcess.start()

    returnValue = res.Result()
    changeList = rFamReloadAdvUtils.ReadChangeList(changeListFilePath)
    returnValue.AppendMessage(tProcess.stop() + ' Change list of length [' +str(len(changeList)) +'] loaded.')

    tProcess.start()
    # read overall family base data from file 
    overallFamilyBaseRootData, overallFamilyBaseNestedData = rFamBaseDataUtils.ReadOverallFamilyDataList(familyBaseDataReportFilePath)
    returnValue.AppendMessage(tProcess.stop() + ' Nested base data list of length [' + str(len(overallFamilyBaseNestedData)) + '] loaded.')
    
    if(len(changeList) > 0):
        # list containing the hosts of the host families
        taskNextLevel = []
        # safety switch in case of infinite loop
        taskListCounter = 0

        tProcess.start()
        taskCurrentLevel = _getHosts(
            changeList, 
            overallFamilyBaseNestedData, 
            overallFamilyBaseRootData
            )
        returnValue.AppendMessage(tProcess.stop() + ' Direct hosts [' + str(len(taskCurrentLevel)) + '] found.')
        
        tProcess.start()
        taskNextLevel = _getHosts(
            taskCurrentLevel, 
            overallFamilyBaseNestedData, 
            overallFamilyBaseRootData
            )
        returnValue.AppendMessage(tProcess.stop() + ' Next level hosts [' + str(len(taskNextLevel)) + '] found.')

        # loop until no more entries in current level tasks
        while (len(taskCurrentLevel) > 0 ):
            
            # remove next level hosts from direct hosts list to avoid overlap in reload process
            cleanedCurrentTasks, overLapTasks = _removeDuplicates(taskCurrentLevel, taskNextLevel)
            
            # write out cleaned up list:
            if(len(cleanedCurrentTasks) > 0):
                tProcess.start()
                resultWriteToDisk = _WriteReloadListToFile(
                    cleanedCurrentTasks, 
                    loadListsOutputDirectoryPath, 
                    taskListCounter
                    )
                returnValue.UpdateSep(resultWriteToDisk, tProcess.stop() +  ' Wrote task list to file with status: ' + str(resultWriteToDisk))
            else:
                # write out an empty task list!
                emptyTaskListFlag = _WriteOutEmptyTaskList(loadListsOutputDirectoryPath, taskListCounter)
                returnValue.UpdateSep(emptyTaskListFlag, 'Wrote empty task list at counter ['+ str(taskListCounter))

            # swap lists to get to next level of loading
            taskCurrentLevel = list(taskNextLevel)
            returnValue.AppendMessage('Swapping next level hosts to direct hosts [' + str(len(taskCurrentLevel)) + ']')

            tProcess.start()
            # get next level host families (task)
            taskNextLevel = _getHosts(
                taskCurrentLevel, 
                overallFamilyBaseNestedData, 
                overallFamilyBaseRootData
                )
            returnValue.AppendMessage(tProcess.stop() + ' Next level hosts [' + str(len(taskNextLevel)) + '] found.')
            
            # increase task list counter to be used in file name
            taskListCounter = taskListCounter + 1
            if(taskListCounter > 20):
                # trigger fail save
                returnValue.UpdateSep(False, ' Exceeded maximum number of task list files! (20)')
                raise Exception("Infinite loop.")
    else:
        returnValue.UpdateSep(True, 'Empty change list found. No families require processing.')
    return returnValue