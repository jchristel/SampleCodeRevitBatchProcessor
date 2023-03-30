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
from duHast.APISamples.Common import RevitCommonAPI as com
from duHast.APISamples import RevitLinks as rLink
from duHast.Utilities import Utility as util

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

def LinkName(name):
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
rootPath_ = r'C:\temp'

hostName_ = util.GetOutPutFileName(revitFilePath_)

# list containing directories where Revit links are located:
# ['Directory path 1', 'Directory path 2']
linkRevitLocations_ = [r'C:\temp']

# list containing directories where CAD links are located:
# ['Directory path 1', 'Directory path 2']
linkCADLocations_ = [r'C:\temp']

# save revit file to new location
Output('Modifying Revit File.... start')

# reload Revit links
resultRevitLinksReload_ = rLink.ReloadRevitLinks(
    doc, 
    linkRevitLocations_, 
    hostName_, 
    rLink.DefaultLinkName, # this could be replaced by custom function i.e. LinkName(name) provided above
    rLink.DefaultWorksetConfigForReload
)

Output(resultRevitLinksReload_.message + ' :: ' + str(resultRevitLinksReload_.status))

# reload CAD links
resultCADLinksReload_ = rLink.ReloadCADLinks(
    doc, 
    linkCADLocations_, 
    hostName_, 
    rLink.DefaultLinkName # this could be replaced by custom function i.e. LinkName(name) provided above
)

Output(resultCADLinksReload_.message + ' :: ' + str(resultCADLinksReload_.status))

# sync changes back to central
if (debug_ == False):
    Output('Syncing to Central: start')
    syncing_ = com.SyncFile (doc)
    Output('Syncing to Central: finished ' + str(syncing_.status))

Output('Modifying Revit File.... finished ')
