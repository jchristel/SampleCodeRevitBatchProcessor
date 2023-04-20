'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Create a revision.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This flow demonstrates how to 

- add a revision (or multiple) to a document

Likely scenarios for this flows are:

- You may want to add a revision to multiple documents

Notes:

- Revit Batch Processor settings:
    
    - all worksets closed
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
import datetime

# set path to library and this script
import sys
sys.path += [COMMON_LIBRARY_LOCATION, SCRIPT_LOCATION]

# import libraries
from duHast.APISamples.Common import file_io as rFileIO
from duHast.APISamples.Revisions import RevitRevisions as rRev
from duHast.Utilities import Result as res

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
    #get default revit file name
    REVIT_FILE_PATH = DEBUG_REVIT_FILE_NAME
    # get document from python shell
    DOC = doc

# -------------
# my code here:
# -------------

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

def AddRevToDocument(doc):
    '''
    Adds a number of revisions to the document

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return:  
        Result class instance.
        
        - Revision(s) created status returned in result.status. False if an exception occurred, otherwise True.
        - result.message will contain the message revision created successfully.
        - result.result: will contain list of id's of new revision created
        
        On exception:
        
        - result.status (bool) will be False.
        - result.message will contain the exception message.
    
    :rtype: :class:`.Result`
    '''

    return_value = res.Result()
    # store rev id's in list 
    ids=[]
    try:
        for rev in revisions_to_add_:
            # create new revision
            new_revision_status = rRev.create_revision(doc, rev)
            if(new_revision_status.status):
                # append to existing revisions
                new_revision = new_revision_status.result[0]
                ids.Add(new_revision.Id)
        return_value.result = ids
    except Exception as e:
        return_value.update_sep(False, 'Failed to create revisions: {}'.format(e))
    return return_value

# -------------
# main:
# -------------

# store output here:
rootPath_ = r'C:\temp'

# list of revisions in format:
revisions_to_add_ = [
    rRev.revisionData(
        'Revision description text',
        'Issue to text',
        'Issue from text',
        rdb.RevisionNumberType.Numeric, # this is a numeric revision 
        datetime.datetime.now().strftime("%d/%m/%y"), # put the current date
        rdb.RevisionVisibility.Hidden # hide revision clouds and tags
    )
]

output('Add revision.... start')

# add revision to doc
result_  = AddRevToDocument(DOC)
output('Add revision.... status: [{}]'.format(result_.status))

# synch the file
if(DEBUG == False):
  if (DOC.IsWorkshared):
      output('Add revision.... Syncing to Central: start')
      syncing_ = rFileIO.sync_file (DOC)
      output('Syncing to Central: finished [{}]'.format (syncing_.status))
  else:
      #none work shared
      output('Add revision.... Saving non workshared file: start')
      DOC.SaveAs(REVIT_FILE_PATH)
      output('Add revision.... Saving non workshared file: finished')

output('Add revision.... finished ')