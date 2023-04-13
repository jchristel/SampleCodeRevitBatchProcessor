'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Write shared parameter data to file.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This flow demonstrates how to write shared parameter data to file.

Note:
For shared parameter properties reported refer to :obj:`RevitSharedParameters.GetSharedParameterReportData <RevitSharedParameters.GetSharedParameterReportData>`.

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
# how to report on shared parameters
# note: shared parameters introduced to a project through a family do not report their category bindings through the below...

# ---------------------------------
# default path locations
# ---------------------------------
# path to library modules
COMMON_LIBRARY_LOCATION = r'C:\temp'
# path to directory containing this script (in case there are any other modules to be loaded from here)
SCRIPT_LOCATION = r'C:\temp'
# debug mode revit project file name
DEBUG_REVIT_FILE_NAME = r'C:\temp\Test_sharedPara.rvt'

import clr
import System

# set path to library and this script
import sys

from duHast.Utilities import DateStamps as dStamp
from duHast.Utilities import FilesCSV as fileCSV
from duHast.APISamples.SharedParameters.Reporting import RevitSharedParameterReportHeader as rSharedParaHeader
from duHast.APISamples.SharedParameters.Reporting import RevitSharedParameterReport as rSharedParaRep

sys.path += [COMMON_LIBRARY_LOCATION, SCRIPT_LOCATION]

# import common library
from duHast.Utilities import Utility as util
from duHast.APISamples import RevitSharedParameters as rSp

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

def write_shared_parameter_data(doc, file_name):
    '''
    Writes shared parameter data to a comma separated text file.

    :param doc: Current model document
    :type doc: Autodesk.Revit.DB.Document
    :param file_name: Fully qualified file path to report file.
    :type file_name: str

    :return: True if report file was written successfully, otherwise False
    :rtype: bool
    '''

    status = True
    try:
        status = fileCSV.writeReportDataAsCSV(
            file_name, 
            rSharedParaHeader.REPORT_SHAREDPARAMETERS_HEADER, 
            rSharedParaRep.GetSharedParameterReportData(doc, REVIT_FILE_PATH))
    except Exception as e:
        status = False
        output('Failed to write data file: {}'.format(file_name))
        output(str(e))
    return status

# -------------
# main:
# -------------

# store output here:
ROOT_PATH = r'C:\temp'

# build output file name
FILE_NAME_SHARED_PARA_REPORT =  ROOT_PATH + '\\'+ dStamp.GetOutPutFileName(REVIT_FILE_PATH,'.txt', '_SharedParas')

output('Writing Shared Parameter Data.... start')

#write out shared parameter data
RESULT = write_shared_parameter_data(DOC, FILE_NAME_SHARED_PARA_REPORT)

output('Writing Shared Parameter Data.... status: ' + str(RESULT))
output('Writing Shared Parameter Data.... finished ' + FILE_NAME_SHARED_PARA_REPORT)


