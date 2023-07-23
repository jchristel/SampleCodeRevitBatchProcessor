"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Helper functions to process Revit BatchProcessor log files.
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

# collection of tools used to process batch processor log files

# todo:
# write out current process IDs (empty text file with process id as file name)
#       script_util.GetSessionId()
# read out process ID from text file and find matching log files
# process log file:
#   - find files processed:
#            11/12/2020 18:01:40 : Processing Revit file (1 of 1) in Revit 2020 session.
#            11/12/2020 18:01:40 :
#            11/12/2020 18:01:40 : 	P:\something\FileName.rvt
#            ....
#            25/11/2020 09:37:34 : 	- Operation completed.
#   - check whether an exception occurred when processing any of the above files:
#       - file(s) not found
#           "WARNING: The following Revit Files do not exist"
#       - .net exception
#           "ERROR: An error occurred while executing the task script!"
#       - timed out occurred and revit process got killed
#           "WARNING: Timed-out"
#   - delete process id pointer file
#   - show user processing results (only when something went wrong(?))

import clr
import System
from System.IO import Path
import glob
import time
import os
import json

# custom result class from common library
from duHast.Utilities.Objects import result as res

# library from common library
from duHast.Utilities import files_io as fileIO, files_get as fileGet

#: global variable controlling debug output
debug_mode_ = False

#: Message snippets which indicate processing of a file went bad
EXCEPTION_MESSAGES = [
    "ERROR: An error occurred while executing the task script! Operation",  # revit batch p message when script is buggy
    "WARNING: Timed-out",  # revit batch p message when revit times out
    "Exception: [Exception]",  # Revit Batch P message when an exception occurs
    "\t- \tMessage: An unrecoverable error has occurred.  The program will now be terminated.",  # Revit message when it crashes out
    "Script Exception:",  # custom script message...something the script was meant to do failed
]

# output...
def output(message=""):
    if debug_mode_:
        print(message)


def delete_log_data_files(directory_path):
    """
    Deletes all log marker files in a directory.

    :param directory_path: The directory path containing marker files to be deleted.
    :type directory_path: str

    :return: True if all files where deleted successfully, otherwise False.
    :rtype: bool
    """

    status = True
    # get files in directory
    files_to_delete = fileGet.get_files_with_filter(directory_path, ".txt")
    if len(files_to_delete) > 0:
        status_delete = True
        for file in files_to_delete:
            status_delete = status_delete and fileIO.file_delete(file)
    return status


def adjust_session_id_for_file_name(id):
    """
    Removes chevrons and replace colons with underscores in session id supplied by revit batch processor so it\
        can be used in a file name.

    :param id: Session id supplied by revit batch processor.
    :type id: str

    :return: Re-formatted session id.
    :rtype: str
    """

    # remove colons
    session_id_changed = id.replace(":", "_")
    # remove chevrons
    session_id_changed = session_id_changed[1:-1]
    return session_id_changed


def adjust_session_id_file_name_back(file_name_id):
    """
    Re-introduces chevrons and replaces underscores with colons to match session Id format used in batch processor to a\
        file name using a batch processor supplied id.

    :param file_name_id: A file name containing a session id with all illegal characters replaced.
    :type file_name_id: str

    :return: A session id.
    :rtype: str
    """

    # re-instate colons
    session_id_changed = file_name_id.replace("_", ":")
    # remove chevrons
    session_id_changed = "<" + session_id_changed + ">"
    return session_id_changed


def write_session_id_marker_file(folder_path, session_id):
    """
    Writes out an empty marker file in given directory.

    - File is of type .txt
    - File name is the batch processor session_id used to identify the log file belonging to this process.

    :param folder_path: Directory of where the file will be written to.
    :type folder_path: str
    :param session_id: Session id supplied by revit batch processor.
    :type session_id: str

    :return: True if marker file was written successfully, otherwise False.
    :rtype: bool
    """

    file_name = os.path.join(folder_path, str(session_id) + ".txt")
    status = True
    try:
        f = open(file_name, "w")
        f.close()
    except:
        status = False
    return status


