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
# how to report on worksets

# ---------------------------------
# default path locations
# ---------------------------------
# path to library modules
commonLibraryLocation_ = r'C:\temp'
# path to directory containing this script (in case there are any other modules to be loaded from here)
scriptLocation_ = r'C:\temp'
# debug mode revit project file name
debugRevitFileName_ = r'C:\temp\Test_worksets.rvt'

import clr
import System

# set path to library and this script
import sys
sys.path += [commonLibraryLocation_, scriptLocation_]

# import common libraries
import Utility as util

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
    # get default revit file name
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

# method writing out shared parameter information
def writeWorksetData(doc, fileName):
    status = True
    try:
        f = open(fileName, 'w')
        f.write('\t'.join(['HOSTFILE', 'ID', 'NAME', 'ISVISIBLEBYDEFAULT', '\n']))
        for p in FilteredWorksetCollector(doc).OfKind(WorksetKind.UserWorkset):
            f.write('\t'.join([util.GetFileNameWithoutExt(revitFilePath_), str(p.Id.IntegerValue), util.EncodeAscii(p.Name), str(p.IsVisibleByDefault), '\n']))
        f.close()
    except Exception as e:
        status = False
        Output('Failed to write data file! ' + fileName + ' with exception: ' + str(e))
    return status

# -------------
# main:
# -------------

# store output here:
rootPath_ = r'C:\temp'

# build output file name
fileName_ = rootPath_ + '\\'+ util.GetOutPutFileName(revitFilePath_)

Output('Writing Workset Data.... start')

# write out workset data
result_ = writeWorksetData(doc, fileName_)

Output('Writing Workset Data.... status: ' + str(result_))
Output('Writing Workset Data.... finished ' + fileName_)