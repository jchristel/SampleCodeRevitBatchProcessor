"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to BIM360.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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

import System
import clr


from duHast.Utilities import files_csv as filesCSV
from duHast.UI import file_item as fi


def get_bim_360_revit_files_from_file_list(file_path_csv, extension):
    """
    Method reading BIM360 file data from a CSV file.

    :param file_path_csv: Fully qualified file path to CSV to be read.
    :type file_path_csv: str
    :param extension: Is an empty place holder...this method is past into another where it expects 2 arguments...
    :type extension: TODO
    :raise: On exception an empty list is returned.

    :return: List in format [Revit version, Project GUID, File GUID, file size in MB, file name]
    :rtype: list of str
    """

    files = get_bim_360_file_data(file_path_csv)
    return files


def get_bim_360_file_data(file_path_csv):
    """
    Reads a csv file containing BIM 360 file data into list of FileItem instances.

    :param file_path_csv: Fully qualified file path to CSV to be read.
    :type file_path_csv: str
    :return: a list of FileItem instances representing BIM360 file data.
        Will return an empty list of an exception occurred.
    :rtype: list of SampleCodeBatchProcessor.FileItem
    """
    revitFiles = []
    try:
        # read the CSV into rows
        rows = filesCSV.read_csv_file(file_path_csv)
        # check whether anything came back
        if len(rows) > 0:
            # process rows
            for row in rows:
                dummy = process_bim_360_file_data_row(row)
                # check whether row got processed ok
                if dummy is not None:
                    revitFiles.append(dummy)
    except Exception as e:
        print("An exception occurred during BIM360 row processing! {}".format(e))
        # return an empty list which will cause this script to abort
        revitFiles = []
    return revitFiles


def process_bim_360_file_data_row(row_data):
    """
    Reads a list of str into file item class object

    :param row_data: the list containing the file data
    :type row_data: list of str in format [Revit version, Project GUID, File GUID, file size in MB, file name]

    :return: Initialized file item instance, None if row is not the right length
    :rtype: SampleCodeBatchProcessor.FileItem
    """

    # check whether we have the right number of columns
    if len(row_data) == 5:
        dummy = fi.MyFileItem(
            name=row_data[4],
            size=int(row_data[3]),
            bim360_project_guid=row_data[1],
            bim360_file_guid=row_data[2],
            bim360_revit_version=row_data[0],
        )
        return dummy
    else:
        return None