def get_current_session_ids(folder_path):
    """
    Returns file names of all text files in a given directory representing session Ids.

    Files will be deleted immediately after reading

    :param folder_path: Directory of where test files are located
    :type folder_path: str

    :return: A list of ids in string format.
    :rtype: [str]
    """
    ids = []
    file_list = glob.glob(folder_path + "\\*" + ".txt")
    # delete marker files
    result_delete = True
    for fd in file_list:
        if debug_mode_ == False:
            result_delete = result_delete & fileIO.file_delete(fd)
    if not result_delete:
        output("Failed to delete a marker file!")
    for f in file_list:
        ids.append(
            adjust_session_id_file_name_back(Path.GetFileNameWithoutExtension(f))
        )
    return ids


def get_log_files(list_of_session_ids):
    """
    Returns a list of fully qualified filepath to log files matching the provided session Ids.

    :param list_of_session_ids: List of session ids.
    :type list_of_session_ids: [str]

    :return: List of fully qualified file path.
    :rtype: [str]
    """

    # save the current file in epoch
    time_now = time.time()
    file_list = glob.glob(
        os.path.join(os.getenv("LOCALAPPDATA"), "BatchRvt") + "\\*" + ".log"
    )
    log_files = []
    if len(file_list) > 0:
        for l in file_list:
            # check whether file is older than 24h
            file_time = os.path.getmtime(l)
            # 24 hr are 86400 seconds
            time_out = 86400
            if debug_mode_ == True:
                time_out = 8640000
            if time_now - file_time < time_out:
                # read the first two rows of the file to get the id
                id_string = get_session_id_from_log_file(l)
                for id_to_match in list_of_session_ids:
                    if id_to_match == id_string:
                        log_files.append(l)
            else:
                output("File is to old: " + str(l))
    return log_files


def get_session_id_from_log_file(file_path):
    """
    Reads the first two rows of a log file to get the session Id used.

    :param file_path: Fully qualified file path to log file
    :type file_path: str

    :return: The session id, or if not not a log file: an empty string.
    :rtype: str
    """

    row_counter = 0
    retrieved_id = ""
    for line in open(file_path, "r"):
        # read row 2 only
        if row_counter == 1:
            data = json.loads(line)
            message = get_message_from_json(data)
            retrieved_id = get_id_from_row(message)
            break
        row_counter += 1
    return retrieved_id


def get_id_from_row(row):
    """
    Extracts the session Id from logfile row.

    sample:
    {"date":{"local":"17/12/2020","utc":"17/12/2020"},"time":{"local":"16:49:27","utc":"05:49:27"},"sessionId":"235e2180-dc33-4d61-8773-1005a59344c0","message":{"msgId":"","message":"Session ID: <2020-12-17T05:49:27.559Z>"}}

    Note: There are two session id fields in thi string!

    TODO: Do some error handling!

    :param row: A json formatted string with the session id in chevrons.
    :type row: str

    :return: The session id.
    :rtype: str
    """

    first = "<"
    last = ">"
    t = get_text_between(row, first, last)
    return first + t + last


def get_text_between(text, first, last):
    """
    Returns text in between characters

    :param text: Text to parse
    :type text: str
    :param first: String indicating start
    :type first: str
    :param last: String indicating end
    :type last: str

    :return: string in between start and end.
    :rtype: str
    """

    start = text.index(first) + len(first)
    end = text.index(last, start)
    return text[start:end]


def get_message_from_json(data):
    """
    Returns the outer message string from json formatted message field in log file.

    sample:
    {"date":{"local":"17/12/2020","utc":"17/12/2020"},"time":{"local":"16:49:27","utc":"05:49:27"},"sessionId":"235e2180-dc33-4d61-8773-1005a59344c0","message":{"msgId":"","message":"Session ID: <2020-12-17T05:49:27.559Z>"}}

    This includes leading tab characters

    :param data: json formatted row of logfile
    :type data: str

    :return: The message string
    :rtype: str
    """
    outer_message = data["message"]
    return outer_message["message"]


