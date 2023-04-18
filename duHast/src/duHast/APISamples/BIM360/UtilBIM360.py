'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to BIM360.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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

import System
import clr


from duHast.Utilities import FilesCSV as filesCSV
from duHast.UI import FileItem as fi
        
def get_bim_360_revit_files_from_file_list(filepathCSV, extension):
    '''
    Method reading BIM360 file data from a CSV file.

    :param filepathCSV: Fully qualified file path to CSV to be read.
    :type filepathCSV: str
    :param extension: Is an empty place holder...this method is past into another where it expects 2 arguments...
    :type extension: TODO
    :raise: On exception an empty list is returned.
    
    :return: List in format [Revit version, Project GUID, File GUID, file size in MB, file name]
    :rtype: list of str
    '''

    files = get_bim_360_file_data(filepathCSV)
    return files

def get_bim_360_file_data(filepathCSV):
    '''
    Reads a csv file containing BIM 360 file data into list of FileItem instances.

    :param filepathCSV: Fully qualified file path to CSV to be read.
    :type filepathCSV: str
    :return: a list of FileItem instances representing BIM360 file data.
        Will return an empty list of an exception occurred.
    :rtype: list of SampleCodeBatchProcessor.FileItem
    '''
    revitFiles = []
    try:
        # read the CSV into rows
        rows = filesCSV.read_csv_file(filepathCSV)
        # check whether anything came back
        if(len(rows)>0):
            # process rows
            for row in rows:
                dummy = process_bim_360_file_data_row(row)
                # check whether row got processed ok
                if (dummy is not None):
                    revitFiles.append(dummy)
    except Exception as e:
        print ('An exception occurred during BIM360 row processing! ' + str(e))
        # return an empty list which will cause this script to abort
        revitFiles = []
    return revitFiles

def process_bim_360_file_data_row (rowData):
    '''
    Reads a list of str into file item class object

    :param rowData: the list containing the file data
    :type rowData: list of str in format [Revit version, Project GUID, File GUID, file size in MB, file name]
    
    :return: Initialized file item instance, None if row is not the right length
    :rtype: SampleCodeBatchProcessor.FileItem
    '''

    # check whether we have the right number of columns
    if(len(rowData) == 5):
        dummy = fi.MyFileItem(rowData[4], int(rowData[3]), rowData[1], rowData[2], rowData[0])
        return dummy
    else:
        return None