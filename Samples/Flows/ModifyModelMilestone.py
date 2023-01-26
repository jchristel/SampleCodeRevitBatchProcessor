'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Save a detached copy of a workshared project file.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This flow demonstrates how to detach a central file and save a copy in a time stamped folder.

Likely scenarios for this flows are:

- Models being send out for coordination
- Creating milestone copies

Notes:

- this sample creates a dated back-up folder in a given location and than re-creates a central file with the same name in the new location
- Revit Batch Processor settings:
    
    - detach model
    - all worksets closed
    - audit on opening
    - preserve worskets

- the SaveAs() method will compress the newly created central file by default
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


# ---------------------------------
# default path locations
# ---------------------------------
# path to library modules
commonLibraryLocation_ = r'C:\temp'
# path to directory containing this script (in case there are any other modules to be loaded from here)
scriptLocation_ = r'C:\temp'
# debug mode revit project file name
debugRevitFileName_ = r'C:\temp\Test_Files.rvt'

import clr
import System

# set path to library and this script
import sys
sys.path += [commonLibraryLocation_, scriptLocation_]

# import libraries
from duHast.APISamples import RevitCommonAPI as com
from duHast.APISamples import Utility as util

# autodesk API
import Autodesk.Revit.DB as rdb

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
    '''
    Output messages either to batch processor (debug = False) or console (debug = True)

    :param message: the message, defaults to ''
    :type message: str, optional
    '''

    if not debug_:
        revit_script_util.Output(str(message))
    else:
        print (message)

# -------------
# main:
# -------------

# store output (models) here:
rootPath_ = r'C:\temp'
modelOutFolderSuffix_ = '_Milestone'

# list containing the default file name:
# which in case of this back up is the same as the current file name
# [[revit host file name before save, revit host file name after save]]
defaultFileNames_ = [[util.GetFileNameWithoutExt(revitFilePath_), util.GetFileNameWithoutExt(revitFilePath_)]]

#save revit file to new location
Output('Modifying Revit File.... start')

# get mile stone folder
milestonePath_ = rootPath_ + '\\' + util.GetFolderDateStamp() + modelOutFolderSuffix_
flagGotFolder_ = util.CreateTargetFolder(rootPath_, util.GetFolderDateStamp() + modelOutFolderSuffix_)
# do we have a valid folder?
if (flagGotFolder_):
    # save new central file to back up folder
    result_ = com.SaveAs(doc, rootPath_ + '\\' + milestonePath_, revitFilePath_ , defaultFileNames_)
    Output(result_.message + ' :: ' + str(result_.status))
    # sync changes back to central
    if (debug_ == False):
        Output('Syncing to Central: start')
        syncing_ = com.SyncFile (doc)
        Output('Syncing to Central: finished ' + str(syncing_.status))
else:
    Output('failed to create target folder ' + milestonePath_)

('Modifying Revit File.... finished ')