def process_log_file(file_path):
    """
    Process revit batch processor session log file.

    - find Revit files processed:
    - check whether an exception occurred when processing any of the above files.

    :param file_path: Fully qualified file path to json formatted log file
    :type file_path: str

    :return: returns list of arrays in format:
        [[processed Revit file name, status of processing (true or false), message]]
    :rtype: [[str]]
    """

    files_process_status = []
    # get all files processed
    try:
        files_processed = get_files_processed(file_path)
        # check whether any file not founds came back
        try:
            files_not_found = get_files_not_found(files_processed)
            try:
                # filter files_processed by files not found
                files_to_check = filter_files_not_found(
                    files_processed, files_not_found
                )
                # check for exceptions during file processing
                for file_to_check in files_to_check:
                    try:
                        status, message = get_process_status(file_to_check, file_path)
                    except Exception as e:
                        output("GetProcessStatus: " + str(e))
                    dummy = [file_to_check, status, message]
                    files_process_status.append(dummy)
                # add files not found
                for f in files_not_found:
                    dummy = [f[0], False, ["File not found"]]
                    files_process_status.append(dummy)
            except Exception as e:
                output("FileToCheck: " + str(e))
        except Exception as e:
            output("GetFilesNotFound: " + str(e))
    except Exception as e:
        output("GetFilesProcessed: " + str(e))
    return files_process_status


# filtering files not found from overall file list
#
# filesProcessed: list of arrays, first entry in array is fully qualified file path
# filesNotFound: list of fully qualified file path
# returns a list of fully qualified file path (of files marked as found)
def filter_files_not_found(files_processed, files_not_found):
    filtered_list = []
    for file_name, status in files_processed:
        flag = False
        for fn, fnStatus in files_not_found:
            if fn == file_name:
                flag = True
                break
        if not flag:
            filtered_list.append(file_name)
    return filtered_list


def get_process_status(file_to_check, log_file_path):
    """
    Reads a log file and checks whether any exception occurred when processing a specific revit file.

    :param file_to_check: Fully qualified file path of Revit file which was processed
    :type file_to_check: str
    :param log_file_path: The fully qualified batch processor session log file path.
    :type log_file_path: str

    :return: A process status and a message.

        - process status: True if no exception occurred during revit file processing, otherwise false
        - message: the exception message recorded in the log file.

    :rtype: bool, str
    """

    message = ["Found no match in log file"]
    # flag indicating whether we managed to retrieve processing data for a file
    found_match = False
    json_data = read_log_file(log_file_path)
    # get data block showing how each file was processed
    unformatted_revit_file_process_messages = get_log_blocks(
        json_data,
        "\t- Processing file (",
        ["\t- Task script operation completed.", "\t- Operation aborted."],
        True,
    )
    process_status = True
    # loop over messages in this block and check for time out, and exception messages
    for message_block in unformatted_revit_file_process_messages:
        # check if right file the file name
        # todo
        file_name = get_file_name_from_data_block(message_block)
        if file_name == file_to_check:
            output(
                "file to check: "
                + str(file_to_check + "     file found: " + file_name)
                + "    is match "
                + str(file_name == file_to_check)
            )
            found_match = True
            # flag to show whether logs show any issues
            found_problem = False
            for m in message_block:
                output(m)
                # check for exceptions
                for exception_message in EXCEPTION_MESSAGES:
                    if exception_message in m:
                        process_status = False
                        found_problem = True
                        message = [m.strip()]
                        break
            if found_problem == False:
                message = "[ok]"
                process_status = True
    # check if a match for given file was found in log data
    if found_match == False:
        process_status = False
        message = "[Failed to retrieve processing data for file.]"
    return process_status, message


def get_file_name_from_data_block(message_block):
    """
    Extracts the file name from a process message block.

    :param message_block: list of json formatted rows representing all messages received during file process
    :type message_block: [str]

    :return: The fully qualified file path of the file processed
    :rtype: str
    """

    # check if this is a cloud model
    if "CLOUD MODEL" in message_block[0]:
        # ['\t- Processing file (1 of 1): CLOUD MODEL', '\t- ', '\t- \tProject ID: GUID', '\t- \tModel ID: GUID',...]
        message_starter = "\t- \t"
        file_name = message_block[3].Trim()[len(message_starter) - 1 :]
    else:
        # ["\t- Processing file (x of y): file path"}},...]
        message_starter = "\t- Processing file (x of y): "
        file_name = message_block[0].Trim()[len(message_starter) - 1 :]
    return file_name


