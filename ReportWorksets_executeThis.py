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

import clr
import System

# flag whether this runs in debug or not
debug_ = False

# --------------------------
#default file path locations
# --------------------------
#store output here:
rootPath_ = r'C:\temp'
#path to Common.py
commonlibraryDebugLocation_ = r'C:\temp'
#debug mode revit project file name
debugRevitFileName_ = r'C:\temp\Test_worksets.rvt'

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

#set path to common library
import sys
sys.path.append(commonlibraryDebugLocation_)
#import common library
import Common as com
from Common import *

clr.AddReference('System.Core')
clr.ImportExtensions(System.Linq)

from Autodesk.Revit.DB import *

#output messages either to batch processor (debug = False) or console (debug = True)
def Output(message = ''):
    if not debug_:
        revit_script_util.Output(str(message))
    else:
        print (message)

# -------------
# my code here:
# -------------

#build output file name
fileName_ = rootPath_ + '\\'+ com.GetOutPutFileName(revitFilePath_)

#method writing out shared parameter information
def writeWorksetData(doc, fileName):
    status = True
    try:
        f = open(fileName, 'w')
        f.write('\t'.join(['HOSTFILE', 'ID', 'NAME', 'ISVISIBLEBYDEFAULT', '\n']))
        for p in FilteredWorksetCollector(doc).OfKind(WorksetKind.UserWorkset):
            f.write('\t'.join([com.GetRevitFileName(revitFilePath_), str(p.Id.IntegerValue), com.EncodeAscii(p.Name), str(p.IsVisibleByDefault), '\n']))
        f.close()
    except Exception as e:
        status = False
        Output('Failed to write data file! ' + fileName + ' with exception: ' + str(e))
        Output (str(e))
    return status

# -------------
# main:
# -------------

Output('Writing Workset Data.... start')

#write out shared parameter data
result_ = writeWorksetData(doc, fileName_)

Output('Writing Workset Data.... status: ' + str(result_))
Output('Writing Workset Data.... finished ' + fileName_)
