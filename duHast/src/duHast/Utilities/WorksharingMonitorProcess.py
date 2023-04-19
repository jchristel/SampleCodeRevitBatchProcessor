'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Helper functions relating to Revit worksharing monitor process. 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''
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

from duHast.Utilities import FilesCSV as filesCSV, FilesGet as fileGet, FilesIO as util
from duHast.Utilities import Result as res
from duHast.Utilities import SystemProcess as sp


''' 
Process name of work sharing monitor
'''

PROCESS_NAME_WSM = 'WorksharingMonitor.exe'
PROCESS_MARKER_FILENAME = 'WSMProcessList'
PROCESS_MARKER_FILE_EXTENSION = '.plist'


# --------------------------------- worksharing monitor specific ---------------------------------------

def get_work_sharing_monitor_processes():
    '''
    Get all currently running worksharing monitor processes

    :return: _description_
    :rtype: [[HandleCount, Name, Priority, ProcessId, ThreadCount, WorkingSetSize]]
    '''
    all_processes = sp.get_all_running_processes()
    wsm_processes = sp.filter_by_process_name([PROCESS_NAME_WSM], all_processes)
    return wsm_processes

def write_out_wsm_data_to_file(directory_path):
    '''
    Writes out all running worksharing monitor processes data to file

    :param directory_path: The directory path to where the marker file is to be saved.
    :type directory_path: str
    
    :return:  
        Result class instance.
        
        - Export status returned in result.status. False if an exception occurred, otherwise True.
        - result.message will contain the fully qualified file path of the exported file.
        
        On exception:
        
        - result.status (bool) will be False.
        - result.message will contain the exception message.
    
    :rtype: :class:`.Result`
    '''

    status = res.Result()
    process_list = get_work_sharing_monitor_processes()
    status_write_out = sp.write_out_process_data(directory_path, process_list, PROCESS_MARKER_FILENAME, PROCESS_MARKER_FILE_EXTENSION)
    if(status_write_out):
        status.update_sep(True, 'Successfully wrote WSM process marker file to: ' + str(directory_path))
    else:
        status.update_sep(False, 'Failed to write WSM process marker file to: ' + str(directory_path))
    return status

def delete_wsm_data_files(directory_path):
    '''
    Deletes all WSM marker files in a directory.

    WSM marker files got a specific file extension: Check: PROCESS_MARKER_FILE_EXTENSION 

    :param directory_path: The directory path containing marker files to be deleted.
    :type directory_path: str

    :return: True if all files where deleted successfully, otherwise False.
    :rtype: bool
    '''

    status = True
    # get files in directory
    files_to_delete = fileGet.get_files_with_filter(directory_path, PROCESS_MARKER_FILE_EXTENSION)
    if(len(files_to_delete) > 0):
        status_delete = True
        for file in files_to_delete:
            status_delete = status_delete and util.file_delete(file)
    return status

def read_wsm_data_from_file(directory_path):
    '''
    Reads all worksharing monitor processes data from marker file(s) in a given directory
    
    WSM marker files got a specific file extension: Check: PROCESS_MARKER_FILE_EXTENSION 

    :param directory_path: The directory path to where marker files are to be read from.
    :type directory_path: str
    
    :return: list of list of str
    :rtype: [[HandleCount, Name, Priority, ProcessId, ThreadCount, WorkingSetSize]]
    '''
    
    process_data = []
    files = fileGet.get_files_with_filter(directory_path, PROCESS_MARKER_FILE_EXTENSION)
    if(len(files) > 0):
        for file in files:
            rows = filesCSV.read_csv_file(file)
            if(len(rows)>0):
                process_data = process_data + rows
    return process_data

def get_wsm_sessions_to_delete(ws_ms_to_keep):
    '''
    Returns Worksharing monitor process sessions filtered by provided list (not in list)

    :param ws_ms_to_keep: List of worksharing monitor sessions to filter by. WSM included in this list will be removed from past in list.
    :type ws_ms_to_keep: List of list of str in format: [[HandleCount, Name, Priority, ProcessId, ThreadCount, WorkingSetSize]]
    
    :return: Filtered list of list of str of worksharing monitor sessions 
    :rtype: [[HandleCount, Name, Priority, ProcessId, ThreadCount, WorkingSetSize]]
    '''

    all_running_wsm_processes = get_work_sharing_monitor_processes()
    if(len(ws_ms_to_keep) > 0):
        # get ids from list
        ids= []
        for wsm_p in ws_ms_to_keep:
            ids.append(wsm_p[3])
        filtered_processes = sp.filter_by_process_ids(ids, ws_ms_to_keep, False)
        return filtered_processes
    else:
        return all_running_wsm_processes

def clean_up_wsm_data_files(directory_path):
    '''
    Removes all wsm data marker files in a given directory.

    WSM marker files got a specific file extension: Check: PROCESS_MARKER_FILE_EXTENSION.

    :param directory_path: The directory path containing the marker files to be deleted.
    :type directory_path: str
    
    :return:  
        Result class instance.
        
        - Delete status returned in result.status. False if an exception occurred, otherwise True.
        - result.message will confirm successful deletion of all files.
        
        On exception:
        
        - result.status (bool) will be False.
        - result.message will contain the exception message.

    :rtype: :class:`.Result`
    '''

    status = res.Result()
    # attempt to delete old marker files
    status_delete = delete_wsm_data_files(directory_path)
    if(status_delete):
        status.update_sep(True,'Successfully deleted WSM marker file(s)!')
    else:
        status.update_sep(False,'Failed to delete WSM marker file(s)!')
    return status

def die_wsm_die(directory_path, ignore_marker_files = False):
    '''
    Kills all worksharing monitor processes currently active.

    Unless marker files are used. In that case only worksharing monitor sessions identified in marker files will be killed.

    :param directory_path: The directory path to where marker files are to be read from.
    :type directory_path: str
    :param ignore_marker_files: True no marker file data will be read and all WSM sessions running will be killed., defaults to False
    :type ignore_marker_files: bool, optional
    
    :return:  
        Result class instance.
        
        - Kill status returned in result.status. False if an exception occurred, otherwise True.
        - result.message will confirm successful killing of all WSM processes.
        
        On exception:
        
        - result.status (bool) will be False.
        - result.message will contain the exception message.
    
    :rtype: :class:`.Result`
    '''

    status = res.Result()
    try:
        wsm_running_prior = []
        if(ignore_marker_files == False):
            # read out worksharing monitor sessions running before script started
            wsm_running_prior = read_wsm_data_from_file(directory_path)
        wsm_to_delete = get_wsm_sessions_to_delete(wsm_running_prior)
        status_kill = sp.kill_processes(wsm_to_delete)
        if(status_kill):
            status.update_sep(True, 'All WSM sessions where killed.')
        else:
            status.update_sep(False, 'Failed to kill all WSM sessions.')
    except Exception as e:
        status.update_sep(False,'Failed to kill wsm sessions with exceptions: ' + str(e))
    return status