def get_files_processed(file_path):
    """
    Reads a batch processor logfile and extracts all file names of files processed.

    :param file_path: The fully qualified file path to log file.
    :type file_path: str

    :return: a list lists containing The fully qualified file path for each file processed and their process status. True for no exception encountered, otherwise false.
        [[filepath, status]]
    :rtype: [[str, bool]]
    """
    # log file structure:
    # start of file list (file server):
    #   {"date":{"local":"17/12/2020","utc":"17/12/2020"},"time":{"local":"16:49:28","utc":"05:49:28"},"sessionId":"235e2180-dc33-4d61-8773-1005a59344c0","message":{"msgId":"","message":"Revit Files for processing (1):"}}
    #   {"date":{"local":"17/12/2020","utc":"17/12/2020"},"time":{"local":"16:49:28","utc":"05:49:28"},"sessionId":"235e2180-dc33-4d61-8773-1005a59344c0","message":{"msgId":"","message":""}}
    #   {"date":{"local":"17/12/2020","utc":"17/12/2020"},"time":{"local":"16:49:28","utc":"05:49:28"},"sessionId":"235e2180-dc33-4d61-8773-1005a59344c0","message":{"msgId":"","message":"\tP:\\something\\FileName.rvt"}}
    #   {"date":{"local":"17/12/2020","utc":"17/12/2020"},"time":{"local":"16:49:28","utc":"05:49:28"},"sessionId":"235e2180-dc33-4d61-8773-1005a59344c0","message":{"msgId":"","message":"\tFile exists: YES"}}
    #   {"date":{"local":"17/12/2020","utc":"17/12/2020"},"time":{"local":"16:49:28","utc":"05:49:28"},"sessionId":"235e2180-dc33-4d61-8773-1005a59344c0","message":{"msgId":"","message":"\tFile size: 86.93MB"}}
    #   {"date":{"local":"17/12/2020","utc":"17/12/2020"},"time":{"local":"16:49:28","utc":"05:49:28"},"sessionId":"235e2180-dc33-4d61-8773-1005a59344c0","message":{"msgId":"","message":"\tRevit version: Autodesk Revit 2020 (Build: 20200826_1250(x64))"}}
    #   {"date":{"local":"17/12/2020","utc":"17/12/2020"},"time":{"local":"16:49:28","utc":"05:49:28"},"sessionId":"235e2180-dc33-4d61-8773-1005a59344c0","message":{"msgId":"","message":""}}
    #   {"date":{"local":"17/12/2020","utc":"17/12/2020"},"time":{"local":"16:49:28","utc":"05:49:28"},"sessionId":"235e2180-dc33-4d61-8773-1005a59344c0","message":{"msgId":"","message":"Starting batch operation..."}}
    # end of file list
    # start of file list (cloud model):
    #   {"date":{"local":"18/05/2021","utc":"18/05/2021"},"time":{"local":"19:20:00","utc":"09:20:00"},"sessionId":"e8a39f45-ca88-464f-a32f-278f0414280f","message":{"msgId":"","message":"Revit Files for processing (1):"}}
    #   {"date":{"local":"18/05/2021","utc":"18/05/2021"},"time":{"local":"19:20:00","utc":"09:20:00"},"sessionId":"e8a39f45-ca88-464f-a32f-278f0414280f","message":{"msgId":"","message":""}}
    #   {"date":{"local":"18/05/2021","utc":"18/05/2021"},"time":{"local":"19:20:00","utc":"09:20:00"},"sessionId":"e8a39f45-ca88-464f-a32f-278f0414280f","message":{"msgId":"","message":"\tCLOUD MODEL"}}
    #   {"date":{"local":"18/05/2021","utc":"18/05/2021"},"time":{"local":"19:20:00","utc":"09:20:00"},"sessionId":"e8a39f45-ca88-464f-a32f-278f0414280f","message":{"msgId":"","message":"\tProject ID: ee514b99-fac1-441a-ba98-6912c4aa4fdb"}}
    #   {"date":{"local":"18/05/2021","utc":"18/05/2021"},"time":{"local":"19:20:00","utc":"09:20:00"},"sessionId":"e8a39f45-ca88-464f-a32f-278f0414280f","message":{"msgId":"","message":"\tModel ID: c15a664d-fab8-4153-8532-b8fa04402528"}}
    #   {"date":{"local":"18/05/2021","utc":"18/05/2021"},"time":{"local":"19:20:00","utc":"09:20:00"},"sessionId":"e8a39f45-ca88-464f-a32f-278f0414280f","message":{"msgId":"","message":"\tRevit version: 2020"}}
    #   {"date":{"local":"18/05/2021","utc":"18/05/2021"},"time":{"local":"19:20:00","utc":"09:20:00"},"sessionId":"e8a39f45-ca88-464f-a32f-278f0414280f","message":{"msgId":"","message":""}}
    # end of file list
    list_of_files = []
    json_data = read_log_file(file_path)
    # get data block showing which files are to be processed
    # there should just be one ...
    log_blocks = get_log_blocks(
        json_data, "Revit Files for processing", ["Starting batch operation..."], False
    )
    if len(log_blocks) > 0:
        unformatted_revit_file_process_messages = log_blocks[0]
        # parse data block and get list of files and file exists status
        # each file block is proceeded by an empty message row
        # last entry is also an empty message block!
        for x in range(len(unformatted_revit_file_process_messages)):
            # check for start of data block
            # Output('unformatted messages '+str(unformatted_revit_file_process_messages))
            if unformatted_revit_file_process_messages[x] == "" and x + 3 <= len(
                unformatted_revit_file_process_messages
            ):
                # check whether cloud model or file server model
                if "CLOUD MODEL" in unformatted_revit_file_process_messages[x + 1]:
                    # get file data from next two rows
                    # substitute file name with file GUID, fake the status always exists
                    dummy = [
                        unformatted_revit_file_process_messages[x + 3],
                        "File exists: YES",
                    ]
                else:
                    # get file data from next two rows
                    dummy = [
                        unformatted_revit_file_process_messages[x + 1],
                        unformatted_revit_file_process_messages[x + 2],
                    ]
                list_of_files.append(get_file_data(dummy))
    return list_of_files


