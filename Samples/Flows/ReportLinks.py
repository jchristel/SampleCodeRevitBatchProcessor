'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Write link data to file.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This flow demonstrates how to write CAD and Revit link property data to file.

Note:

- For Revit link properties reported refer to :obj:`RevitLinks.GetRevitLinkReportData <RevitLinks.GetRevitLinkReportData>`.
- For CAD link properties reported refer to :obj:`RevitLinks.GetCADReportData <RevitLinks.GetCADReportData>`.
- For true Revit link location (shared or project internal) the link need to be loaded -> open all worksets in Revit Batch Processor settings is required
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
# how to report on CAD and Revit links (note: for true Revit link location (shared or project internal) the link need to be loaded -> open all worksets is required)

# ---------------------------------
# default path locations
# ---------------------------------
# path to library modules
COMMON_LIBRARY_LOCATION = r'C:\temp'
# path to directory containing this script (in case there are any other modules to be loaded from here)
SCRIPT_LOCATION = r'C:\temp'
# debug mode revit project file name
DEBUG_REVIT_FILE_NAME = r'C:\temp\Test_Links.rvt'

import clr
import System

# set path to library and this script
import sys
sys.path += [COMMON_LIBRARY_LOCATION, SCRIPT_LOCATION]

# import common library
from duHast.Utilities import DateStamps as dStamp
from duHast.APISamples.Links.Reporting import RevitLinksReportUtils as rLinkRep
from duHast.APISamples.Links.Reporting import RevitLinksReportHeader as rLinkHeader
from duHast.APISamples.Links.Reporting import RevitCadLinksReportUtils as rLinkCadRep
from duHast.APISamples.Links.Reporting import RevitCadLinksReportHeader as rLinkCadHeader
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
    #get default revit file name
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

def write_revit_link_data(doc, file_name):
    '''
    Writes Revit link data to a comma separated text file.

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
            rLinkHeader.REPORT_REVIT_LINKS_HEADER, 
            rLinkRep.GetRevitLinkReportData(doc, REVIT_FILE_PATH))
    except Exception as e:
        status = False
        output('Failed to write data file: {}'.format(file_name))
        output (str(e))
    return status

def write_cad_link_data(doc, file_name):
    '''
    Writes CAD link data to a comma separated text file.

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
            rLinkCadHeader.REPORT_CAD_LINKS_HEADER, 
            rLinkCadRep.GetCADReportData(doc, REVIT_FILE_PATH))
    except Exception as e:
        status = False
        output('Failed to write data file {}'.format(file_name))
        output (str(e))
    return status

# -------------
# main:
# -------------

# store output here:
ROOT_PATH = r'C:\temp'

# build output file names
FILE_NAME_LINK_REVIT_REPORT = ROOT_PATH + '\\'+ dStamp.GetOutPutFileName(REVIT_FILE_PATH,'.txt', '_RVT')
FILE_NAME_LINK_CAD_REPORT = ROOT_PATH + '\\'+ dStamp.GetOutPutFileName(REVIT_FILE_PATH,'.txt', '_CAD')

# write out revit link data
output('Writing Revit Link Data.... start')
RESULT = write_revit_link_data(DOC, FILE_NAME_LINK_REVIT_REPORT)
output('Writing Revit Link.... status: ' + str(RESULT))
output('Writing Revit Link.... finished ' + FILE_NAME_LINK_REVIT_REPORT)

#write out cad link data
output('Writing CAD Link Data.... start')
RESULT = write_cad_link_data(DOC, FILE_NAME_LINK_CAD_REPORT)
output('Writing CAD Link Data.... status: ' + str(RESULT))
output('Writing CAD Link Data.... finished ' + FILE_NAME_LINK_CAD_REPORT)