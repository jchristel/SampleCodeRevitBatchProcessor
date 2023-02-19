'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Reload using advanced tools collection.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module provides utility functions to read and write reload task lists for the Revit Batch Processor.

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

from collections import namedtuple

from duHast.Utilities.timer import Timer
from duHast.Utilities import Result as res
from duHast.Utilities import Utility as util
from duHast.APISamples import RevitFamilyBaseDataUtils as rFamBaseDataUtils

# tuples containing base family data and changed family data read from files
changedFamily = namedtuple('changedFamily', 'name category filePath')
#baseFamily = namedtuple('baseFamily', 'name category rootPath filePath')

# row structure of family change data file
_CHANGE_LIST_INDEX_FAMILY_NAME = 0
_CHANGE_LIST_INDEX_FAMILY_FILE_PATH = 1
_CHANGE_LIST_INDEX_CATEGORY = 2

_TASK_COUNTER_FILE_PREFIX = 'TaskOutput'


def WriteReloadListToFile(reloadFamilies, directoryPath, counter = 0):
    '''
    Writes task list file to disk. File contains single column of fully qualified file path.

    :param reloadFamilies: List of tuples representing families requiring their nested families to be re-loaded.
    :type reloadFamilies: [baseFamily]
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

def DeleteOldTaskLists(directoryPath):
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

def WriteOutEmptyTaskList(directoryPath, counter = 0):
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

def _RemoveRFAFromFileName(familyName):
    '''
    Removes any .rfa file extensions from the family name. (not sure why these are sometimes present)

    :param familyName: the family name
    :type familyName: str
    :return: the family name with out .rfa (if present in the first place.)
    :rtype: str
    '''

    if(familyName.lower().endswith('.rfa')):
        familyName = familyName[:-len('.rfa')]
    return familyName

def ReadChangeList(filePath):
    '''
    Reads list of changed families from file into named tuples.

    :param filePath: Fully qualified file path to change list  file.
    :type filePath: str
    :raises Exception: "Changed families list files does not exist."
    :raises Exception: "Empty families list file!"
    :return: list of named tuples
    :rtype: [changedFamily]
    '''

    rows = []
    if(util.FileExist(filePath)):
        rows = util.ReadCSVfile(filePath)
    else:
        raise Exception("Changed families list files does not exist.")
    if(len(rows) > 0):
        pass
    else:
        raise Exception("Empty families list file!")
    
    returnValue = []
    # skip header row
    for i in range(1, len(rows)):
        #TODO: do i need any .rfa from end of family name?
        famName = _RemoveRFAFromFileName(rows[i][_CHANGE_LIST_INDEX_FAMILY_NAME])
        data = changedFamily(
            famName, 
            rows[i][_CHANGE_LIST_INDEX_CATEGORY], 
            rows[i][_CHANGE_LIST_INDEX_FAMILY_FILE_PATH]
            )
        returnValue.append(data)
    return returnValue