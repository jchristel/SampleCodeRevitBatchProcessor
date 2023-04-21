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

from duHast.Utilities import FilesCSV as fileCSV, FilesGet as fileGet, FilesIO as util, FilesTab as fileTab

# tuples containing base family data and changed family data read from files
changed_family = namedtuple('changed_family', 'name category filePath')
#baseFamily = namedtuple('baseFamily', 'name category rootPath filePath')

# row structure of family change data file
CHANGE_LIST_INDEX_FAMILY_NAME = 0
CHANGE_LIST_INDEX_FAMILY_FILE_PATH = 1
CHANGE_LIST_INDEX_CATEGORY = 2

TASK_COUNTER_FILE_PREFIX = 'TaskOutput'


def write_reload_list_to_file(reload_families, directory_path, counter = 0):
    '''
    Writes task list file to disk. File contains single column of fully qualified file path.

    :param reload_families: List of tuples representing families requiring their nested families to be re-loaded.
    :type reload_families: [baseFamily]
    :param directory_path: Fully qualified directory path to which the task files will be written.
    :type directory_path: str
    :param counter: Task file name suffix, defaults to 0
    :type counter: int, optional
    :return: True if file was written successfully, otherwise False.
    :rtype: bool
    '''

    # write out file list without header
    header = []
    # data to be written to file
    overall_data = []
    file_name = directory_path + '\\' + TASK_COUNTER_FILE_PREFIX + str(counter)+ ".txt"
    # loop over families to get file path
    for r in reload_families:
        # row data
        data = []
        data.append(r.filePath)
        overall_data.append(data)
    try:
        # write data
        fileTab.write_report_data(file_name, header, overall_data, writeType = 'w')
        return True
    except Exception:
        return False

def delete_old_task_lists(directory_path):
    '''
    Deletes all overall task files in given directory.

    :param directory_path: Fully qualified directory path containing the task files to be deleted.
    :type directory_path: str
    :return: True if all files got deleted successfully, otherwise False.
    :rtype: bool
    '''

    flag = True
    # find all files in folder starting with and delete them
    files = fileGet.get_files(directory_path, '.txt')
    if (len(files) > 0):
        for f in files:
            if (util.get_file_name_without_ext(f).startswith(TASK_COUNTER_FILE_PREFIX)):
                flag = flag & util.file_delete(f)
    return flag

def write_out_empty_task_list(directory_path, counter = 0):
    '''
    Writes out an empty task list in case nothing is to be reloaded.

    :param directory_path: Fully qualified directory path to which the task files will be written.
    :type directory_path: str
    :param counter: Task file name suffix, defaults to 0
    :type counter: int, optional
    :return: True if file was written successfully, otherwise False.
    :rtype: bool
    '''

    file_name = directory_path + '\\' + 'TaskOutput' + str(counter)+ ".txt"
    # write out file list without header
    header = []
    # write out empty data
    overall_data = []
    try:
        # write data
        fileTab.write_report_data(file_name, header, overall_data, writeType = 'w')
        return True
    except Exception:
        return False

def _remove_rfa_from_file_name(family_name):
    '''
    Removes any .rfa file extensions from the family name. (not sure why these are sometimes present)

    :param family_name: the family name
    :type family_name: str
    :return: the family name with out .rfa (if present in the first place.)
    :rtype: str
    '''

    if(family_name.lower().endswith('.rfa')):
        family_name = family_name[:-len('.rfa')]
    return family_name

def read_change_list(file_path):
    '''
    Reads list of changed families from file into named tuples.

    :param file_path: Fully qualified file path to change list  file.
    :type file_path: str
    :raises Exception: "Changed families list files does not exist."
    :raises Exception: "Empty families list file!"
    :return: list of named tuples
    :rtype: [changed_family]
    '''

    rows = []
    if(util.file_exist(file_path)):
        rows = fileCSV.read_csv_file(file_path)
    else:
        raise Exception("Changed families list files does not exist.")
    if(len(rows) > 0):
        pass
    else:
        raise Exception("Empty families list file!")
    
    return_value = []
    # skip header row
    for i in range(1, len(rows)):
        #TODO: do i need any .rfa from end of family name?
        fam_name = _remove_rfa_from_file_name(rows[i][CHANGE_LIST_INDEX_FAMILY_NAME])
        data = changed_family(
            fam_name, 
            rows[i][CHANGE_LIST_INDEX_CATEGORY], 
            rows[i][CHANGE_LIST_INDEX_FAMILY_FILE_PATH]
            )
        return_value.append(data)
    return return_value