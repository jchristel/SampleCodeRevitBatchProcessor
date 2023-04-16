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
from duHast.APISamples.Common import RevitFileIO as rFileIO
from duHast.APISamples.Links import RevitLinks as rLink, RevitCadLinks as rCadLink
from duHast.Utilities import DateStamps as dStamp

# autodesk API
import Autodesk.Revit.DB as rdb

clr.AddReference('System.Core')
clr.ImportExtensions(System.Linq)

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

HOST_NAME = dStamp.GetOutPutFileName(REVIT_FILE_PATH)

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
