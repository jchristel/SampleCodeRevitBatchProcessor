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
    - preserve worksets

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


# ---------------------------------
# default path locations
# ---------------------------------
# path to library modules
COMMON_LIBRARY_LOCATION = r'C:\temp'
# path to directory containing this script (in case there are any other modules to be loaded from here)
SCRIPT_LOCATION = r'C:\temp'
# debug mode revit project file name
DEBUG_REVIT_FILE_NAME = r'C:\temp\Test_Files.rvt'

import clr
import System

# set path to library and this script
import sys
sys.path += [COMMON_LIBRARY_LOCATION, SCRIPT_LOCATION]

# import libraries
from duHast.Revit.Common import file_io as rFileIO
from duHast.Utilities import date_stamps as dStamp, directory_io as dirIO, utility as util
from duHast.Utilities import files_io as fileIO

# autodesk API
import Autodesk.Revit.DB as rdb

clr.AddReference('System.Core')
clr.ImportExtensions(System.Linq)

# flag whether this runs in debug or not
DEBUG = True

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

# output messages either to batch processor (debug = False) or console (debug = True)
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

# -------------
# main:
# -------------

# store output (models) here:
ROOT_PATH = r'C:\temp'
MODEL_OUT_FOLDER_SUFFIX = '_Milestone'

# list containing the default file name:
# which in case of this back up is the same as the current file name
# [[revit host file name before save, revit host file name after save]]
DEFAULT_FILE_NAMES = [[fileIO.get_file_name_without_ext(REVIT_FILE_PATH), fileIO.get_file_name_without_ext(REVIT_FILE_PATH)]]

#save revit file to new location
output('Modifying Revit File.... start')

# get mile stone folder
MILESTONE_PATH = ROOT_PATH + '\\' + dStamp.get_folder_date_stamp() + MODEL_OUT_FOLDER_SUFFIX
GOT_DIRECTORY = dirIO.create_target_directory(ROOT_PATH, dStamp.get_folder_date_stamp() + MODEL_OUT_FOLDER_SUFFIX)
# do we have a valid folder?
if GOT_DIRECTORY:
    # save new central file to back up folder
    RESULT = rFileIO.save_as(DOC, ROOT_PATH + '\\' + MILESTONE_PATH, REVIT_FILE_PATH , DEFAULT_FILE_NAMES)
    output('{} :: [{}]'.format(RESULT.message ,RESULT.status))
    # sync changes back to central
    if (DEBUG == False):
        output('Syncing to Central: start')
        SYNCING = rFileIO.sync_file (DOC)
        output('Syncing to Central: finished [{}]'.format (SYNCING.status))
else:
    output('failed to create target folder: {} '.format(MILESTONE_PATH))

('Modifying Revit File.... finished ')