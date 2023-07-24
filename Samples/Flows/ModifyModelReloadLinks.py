'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Reload Revit and CAD links.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This flow demonstrates how to reload Revit and CAD links from a number of given locations.

Likely scenarios for this flows are:

- Linked models have undergone a change in name change and or location

Notes:

- Revit Batch Processor settings:
    
    - all worksets open
    - create new Local file

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
#
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
from duHast.Revit.Links import cad_links as rCadLink, links as rLink
from duHast.Utilities import date_stamps as dStamp

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

def link_name(name):
    '''
    Removes the last 8 characters from a link name:

    - file extension (4 characters)
    - 4 last characters in file name i.e. revision information

    Note:
    This is a sample only since the code below uses the default method RevitWorksets.DefaultLinkName

    :param name: The link name.
    :type name: str

    :return: Shortened link name.
    :rtype: str
    '''
    return name[0:-8]

# -------------
# main:
# -------------

# store output here:
ROOT_PATH = r'C:\temp'

HOST_NAME = dStamp.get_date_stamped_file_name(REVIT_FILE_PATH)

# list containing directories where Revit links are located:
# ['Directory path 1', 'Directory path 2']
LINK_REVIT_LOCATIONS = [r'C:\temp']

# list containing directories where CAD links are located:
# ['Directory path 1', 'Directory path 2']
LINK_CAD_LOCATIONS = [r'C:\temp']

# save revit file to new location
output('Modifying Revit File.... start')

# reload Revit links
RESULT_REVIT_LINKS_RELOAD = rLink.reload_revit_links(
    DOC, 
    LINK_REVIT_LOCATIONS, 
    HOST_NAME, 
    rLink.default_link_name, # this could be replaced by custom function i.e. LinkName(name) provided above
    rLink.default_workset_config_for_reload
)

output('{} :: [{}]'.format(RESULT_REVIT_LINKS_RELOAD.message ,RESULT_REVIT_LINKS_RELOAD.status))

# reload CAD links
RESULT_CAD_LINKS_RELOAD = rCadLink.reload_cad_links(
    DOC, 
    LINK_CAD_LOCATIONS, 
    HOST_NAME, 
    rLink.default_link_name # this could be replaced by custom function i.e. LinkName(name) provided above
)

output('{} :: [{}]'.format(RESULT_CAD_LINKS_RELOAD.message, RESULT_CAD_LINKS_RELOAD.status))

# sync changes back to central
if (DEBUG == False):
    output('Syncing to Central: start')
    SYNCING = rFileIO.sync_file (DOC)
    output('Syncing to Central: finished [{}]'.format (SYNCING.status))

output('Modifying Revit File.... finished ')
