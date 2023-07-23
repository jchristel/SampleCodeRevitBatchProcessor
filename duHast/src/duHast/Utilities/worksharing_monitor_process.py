"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Helper functions relating to Revit worksharing monitor process. 
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

from duHast.Utilities import (
    files_csv as filesCSV,
    files_get as fileGet,
    files_io as fileIO,
)
from duHast.Utilities.Objects import result as res
from duHast.Utilities import system_process as sp


""" 
Process name of work sharing monitor
"""

PROCESS_NAME_WSM = "WorksharingMonitor.exe"
PROCESS_MARKER_FILENAME = "WSMProcessList"
PROCESS_MARKER_FILE_EXTENSION = ".plist"


# --------------------------------- worksharing monitor specific ---------------------------------------


def get_work_sharing_monitor_processes():
    """
    Get all currently running worksharing monitor processes

    :return: _description_
    :rtype: [[HandleCount, Name, Priority, ProcessId, ThreadCount, WorkingSetSize]]
    """
    all_processes = sp.get_all_running_processes()
    wsm_processes = sp.filter_by_process_name([PROCESS_NAME_WSM], all_processes)
    return wsm_processes


def write_out_wsm_data_to_file(directory_path):
    """
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
    """

    status = res.Result()
    process_list = get_work_sharing_monitor_processes()
    status_write_out = sp.write_out_process_data(
        directory_path,
        process_list,
        PROCESS_MARKER_FILENAME,
        PROCESS_MARKER_FILE_EXTENSION,
    )
    if status_write_out:
        status.update_sep(
            True,
            "Successfully wrote WSM process marker file to: " + str(directory_path),
        )
    else:
        status.update_sep(
            False, "Failed to write WSM process marker file to: " + str(directory_path)
        )
    return status


def delete_wsm_data_files(directory_path):
    """
    Deletes all WSM marker files in a directory.

    WSM marker files got a specific file extension: Check: PROCESS_MARKER_FILE_EXTENSION

    :param directory_path: The directory path containing marker files to be deleted.
    :type directory_path: str

    :return: True if all files where deleted successfully, otherwise False.
    :rtype: bool
    """

    status = True
    # get files in directory
    files_to_delete = fileGet.get_files_with_filter(
        directory_path, PROCESS_MARKER_FILE_EXTENSION
    )
    if len(files_to_delete) > 0:
        status_delete = True
        for file in files_to_delete:
            status_delete = status_delete and fileIO.file_delete(file)
    return status


def read_wsm_data_from_file(directory_path):
    """
    Reads all worksharing monitor processes data from marker file(s) in a given directory

    WSM marker files got a specific file extension: Check: PROCESS_MARKER_FILE_EXTENSION

    :param directory_path: The directory path to where marker files are to be read from.
    :type directory_path: str

    :return: list of list of str
    :rtype: [[HandleCount, Name, Priority, ProcessId, ThreadCount, WorkingSetSize]]
    """

    process_data = []
    files = fileGet.get_files_with_filter(directory_path, PROCESS_MARKER_FILE_EXTENSION)
    if len(files) > 0:
        for file in files:
            rows = filesCSV.read_csv_file(file)
            if len(rows) > 0:
                process_data = process_data + rows
    return process_data


def get_wsm_sessions_to_delete(ws_ms_to_keep):
    """
    Returns Worksharing monitor process sessions filtered by provided list (not in list)

    :param ws_ms_to_keep: List of worksharing monitor sessions to filter by. WSM included in this list will be removed from past in list.
    :type ws_ms_to_keep: List of list of str in format: [[HandleCount, Name, Priority, ProcessId, ThreadCount, WorkingSetSize]]

    :return: Filtered list of list of str of worksharing monitor sessions
    :rtype: [[HandleCount, Name, Priority, ProcessId, ThreadCount, WorkingSetSize]]
    """

    all_running_wsm_processes = get_work_sharing_monitor_processes()
    if len(ws_ms_to_keep) > 0:
        # get ids from list
        ids = []
        for wsm_p in ws_ms_to_keep:
            ids.append(wsm_p[3])
        filtered_processes = sp.filter_by_process_ids(ids, ws_ms_to_keep, False)
        return filtered_processes
    else:
        return all_running_wsm_processes


def clean_up_wsm_data_files(directory_path):
    """
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
    """

    status = res.Result()
    # attempt to delete old marker files
    status_delete = delete_wsm_data_files(directory_path)
    if status_delete:
        status.update_sep(True, "Successfully deleted WSM marker file(s)!")
    else:
        status.update_sep(False, "Failed to delete WSM marker file(s)!")
    return status


def die_wsm_die(directory_path, ignore_marker_files=False):
    """
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
    """

    status = res.Result()
    try:
        wsm_running_prior = []
        if ignore_marker_files == False:
            # read out worksharing monitor sessions running before script started
            wsm_running_prior = read_wsm_data_from_file(directory_path)
        wsm_to_delete = get_wsm_sessions_to_delete(wsm_running_prior)
        status_kill = sp.kill_processes(wsm_to_delete)
        if status_kill:
            status.update_sep(True, "All WSM sessions where killed.")
        else:
            status.update_sep(False, "Failed to kill all WSM sessions.")
    except Exception as e:
        status.update_sep(
            False, "Failed to kill wsm sessions with exceptions: " + str(e)
        )
    return status