# method parsing two rows of json formatted data
#
# data list of 2 rows of Json formatted data
# sample of file system:
# 18/05/2021 15:57:53 : 	File exists: YES
# 18/05/2021 15:57:53 : 	File size: 199.38MB
# sample of BIM360:
# 18/05/2021 15:37:23 : 	Project ID: a valid guid
# 18/05/2021 15:37:23 : 	Model ID: a valid guid
# note: when processing BIM360 files batch processor is not checking whether the file exists upfront!
# returns list in format
# [filename, file exists status as bool]
def get_file_data(data):
    # trim white spaces from file name
    file_name = data[0].Trim()
    file_status = False
    # check whether file status contains a YES or whether this is a cloud model
    # (RBP does not check upfront whether a cloud model exists!)
    if "YES" in data[1] or "Project ID" in data[1]:
        file_status = True
    return [file_name, file_status]


def get_files_not_found(files_processed):
    """
    Filters list of all files meant to be processed and returns the ones flagged as file not found.

    :param files_processed: array of lists in format: [[filename, status as bool],[filename, status as bool],...]
    :type files_processed: [[str, bool]]

    :return: array of lists in format: [[filename, status as bool],[filename, status as bool],...]
    :rtype: [[str, bool]]
    """

    file_not_found = []
    for f in files_processed:
        if f[1] == False:
            file_not_found.append(f)
    return file_not_found


