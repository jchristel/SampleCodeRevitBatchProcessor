#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2023, Jan Christel
# All rights reserved.

# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

# - Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# - Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# - Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
#
# This software is provided by the copyright holder "as is" and any express or implied warranties, including, but not limited to, the implied warranties of merchantability and fitness for a particular purpose are disclaimed.
# In no event shall the copyright holder be liable for any direct, indirect, incidental, special, exemplary, or consequential damages (including, but not limited to, procurement of substitute goods or services; loss of use, data, or profits;
# or business interruption) however caused and on any theory of liability, whether in contract, strict liability, or tort (including negligence or otherwise) arising in any way out of the use of this software, even if advised of the possibility of such damage.
#
#
#

# this sample re-creates a central file by detaching the original file and then creating a new central file with the same name
# in the same location
# batch processor settings should be
# - all worksets closed
# - audit on opening
# - preserve worskets
# the SaveAs() method will compress the newly created central file by default

# --------------------------
#default file path locations
# --------------------------

import clr
import System

import utilReloadBVN as utilR # sets up all commonly used variables and path locations!
# import common library
import RevitCommonAPI as com
import Result as res
import RevitFamilyReload as rFamReload
import RevitFamilyUtils as rFamUtils
import Utility as util
from timer import Timer

#clr.AddReference('System.Core')
#clr.ImportExtensions(System.Linq)

from Autodesk.Revit.DB import *

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
    revitFilePath_ = utilR.DEBUG_REVIT_FILE_NAME

# -------------
# my code here:
# -------------

# output messages either to batch processor (debug = False) or console (debug = True)
def Output(message = ''):
    if not debug_:
        revit_script_util.Output(str(message))
    else:
        print (message)

# -------------
# main:
# -------------

# setup timer
t = Timer()
t.start()

# debug test 
Output('Script directory: ' + utilR.SCRIPT_DIRECTORY)

Output('Modifying Revit File.... start')

# start reload
flag = rFamReload.ReloadAllFamilies(
    doc, 
    utilR.REVIT_LIBRARY_PATH,
    utilR.REVIT_LIBRARY_INCLUDE_SUB_DIRS_IN_SEARCH
    )

# show results
Output (flag.message)
Output ('Overall reload status: ' + str(flag.status))
Output (str(t.stop()))

# get the file name
fileName = util.GetFileNameWithoutExt(revitFilePath_)
revitFilePathNew_ = utilR.WORKING_DIRECTORY + '\\' + fileName + '.rfa'

# save file if required
if (True):
    # save family file
    Output('Saving family file: start')
    syncing_ = com.SaveAsFamily(doc, utilR.WORKING_DIRECTORY, revitFilePath_, [[fileName, fileName]], '.rfa', True)
    Output('Saving family file: finished ' + str(syncing_.message) + ' :: '  + str(syncing_.status))
    # save marker file
    if(syncing_.status == False):
        Output(str(syncing_.message))
    else:
        # write marker file
        fileNameMarker = utilR.WORKING_DIRECTORY + '\\' + fileName + '_marker_.temp'
        try:
            writeDataFlag = util.writeReportDataAsCSV(
                fileNameMarker, 
                '', 
                [
                    ['Copy From', 'Copy To'],
                    [revitFilePathNew_, revitFilePath_]]
                )
            Output('Wrote marker file: ' + str(fileNameMarker) + ' :: '  + str(True)) 
        except Exception as e:
            Output('Wrote marker file: ' + str(fileNameMarker) + ' :: '  + str(False) + '  Exception: ' + str(e))