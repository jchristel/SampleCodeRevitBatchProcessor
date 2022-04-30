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

import csv
import System
import clr
import csv
import FileItem as fi
import Utility as util


# helper method retrieving files in a given directory and of a given file extension
# filepathCSV           path to CSV to be read
# extension             is empty place holder...this method is passt into another where it expects 2 arguments...
def getBIM360RevitFilesFromFileList(filepathCSV, extension):
    files = GetBIM360Data(filepathCSV)
    return files

# entry point for processing a csv file containing BIM 360 data
# filepathCSV       path to CSV to be read
def GetBIM360Data(filepathCSV):
    revitfiles = []
    try:
        # read the CSV into rows
        rows = util.ReadCSVfile(filepathCSV)
        # check whether anything came back
        if(len(rows)>0):
            # process rows
            for row in rows:
                dummy = ProcessBIM360Row(row)
                # check whether row got processed ok
                if (dummy is not None):
                    revitfiles.append(dummy)
    except Exception as e:
        print ('An exception occured during BIM360 row processing! ' + str(e))
        # return an empty list which will cause this script to abort
        revitfiles = []
    return revitfiles

# reads a row from csv file into file item class object
# returns None if row is not the right length
def ProcessBIM360Row (rowData):
    # check whether we have the right number of columns
    if(len(rowData) == 5):
        dummy = fi.MyFileItem(rowData[4], int(rowData[3]), rowData[1], rowData[2], rowData[0])
        return dummy
    else:
        return None