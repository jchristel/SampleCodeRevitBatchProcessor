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


import os
from os import path


# flag whether this runs in debug or not
debug_ = False

# --------------------------
#default file path locations
# --------------------------
#store output here:
#rootPath_ = r'C:\temp'
rootPath_ = r'P:\18\1803009.000\Design\BIM\_Revit\3.0 Milestones'
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

#folder methods are in here:
import Common_Post as cp
from Common_Post import *

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

def CreateFolder(root, folderName):
    dirName = path.join(root,folderName)
    flag = True
    try:
        # Create target Directory
        Output('Creating directory ' + dirName)
        os.mkdir(dirName)
    except Exception:
        flag = False
    return flag
    
def CreateTargetFolder(targetLocation, folderName):
    returnFolderName = folderName
    #check if folder exists
    flag = False
    if(path.exists(targetLocation + '\\' + folderName) == False):
        flag = CreateFolder(targetLocation, folderName)
    else:
        #create new folder
        flag = True
    return flag, returnFolderName

# -------------
# main:
# -------------


#list containing the default file names:
# [[revit host file name before save, revit host file name after save]]
defaultFileNames_ = [[com.GetRevitFileName(revitFilePath_), com.GetRevitFileName(revitFilePath_)]]

#save revit file to new location
Output('Modifying Revit File.... start')

#get mile stone folder
flagGotFolder_, milestonePath_ = CreateTargetFolder(rootPath_, cp.GetFolderDateStamp() + str('_Milestone'))
if (flagGotFolder_):
    result_ = com.SaveAs(doc, rootPath_ + '\\' + milestonePath_, revitFilePath_ , defaultFileNames_)
    Output(result_.message + ' :: ' + str(result_.status))
    #sync changes back to central
    if (debug_ == False):
        Output('Syncing to Central: start')
        syncing_ = com.SyncFile (doc)
        Output('Syncing to Central: finished ' + str(syncing_.result))
else:
    Output('failed to create target folder ' + rootPath_ + '\\' + cp.GetFolderDateStamp() + str('_Milestone'))

('Modifying Revit File.... finished ')
