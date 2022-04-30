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
commonLibraryLocation_ = r'C:\temp'
# path to directory containing this script (in case there are any other modules to be loaded from here)
scriptLocation_ = r'C:\temp'
# debug mode revit project file name
debugRevitFileName_ = r'C:\temp\Test_Links.rvt'

import clr
import System

# set path to library and this script
import sys
sys.path += [commonLibraryLocation_, scriptLocation_]

# import common library
import Utility as util
import RevitLinks as rLink

# autodesk API
from Autodesk.Revit.DB import *

clr.AddReference('System.Core')
clr.ImportExtensions(System.Linq)

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
    #get default revit file name
    revitFilePath_ = debugRevitFileName_

# -------------
# my code here:
# -------------

# output messages either to batch processor (debug = False) or console (debug = True)
def Output(message = ''):
    if not debug_:
        revit_script_util.Output(str(message))
    else:
        print (message)

# method writing out Revit link information
# doc:          current model document
# fileName:     fully qualified file path
def writeRevitLinkData(doc, fileName):
    status = True
    try:
        status = util.writeReportData(
            fileName, 
            rLink.REPORT_REVIT_LINKS_HEADER, 
            rLink.GetRevitLinkReportData(doc, revitFilePath_))
    except Exception as e:
        status = False
        Output('Failed to write data file!' + fileName)
        Output (str(e))
    return status

# method writing out CAD link information
# doc:          current model document
# fileName:     fully qualified file path
def writeCADLinkData(doc, fileName):
    status = True
    try:
        status = util.writeReportData(
            fileName, 
            rLink.REPORT_CAD_LINKS_HEADER, 
            rLink.GetCADReportData(doc, revitFilePath_))
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
fileNameLinkRevit_ = rootPath_ + '\\'+ util.GetOutPutFileName(revitFilePath_,'.txt', '_RVT')
fileNameLinkCAD_ = rootPath_ + '\\'+ util.GetOutPutFileName(revitFilePath_,'.txt', '_CAD')

# write out revit link data
Output('Writing Revit Link Data.... start')
result_ = writeRevitLinkData(doc, fileNameLinkRevit_)
Output('Writing Revit Link.... status: ' + str(result_))
Output('Writing Revit Link.... finished ' + fileNameLinkRevit_)

#write out cad link data
Output('Writing CAD Link Data.... start')
result_ = writeCADLinkData(doc, fileNameLinkCAD_)
Output('Writing CAD Link Data.... status: ' + str(result_))
Output('Writing CAD Link Data.... finished ' + fileNameLinkCAD_)