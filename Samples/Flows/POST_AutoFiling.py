'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Automated filing.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This flow demonstrates how to file incoming models into as given folder structure and keep a record of date and revision of files received.

The given folder structure includes a NavisWorks federated model folder where all .nwc files are stored. In order to replace existing files in that location, incoming files are stripped of their revision information contained within the file name.


This script can be used when: 

- multiple sessions of Revit Batch Processor are to be run in parallel using a batch script set up
- single session of Revit Batch Processor is used


- this can either be:

    - started from a batch file after Revit Batch Processor is finished
    - started as a post - process script in the Revit Batch Processor UI

'''

#!/usr/bin/python
# -*- coding: utf-8 -*-
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

# this sample shows how to do some automated filing of (incoming) Revit and NWC files after a process has run
# steps included are:
# copy and rename, i.e. remove revision data, NWC files into given locations to assist in updating federated NavisWorks models
# move Revit, NWC, IFC files into an automatically created dated folder in a given INCOMING location [INCOMING location can be nominated per file to allow for separate locations per consultant for instance]
# updated an incoming files register with date and revision of files received. (Date is current date, revision will need to be included in the file name). The register is a CSV text file which in turn can be linked into MS Excel

# ---------------------------------
# default path locations
# ---------------------------------
# path to library modules
COMMON_LIBRARY_LOCATION = r'C:\temp'
# path to directory containing this script (in case there are any other modules to be loaded from here)
SCRIPT_LOCATION = r'C:\temp'

import clr
import System

# set path to library and this script
import sys
sys.path += [COMMON_LIBRARY_LOCATION, SCRIPT_LOCATION]

# import libraries
from duHast.Utilities import FilesGet as fileGet
from duHast.Utilities import FilesIO as fileIO
from duHast.Utilities import DirectoryIO as dirIO
from duHast.Utilities import DateStamps as dateStamp
from duHast.Utilities import FilesCSV as fileCSV

import os.path
from os import path
import shutil
from System.IO import Path

# to read csv files
import csv
clr.AddReference('System.Core')
clr.ImportExtensions(System.Linq)

# flag whether this runs in debug or not
DEBUG = False

# Add batch processor scripting references
if not DEBUG:
    import script_util

# -------------
# my code here:
# -------------

# output messages either to batch processor (debug = False) or console (debug = True)
def output(message = ''):
    '''
    Output messages either to batch processor (debug = False) or console (debug = True)

    :param message: the message, defaults to ''
    :type message: str, optional
    '''

    if not DEBUG:
        script_util.Output(str(message))
    else:
        print (message)

def _get_nwc_file_name(current_file_name):
    '''
    Drop revision and other things of current NWC file name so the previous version in a federated model can be replaced.

    :param current_file_name: _description_
    :type current_file_name: str
    :return: _description_
    :rtype: _type_
    '''

    return_value = current_file_name
    found_match = False
    try:
        for nwc_name_starts_width, new_nwc_file_name in NWC_FILE_NAMING:
            if (current_file_name.startswith(nwc_name_starts_width)):
                found_match = True
                return_value = new_nwc_file_name
                break
    except Exception as e:
        output('Failed to find match: {}'.format(e))
        return_value = current_file_name
    if(found_match):
        output('Found match for:  {} to: {}'.format(current_file_name, return_value))
    else:
        output('Found no match for:  {}'.format(current_file_name))
    return return_value

def _copy_nwc_files():
    '''
    Copy nwc files to Navisworks. federated model, location

    :return: True if all files where copied successfully, otherwise False.
    :rtype: bool
    '''

    status = True
    file_filter = '*.nwc'
    # check whether any files match the filter
    for nwc_file_name_start, nwc_target_folder in DEFAULT_NWC_LOCATIONS:
        files =  fileGet.GetFilesWithFilter (SOURCE_PATH, file_filter, nwc_file_name_start + '*')
        if(files != None and len(files) > 0):
            output('Copying nwc Files...' + str(len(files)))
            for file in files:
                try:
                    # extract file name only
                    file_name = Path.GetFileName(file)
                    src = SOURCE_PATH + '\\' + file_name
                    destination_file_name = _get_nwc_file_name(file_name)
                    dst = nwc_target_folder + '\\' + destination_file_name
                    copy_status = fileIO.CopyFile(src,dst)
                    status = status & copy_status
                    output('Copied file from:  {} to: {}'.format(src, dst))
                except Exception:
                    output('Failed to copy file from: {} to: {}'.format(src, dst))
                    status = False
        else:
            output('No nwc files matching filter: {} in source path: {}' .format(file_filter, SOURCE_PATH))
    return status

def create_target_directory(target_location, directory_name):
    '''
    Set up dated model incoming folder.

    :param target_location: Directory in which to create a new folder
    :type target_location: str
    :param directory_name: New folder name.
    :type directory_name: str
    :return: True if folder was created successfully, otherwise False
    :rtype: bool
    '''

    return_directory_name = directory_name
    # check if folder exists
    flag = False
    if(dirIO.DirectoryExists(target_location + '\\' + directory_name) == False):
        got_folder = False
        n = 1
        # create new folder (stop at 10 attempts)
        while (got_folder == False and n < 10):
            if (dirIO.DirectoryExists(target_location + '\\' + directory_name + '(' + str(n) + ')') == False):
                flag = dirIO.CreateFolder(target_location, directory_name + '(' + str(n) + ')')
                return_directory_name = directory_name + '(' + str(n) + ')'
                # ignore the flag coming back in to avoid infinite loops
                got_folder = True
            n += 1
    return flag, return_directory_name

def move_files(file_data):
    '''
    Move files into incoming folder(s)

    :param file_data: _description_
    :type file_data: _type_
    :return: True if all files where moved successfully, otherwise False.
    :rtype: bool
    '''

    status = True
    # get the date stamp
    directory_name = dateStamp.GetFolderDateStamp() + str('_Models')
    for file_filter, target_location in file_data:
        # check if target root path still exists
        if(path.exists(target_location)):
            # check whether any files match the filter
            files = fileGet.GetFilesWithFilter(SOURCE_PATH, '.*', file_filter + '*')
            # copy any *.nwc files into the right folders first
            _copy_nwc_files()
            # move files into file in location
            if(files != None and len(files) > 0):
                flag_got_directory = dirIO.CreateTargetFolder(target_location, directory_name)
                if flag_got_directory:
                    output('Moving Files... {}'.format(len(files)))
                    # move files
                    for file in files:
                        try:
                            # extract file name only
                            file_name = Path.GetFileName(file)
                            src = SOURCE_PATH + '\\' + file_name
                            dst = target_location + '\\' + directory_name + '\\' + file_name
                            shutil.move(src,dst)
                            status = status & True
                            output('Moved file from : {} to: {}'.format(src, dst))
                        except Exception:
                            output('Failed to move file from: {} to: {}'.format(src, dst))
                            status = False
                else:
                    output('Failed to create target folder: {}'.format(target_location))
            else:
                output('No files matching filter {} in source location: {}'.format(file_filter, SOURCE_PATH))
        else:
            output(target_location + ' no longer exists!')
            status = False
    return status

# --------------------- saving files received list ---------------------------------

def save_files_received_list():
    '''
    Saves out a file where each row contains the dates a file was received last.

    Note:
    This reads the previously written received file and only overwrites the date of files a match was found for/

    :return: True if everything went well, otherwise False.
    :rtype: bool
    '''

    status = True
    # get the current received file and read rows into 2D array
    current_issue_list = _read_current_file_received()
    # get current data mapping array
    all_files_mapping_table = _build_mapping_table()
    # data to be written back
    new_issue_list = []
    for row_counter in range(0, len(all_files_mapping_table)):
        new_issue_row = []
        column_counter = 0
        for files in all_files_mapping_table[row_counter]:
            for file_extension,name_filter in files:
                # get files and check for match
                date_value, revision = _get_file_match(file_extension, name_filter)
                if (date_value == '-'):
                    # use the value from currentIssueList (if there is one...)
                    if(current_issue_list is not None and len(current_issue_list)>0):
                        try:
                            new_issue_row.append(current_issue_list[row_counter + OUTPUT_ROW_HEADERS_COUNT][column_counter + OUTPUT_COLUMN_HEADERS_COUNT])
                            column_counter += 1
                            new_issue_row.append(current_issue_list[row_counter + OUTPUT_ROW_HEADERS_COUNT][column_counter + OUTPUT_COLUMN_HEADERS_COUNT])
                        except Exception:
                            # current file issue list has less columns the new one...add default
                            new_issue_row.append('-')# date
                            column_counter += 1
                            new_issue_row.append('-')# revision
                    else:
                        # no file issue list was found...add default value
                        new_issue_row.append('-')# date
                        column_counter += 1
                        new_issue_row.append('-')# revision
                else:
                    new_issue_row.append(date_value)
                    column_counter += 1
                    new_issue_row.append(revision)
                # increase column counter
                column_counter += 1
        new_issue_list.append(new_issue_row)
    # write array back to file
    padded_data = _add_headers_to_data(new_issue_list)
    status = _write_new_file_received_data(padded_data)
    return status

def _add_headers_to_data(new_issue_list):
    '''
    Adds row and column headers to files received data

    :param new_issue_list: _description_
    :type new_issue_list: _type_
    :return: _description_
    :rtype: _type_
    '''
    updated_data = []
    # check if row headers are required
    if (OUTPUT_ROW_HEADERS_COUNT > 0):
        # row counter
        row_index = 0
        for data_row in new_issue_list:
            column_index = 0
            for row_header in OUTPUT_ROW_HEADERS:
                data_row.insert(column_index, row_header[row_index])
                column_index  += 1
            updated_data.append(data_row)
            row_index += 1
    else:
        for data_row in new_issue_list:
            updated_data.append(data_row)
    # check if column headers are required
    if (OUTPUT_COLUMN_HEADERS_COUNT > 0):
        row_index = 0
        for column_header in OUTPUT_COLUMN_HEADERS:
            # Insert blank columns for row headers
            if (OUTPUT_ROW_HEADERS_COUNT > 0):
                for x in range(0,OUTPUT_ROW_HEADERS_COUNT):
                    column_header.insert(0,'-')
            # need to allow for row headers!!
            updated_data.insert(row_index, column_header)
            row_index += 1
    return updated_data

def _get_file_match(file_extension, name_filter):
    '''
    Find file match with filters provided
    File extension in format '.rvt'

    :param file_extension: _description_
    :type file_extension: _type_
    :param name_filter: _description_
    :type name_filter: _type_
    :return: _description_
    :rtype: str (default='-'), str(default='-')
    '''

    return_value = '-'
    revision = '-'
    # check whether valid name filter otherwise return '-'
    if(name_filter is not ''):
        files = fileGet.GetFilesWithFilter(SOURCE_PATH, file_extension, name_filter + '*')
        if (files is not None and len(files) > 0):
            # got a match
            return_value = dateStamp.GetFolderDateStamp()
            # get the revision
            revision = _get_file_revision(files[0])
    return return_value, revision

def _get_file_revision(file_name):
    '''
    Get the revision information from the file name.

    :param file_name: the file name
    :type file_name: str
    :return: the file revision, if exists, otherwise '-'
    :rtype: str (default='-')
    '''

    # default value in case no revision information is included in file name
    return_value = '-'
    for revision_start_char in REVISION_SEPARATOR_START:
        # check if file contains any of these
        start_index = file_name.find(revision_start_char)
        if ( start_index > 0):
            end_index = start_index + 1
            # look for end of revision
            for revision_end_char in REVISION_SEPARATOR_END:
                end_index = file_name.find(revision_end_char)
                if (end_index > 0):
                    break
            return_value = file_name[start_index + 1:end_index]
            break
    return return_value

def _build_mapping_table():
    '''
    Builds a mapping array from global nwc and rvt all files received lists
    This defines the rows and column of the incoming file tracker
    in this sample its: NWC, Revision of NWC, Revit, Revision of Revit

    :return: _description_
    :rtype: _type_
    '''

    mapping_array = []
    # loop over lists and build mapping table as required
    rvt_list = _rebuild_file_list(ALL_FILES_RECEIVED_RVT)
    nwc_list = _rebuild_file_list(ALL_FILES_RECEIVED_NWC)
    # loop over array and build mapping 2d array:
    # row discipline, column building in format ([filter (rvt), filename], [filter(nwc), filename])
    for x in range(0, len(nwc_list)):
        mapping_row = []
        for y in range(0,len(nwc_list[x])):
            mapping_row.append([nwc_list[x][y], rvt_list[x][y]])
        mapping_array.append(mapping_row)
    return mapping_array

def _rebuild_file_list(received_files):
    '''
    Loops over list of received files and builds a list of pairs of [file filter, file name]

    :param received_files: _description_
    :type received_files: _type_
    :return: _description_
    :rtype: _type_
    '''

    output_list = []
    for x in received_files:
        dummy = []
        for file_type_filter,file_name_filters in x:
            for file_name_filter in file_name_filters:
                dummy.append([file_type_filter, file_name_filter])
            output_list.append(dummy)
    return output_list

def _read_current_file_received():
    '''
    Read the current issue date file located in SourcePath location with name
    'issueList.csv'

    :return: _description_
    :rtype: _type_
    '''

    reference_list = []
    try:
        reference_list = fileCSV.ReadCSVfile(CURRENT_ISSUE_DATA_FILE_NAME)
    except Exception as e:
        output('Failed to open current model issue list with exception: {}'.format(e))
    return reference_list

def _write_new_file_received_data(data):
    '''
    Write new revision data out to file.

    :param data: _description_
    :type data: _type_
    :return: True if file was written successfully, otherwise False.
    :rtype: bool
    '''

    status = True
    try:
        fileCSV.writeReportDataAsCSV(CURRENT_ISSUE_DATA_FILE_NAME,[],data)
    except Exception as e:
        status = False
        output('Failed to write data file: {} with exception: {}'.format(CURRENT_ISSUE_DATA_FILE_NAME, e))
    return status

# -------------
# main:
# -------------

# store output here:
ROOT_PATH = r'C:\temp'
# directory containing incoming files
SOURCE_PATH = r'C:\temp'

# list of locations where incoming files are to be saved,
# format is:
# [Name starts with, fully qualified directory path]
# this script will create a dated folder in the location provided and move files into it
DEFAULT_MODEL_IN_LOCATIONS = [
    ['Structure File Name', r'C:\temp\Structure\In'],
    ['Fire Dry File Name', r'C:\temp\Fire\In'],
    ['Fire Wet File Name', r'C:\temp\Fire\In'],
    ['Electrical File Name', r'C:\temp\Electrical\In'],
    ['Security File Name', r'C:\temp\Security\In'],
    ['Mechanical File Name', r'C:\temp\Mechanical\In'],
    ['Steel Fabricator Zone File Name', r'C:\temp\Structure\In'],
    ['Hydraulic File Name', r'C:\temp\Hydraulic\In']
]


# list of locations where incoming NavisWorks files are to be saved
DEFAULT_NWC_LOCATIONS = [
    ['Structure File Name', r'C:\temp\NavisWorks'],
    ['Fire Dry File Name', r'C:\temp\NavisWorks'],
    ['Fire Wet File Name', r'C:\temp\NavisWorks'],
    ['Common File Name', r'C:\temp\NavisWorks']# all other consultants
]

# list containing the default file names:
# [[Navis file name before move, Navis file name after move]]
NWC_FILE_NAMING = [
    ['StructureFileBeforeName', 'StructureFileAfterName'],
    ['FireDryBeforeName', 'FireDryAfterName'],
    ['FireWetBeforeName', 'FireWetAfterName'],
    ['ElectricalFileBeforeName', 'ElectricalFileAfterName'],
    ['SecurityFileBeforeName', 'SecurityFileAfterName'],
    ['MechanicalFileBeforeName', 'MechanicalFileAfterName'],
    ['SteelFileBeforeName', 'SteelFileAfterName'],
    ['HydraulicFileBeforeName', 'HydraulicFileAfterName']
]

# nwc files list to build files received array 
NWC_ST_NORTH = [['.nwc',['StructureFileBeforeName']]]
NWC_ST_ONE = [['.nwc',['SteelFileBeforeName']]]
NWC_HY = [['.nwc',['HydraulicFileBeforeName']]]
NWC_FPW = [['.nwc',['FireWetBeforeName']]]
NWC_FPD = [['.nwc',['FireDryBeforeName']]]
NWC_ME = [['.nwc',['MechanicalFileBeforeName']]]
NWC_EL = [['.nwc',['ElectricalFileBeforeName']]]
NWC_SE = [['.nwc',['SecurityFileBeforeName']]]

# rvt files list to build files received array 
RVT_ST_NORTH = [['.rvt',['StructureFileBeforeName']]]
RVT_ST_ONE = [['.rvt',['SteelFileBeforeName']]]
RVT_HY = [['.rvt',['HydraulicFileBeforeName']]]
RVT_FPW = [['.rvt',['FireWetBeforeName']]]
RVT_FPD = [['.rvt',['FireDryBeforeName']]]
RVT_ME = [['.rvt',['MechanicalFileBeforeName']]]
RVT_EL = [['.rvt',['ElectricalFileBeforeName']]]
RVT_SE = [['.rvt',['SecurityFileBeforeName']]]

# build full files received baseline 2D array

output('Building files received mapping table.... start')
ALL_FILES_RECEIVED_NWC = [NWC_ST_NORTH, NWC_ST_ONE,  NWC_HY,  NWC_FPW, NWC_FPD, NWC_ME,  NWC_EL,  NWC_SE]
ALL_FILES_RECEIVED_RVT = [RVT_ST_NORTH, RVT_ST_ONE,  RVT_HY, RVT_FPW, RVT_FPD, RVT_ME, RVT_EL, RVT_SE]

CURRENT_ISSUE_DATA_FILE_NAME = SOURCE_PATH + r'\issueList.csv'
REVISION_SEPARATOR_START = ['[', '(']
REVISION_SEPARATOR_END = [']', ')']

# output headers
OUTPUT_COLUMN_HEADERS = [
    ['NWC','REVISION','REVIT','REVISION']
]
OUTPUT_ROW_HEADERS = [
    ['structure', 'structure - steel zone one','hydraulic','fire - wet','fire - dry','mechanical','electrical','security']
]

# these are used to correctly calculate the columns and rows containing data when reading existing data file
OUTPUT_COLUMN_HEADERS_COUNT = len(OUTPUT_COLUMN_HEADERS)
OUTPUT_ROW_HEADERS_COUNT = len(OUTPUT_ROW_HEADERS)

# save files received list
RESULT_SAVE_FILE_STATS = save_files_received_list()
output('Writing files received mapping table.... status [{}]'.format(RESULT_SAVE_FILE_STATS))

# move files
output('Moving files .... start')
RESULT = move_files(DEFAULT_MODEL_IN_LOCATIONS)
output('Moving files .... status: [{}]'.format(RESULT))