def get_log_blocks(json_data, start_marker, end_markers, multiple_blocks):
    """
    Reads json formatted data into blocks per files processed.

    Returns the message sections per row entry only.

    :param json_data: List of logfile rows in json data format
    :type json_data: [str]
    :param start_marker: String in messages indicating start of block.
    :type start_marker: str
    :param end_markers: String in messages indicating end of block.
    :type end_markers: str
    :param multiple_blocks: Flag indicating whether there are multiple data block in log file to be returned
    :type multiple_blocks: bool

    :return: List of list of str
    :rtype: [[str]]
    """

    unformatted_block_data = []
    data_block = []
    message_string = ""
    # extract rows belonging to blocks
    file_block = False
    # Output('json data: ' + str(json_data))
    for data in json_data:
        message_string = get_message_from_json(data)
        if message_string.startswith(start_marker) and file_block == False:
            file_block = True
        # flag to indicate we found a match for end of block
        match_end_block = False
        for end_marker in end_markers:
            match = False
            if message_string.startswith(end_marker) and file_block == True:
                match_end_block = True
                unformatted_block_data.append(data_block)
                data_block = []
                file_block = False
                match = True
                break
        if not multiple_blocks and match:
            break
        if file_block:
            data_block.append(message_string)
    # check for open block
    if file_block == True and match_end_block == False:
        # append this data...hopefully there is an exception message in there!!
        unformatted_block_data.append(data_block)
        output("Added open data block")
        output(data_block)
        output("")
    return unformatted_block_data


def read_log_file(file_path):
    """
    Reads batch processor log file into lists of json objects.

    Sample row:
        {'sessionId': '778e87a5-4b94-4552-9e7e-c9ed38b5caee', 'time': {'local': '09:35:45', 'utc': '22:35:45'}, 'date': {'local': '25/11/2020', 'utc': '24/11/2020'}, 'message': {'msgId': '', 'message': ''}}

    :param file_path: The fully qualified file path to log file in json format
    :type file_path: str

    :return: list of json objects
    :rtype: [json]
    """

    data = []
    with open(file_path) as f:
        for line in f:
            data.append(json.loads(line))
    return data


def process_log_files(folder_path, debug=False):
    """
    Loops over log files and checks whether any exceptions occurred during revit files processing.

    :param folder_path: Fully qualified directory path where marker files are stored.
    :type folder_path: str
    :param debug: Flag indicating whether this is running in debug mode which will output some debug messages, defaults to False
    :type debug: bool, optional

    :return:
        Result class instance.

        - Process status returned in result.status. False if an exception occurred, otherwise True.
        - result.message will contain message(s) for each revit file found in logs and whether an exception occurred during processing
        - result.result will be an empty list.

        On exception:

        - result.status (bool) will be False.
        - result.message will contain the exception message.
        - result.status will be an empty list.

    :rtype: :class:`.Result`

    """

    return_value = res.Result()
    debug_mode_ = debug
    logfile_results = []
    try:
        # get all marker files
        marker_file_ids = get_current_session_ids(folder_path)
        if debug_mode_:
            return_value.append_message(
                "Found marker file(s): {}".format(len(marker_file_ids))
            )
        if len(marker_file_ids) > 0:
            # find log files matching markers
            log_files = get_log_files(marker_file_ids)
            if debug_mode_:
                return_value.append_message(
                    "Found log file(s): {}".format(len(log_files))
                )
            if len(log_files) == len(marker_file_ids):
                data = []
                for lf in log_files:
                    # debug output
                    message = "Processing log file(s): {}".format(lf)
                    # return_value.AppendMessage('Processing log files: ' + lf)
                    try:
                        data = process_log_file(lf)
                        if len(data) > 0:
                            message = (
                                "{} [Got processed Revit file(s) data: {}]".format(
                                    message, len(data)
                                )
                            )
                        else:
                            # dummy run no files processed!
                            message = "{} [No Revit file(s) processed!]".format(message)
                    except Exception as e:
                        message = "{} [An exception occurred: {}]".format(message, e)
                    if debug_mode_:
                        return_value.append_message(message)
                    for d in data:
                        logfile_results.append(d)
                return_value.append_message("\n")
                return_value.append_message("Processed file(s) results:")
                # store results in return object
                for lf_results in logfile_results:
                    list_to_str = "\t".join(map(str, lf_results))
                    return_value.append_message(list_to_str)
                return_value.status = True
            else:
                return_value.update_sep(
                    False,
                    "Number of log files [{}] does not match required number: {}".format(
                        len(log_files), len(marker_file_ids)
                    ),
                )
        else:
            return_value.update_sep(
                False, "No marker files found in location: {}".format(folder_path)
            )
    except Exception as e:
        return_value.update_sep(False, "Terminated with Exception: {}".format(e))
    return return_value
