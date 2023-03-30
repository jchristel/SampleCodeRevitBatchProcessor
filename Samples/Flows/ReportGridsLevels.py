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
commonLibraryLocation_ = r'C:\temp'
# path to directory containing this script (in case there are any other modules to be loaded from here)
scriptLocation_ = r'C:\temp'
# debug mode revit project file name
debugRevitFileName_ = r'C:\temp\Test_grids.rvt'

import clr
import System

# set path to library and this script
import sys
sys.path += [commonLibraryLocation_, scriptLocation_]

# import common libraries
from duHast.APISamples.Common import RevitCommonAPI as com
from duHast.APISamples import RevitGrids as rGrid
from duHast.APISamples import RevitLevels as rLevel
from duHast.Utilities import Utility as util

# flag whether this runs in debug or not
debug_ = False

# Add batch processor scripting references
if not debug_:
    import revit_script_util
    import revit_file_util
    clr.AddReference('RevitAPI')
    clr.AddReference('RevitAPIUI')
    # NOTE: these only make sense for batch Revit file processing mode.
    doc = revit_script_util.GetScriptDocument()
    revitFilePath_ = revit_script_util.GetRevitFilePath()
else:
    # get default revit file name
    revitFilePath_ = debugRevitFileName_

# -------------
# my code here:
# -------------

def Output(message = ''):
    '''
    Output messages either to batch processor (debug = False) or console (debug = True)

    :param message: the message, defaults to ''
    :type message: str, optional
    '''

    if not debug_:
        revit_script_util.Output(str(message))
    else:
        print (message)

def writeGridData(doc, fileName):
    '''
    Writes grid data to a tab separated text file.

    :param doc: Current model document
    :type doc: Autodesk.Revit.DB.Document
    :param fileName: Fully qualified file path to report file.
    :type fileName: str

    :return: True if report file was written successfully, otherwise False
    :rtype: bool
    '''

    status = True
    try:
        status = util.writeReportData(
            fileName, 
            rGrid.REPORT_GRIDS_HEADER, 
            rGrid.GetGridReportData(doc, revitFilePath_))
    except Exception as e:
        status = False
        Output('Failed to write data file!' + fileName)
        Output (str(e))
    return status

def writeLevelData(doc, fileName):
    '''
    Writes levels data to a tab separated text file.

    :param doc: Current model document
    :type doc: Autodesk.Revit.DB.Document
    :param fileName: Fully qualified file path to report file.
    :type fileName: str

    :return: True if report file was written successfully, otherwise False
    :rtype: bool
    '''

    status = True
    try:
        status = util.writeReportData(
            fileName, 
            rLevel.REPORT_LEVELS_HEADER, 
            rLevel.GetLevelReportData(doc, revitFilePath_))
    except Exception as e:
        status = False
        Output('Failed to write data file!' + fileName)
        Output (str(e))
    return status

# -------------
# main:
# -------------

# store output here:
rootPath_ = r'C:\temp'

# build output file names
fileNameGrid_ = rootPath_ + '\\'+ util.GetOutPutFileName(revitFilePath_,'.txt', '_grids')
fileNameLevel_ = rootPath_ + '\\'+ util.GetOutPutFileName(revitFilePath_,'.txt', '_levels')

#write out grid data
Output('Writing Grid Data.... start')
result_ = writeGridData(doc, fileNameGrid_)
Output('Writing Grid Data.... status: ' + str(result_))
Output('Writing Grid Data.... finished ' + fileNameGrid_)

#write out Level data
Output('Writing Level Data.... start')
result_ = writeLevelData(doc, fileNameLevel_)
Output('Writing Level Data.... status: ' + str(result_))
Output('Writing Level Data.... finished ' + fileNameLevel_)