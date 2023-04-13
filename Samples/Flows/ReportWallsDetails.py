'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Write wall type data to file.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This flow demonstrates how to write wall type data to file.

Note:
For wall type properties reported refer to :obj:`RevitWalls.GetWallReportData <RevitWalls.GetWallReportData>`.

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

# sample description
# how to report on wall types
# note: in place families of category wall and curtain wall do not have a valid Compound structure

# ---------------------------------
# default path locations
# ---------------------------------
# path to library modules
COMMON_LIBRARY_LOCATION = r'C:\temp'
# path to directory containing this script (in case there are any other modules to be loaded from here)
SCRIPT_LOCATION = r'C:\temp'
# debug mode revit project file name
DEBUG_REVIT_FILE_NAME = r'C:\temp\Test_walls.rvt'

import clr
import System

# set path to library and this script
import sys
sys.path += [COMMON_LIBRARY_LOCATION, SCRIPT_LOCATION]

# import common library
from duHast.APISamples.Walls.Reporting import RevitWallsReportHeader as rWallHeader
from duHast.APISamples.Walls.Reporting import RevitWallsReport as rWallRep
from duHast.Utilities import DateStamps as dStamp
from duHast.Utilities import FilesCSV as fileCSV

# autodesk API
from Autodesk.Revit.DB import *

clr.AddReference('System.Core')
clr.ImportExtensions(System.Linq)

# flag whether this runs in debug or not
DEBUG = False

# Add batch processor scripting references
if not DEBUG:
    import revit_script_util
    import revit_file_util
    clr.AddReference('RevitAPI')
    clr.AddReference('RevitAPIUI')
    DOC = revit_script_util.GetScriptDocument()
    REVIT_FILE_PATH = revit_script_util.GetRevitFilePath()
else:
    # get default revit file name
    REVIT_FILE_PATH = DEBUG_REVIT_FILE_NAME
    # get document from python shell
    DOC = doc

# -------------
# my code here:
# -------------

def output(message = ''):
    '''
    Output messages either to batch processor (debug = False) or console (debug = True)

    :param message: the message, defaults to ''
    :type message: str, optional
    '''

    if not DEBUG:
        revit_script_util.Output(str(message))
    else:
        print (message)

def write_wall_type_data(doc, fileName):
    '''
    Writes wall type data to a comma separated text file.

    :param doc: Current model document
    :type doc: Autodesk.Revit.DB.Document
    :param fileName: Fully qualified file path to report file.
    :type fileName: str

    :return: True if report file was written successfully, otherwise False
    :rtype: bool
    '''

    status = True
    try:
        status = fileCSV.writeReportDataAsCSV(
            fileName, 
            rWallHeader.REPORT_WALLS_HEADER, 
            rWallRep.GetWallReportData(doc, REVIT_FILE_PATH))
    except Exception as e:
        status = False
        output('Failed to write data file: {}'.format(fileName))
        output (str(e))
    return status

# -------------
# main:
# -------------

# store output here:
ROOT_PATH = r'C:\temp'

# build output file name
FILE_NAME_WALL_TYPE_REPORT =  ROOT_PATH + '\\'+ dStamp.GetOutPutFileName(REVIT_FILE_PATH,'.txt', '_WallTypes')

output('Writing Wall Type Data.... start')
#write out wall type data
RESULT = write_wall_type_data (DOC, FILE_NAME_WALL_TYPE_REPORT)
output('Writing Wall Type Data.... status: ' + str(RESULT))
output('Writing Wall Type Data.... finished ' + FILE_NAME_WALL_TYPE_REPORT)