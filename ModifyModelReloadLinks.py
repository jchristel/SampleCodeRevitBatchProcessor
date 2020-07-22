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

# this sample re-creates a central file by detaching the original file and then creating a new central file with the same name
# in the same location
# batch processor settings should be
# - all worksets closed
# - audit on opening
# - preserve worskets
# the SaveAs() method will compress the newly created central file by default

import clr
import System

# flag whether this runs in debug or not
debug_ = True

# --------------------------
#default file path locations
# --------------------------
#store output here:
#rootPath_ = r'C:\temp'
rootPath_ = r'P:\18\1803009.000\Design\BIM\_Revit\1.0 Project Files'
#path to Common.py
commonlibraryDebugLocation_ = r'P:\18\1803009.000\Design\BIM\_Revit\5.0 Project Resources\01 Scripts\04 BatchP\_Common'
#debug mode revit project file name
debugRevitFileName_ = r'C:\temp\Test_Files.rvt'

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

#special treatment to link names...
#ignores the revit file version (4 characters) at the end of the file name and the file extension (4 characters) also at end of file
def LinkName(name):
    return name[0:-8]

# -------------
# main:
# -------------
hostName_ = com.GetOutPutFileName(revitFilePath_)

#list containing directories where Revit links are located:
# ['Directory path 1', 'Directory path 2']
linkRevitLocations_ = [r'C:\temp']

#list containing directories where CAD links are located:
# ['Directory path 1', 'Directory path 2']
linkCADLocations_ = [r'C:\temp']


#save revit file to new location
Output('Modifying Revit File.... start')

#reload Revit links
resultRevitLinksReload_ = com.ReloadRevitLinks(doc, linkRevitLocations_, hostName_, com.DefaultLinkName, com.DefaultWorksetConfigForReload)
Output(resultRevitLinksReload_.message + ' :: ' + str(resultRevitLinksReload_.status))

#reload CAD links
resultCADLinksReload_ = com.ReloadCADLinks(doc, linkCADLocations_, hostName_, com.DefaultLinkName)
Output(resultCADLinksReload_.message + ' :: ' + str(resultCADLinksReload_.status))

#sync changes back to central
if (debug_ == False):
    Output('Syncing to Central: start')
    syncing_ = com.SyncFile (doc)
    Output('Syncing to Central: finished ' + str(syncing_.status))

Output('Modifying Revit File.... finished ')
