'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Write grids and levels data to file.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This flow demonstrates how to write grids and level property data to file.

Note:

- For grid properties reported refer to :obj:`RevitGrids.GetGridReportData <RevitGrids.GetGridReportData>`.
- For level properties reported refer to :obj:`RevitLevels.GetLevelReportData <RevitLevels.GetLevelReportData>`.
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


# ---------------------------------
# default path locations
# ---------------------------------
# path to library modules
COMMON_LIBRARY_LOCATION = r'C:\temp'
# path to directory containing this script (in case there are any other modules to be loaded from here)
SCRIPT_LOCATION = r'C:\temp'
# debug mode revit project file name
DEBUG_REVIT_FILE_NAME = r'C:\temp\Test_grids.rvt'

import clr
import System

# set path to library and this script
import sys
sys.path += [COMMON_LIBRARY_LOCATION, SCRIPT_LOCATION]

# import common libraries
from duHast.APISamples.Grids.Reporting import grids_report_header as rGridHeader
from duHast.APISamples.Grids.Reporting import grid_report_utils as rGridRep
from duHast.APISamples.Levels.Reporting import levels_report_header as rLevelHeader
from duHast.APISamples.Levels.Reporting import levels_report_utils as rLevelRep

from duHast.Utilities import DateStamps as dStamp
from duHast.Utilities import FilesCSV as fileCSV

# flag whether this runs in debug or not
DEBUG = False

# Add batch processor scripting references
if not DEBUG:
    import revit_script_util
    import revit_file_util
    clr.AddReference('RevitAPI')
    clr.AddReference('RevitAPIUI')
    # NOTE: these only make sense for batch Revit file processing mode.
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

def write_grid_data(doc, file_name):
    '''
    Writes grid data to a comma separated text file.

    :param doc: Current model document
    :type doc: Autodesk.Revit.DB.Document
    :param file_name: Fully qualified file path to report file.
    :type file_name: str

    :return: True if report file was written successfully, otherwise False
    :rtype: bool
    '''

    status = True
    try:
        status = fileCSV.write_report_data_as_csv(
            file_name, 
            rGridHeader.REPORT_GRIDS_HEADER, 
            rGridRep.get_grid_report_data(doc, REVIT_FILE_PATH))
    except Exception as e:
        status = False
        output('Failed to write data file: {}'.format(file_name))
        output (str(e))
    return status

def write_level_data(doc, file_name):
    '''
    Writes levels data to a comma separated text file.

    :param doc: Current model document
    :type doc: Autodesk.Revit.DB.Document
    :param file_name: Fully qualified file path to report file.
    :type file_name: str

    :return: True if report file was written successfully, otherwise False
    :rtype: bool
    '''

    status = True
    try:
        status = fileCSV.write_report_data_as_csv(
            file_name, 
            rLevelHeader.REPORT_LEVELS_HEADER, 
            rLevelRep.get_level_report_data(doc, REVIT_FILE_PATH))
    except Exception as e:
        status = False
        output('Failed to write data file: {}'.format(file_name))
        output (str(e))
    return status

# -------------
# main:
# -------------

# store output here:
ROOT_PATH = r'C:\temp'

# build output file names
FILE_NAME_GRID_REPORT = ROOT_PATH + '\\'+ dStamp.get_date_stamped_file_name(REVIT_FILE_PATH,'.txt', '_grids')
FILE_NAME_LEVEL_REPORT = ROOT_PATH + '\\'+ dStamp.get_date_stamped_file_name(REVIT_FILE_PATH,'.txt', '_levels')

#write out grid data
output('Writing Grid Data.... start')
RESULT = write_grid_data(DOC, FILE_NAME_GRID_REPORT)
output('Writing Grid Data.... status: {}'.format(RESULT))
output('Writing Grid Data.... finished: {}'.format(FILE_NAME_GRID_REPORT))

#write out Level data
output('Writing Level Data.... start')
RESULT = write_level_data(DOC, FILE_NAME_LEVEL_REPORT)
output('Writing Level Data.... status: {}'.format(RESULT))
output('Writing Level Data.... finished: {}'.format(FILE_NAME_LEVEL_REPORT))