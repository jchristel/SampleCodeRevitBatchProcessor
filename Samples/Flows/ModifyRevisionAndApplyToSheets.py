'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Create a revision and add it to a specific sheet.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This flow demonstrates how to 

- add a revision (or multiple) to a document
- apply those revisions to sheets (filtered selection)
- mark the revision(s) as issued

Likely scenarios for this flows are:

- You may want to add a revision to a splash ( start up view) sheet for QA purposes every time you issue the model

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
from duHast.APISamples.Common import RevitFileIO as rFileIO
from duHast.APISamples.Views import RevitViews as rView, RevitViewSheets as rSheetView
from duHast.APISamples.Revisions import RevitRevisions as rRev
from duHast.Utilities import Utility as util, FilesIO as fileIO, Compare as comp
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

def get_sheets(doc, sheet_filter_rules):
    '''
    Get all sheets from the model matching filters supplied. 

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param sheetFilterRules: A set of rules. If sheet matches rule it will be returned. Defaults to None which will return all sheets. Refer to `sheetRules_` below.
    :type sheetFilterRules: [[filename,[[filter rules]]]]

    :return: List of sheets matching filter(s)
    :rtype: [Autodesk.Revit.DB.View]
    '''

    results = []
    # get sheets where revisions need to be applied to:
    revit_file_name = fileIO.GetFileNameWithoutExt(REVIT_FILE_PATH)
    for file_name, sheet_rules in sheet_filter_rules:
        if (revit_file_name.startswith(file_name)):
            results = rSheetView.GetSheetsByFilters(doc, sheet_rules)
            break
    return results

def mark_revisions_as_issued(doc, revIds):
    '''
    Marks revisions as issued.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param revIds: List of revision ids identifying revisions to be marked as issued.
    :type revIds: [Autodesk.Revit.DB.ElementId]

    :return:  
        Result class instance.
        
        - Revisions marked as issued status returned in result.status. False if an exception occurred, otherwise True.
        - result.message will contain the message(s) revision marked as issued successfully.
        - result.result: empty list
        
        On exception:
        
        - result.status (bool) will be False.
        - result.message will contain the exception message.
    
    :rtype: :class:`.Result`
    '''

    return_value = res.Result()
    # get all revisions in file
    revisions_in_model = rdb.Revision.GetAllRevisionIds(doc)
    # check against what was applied
    ids_to_be_marked_issued = set(revIds).intersection(revisions_in_model)
    for id in ids_to_be_marked_issued:
        # set revision status to issued
        result_set_to_issued = rRev.MarkRevisionAsIssuedByRevisionId(doc, id)
        return_value.Update(result_set_to_issued)
    return return_value

def add_revision_to_document(doc):
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
        for rev in REVISIONS_TO_ADD:
            # create new revision
            new_rev_status = rRev.CreateRevision(doc, rev)
            if(new_rev_status.status):
                # append to existing revisions
                newRev = new_rev_status.result[0]
                ids.Add(newRev.Id)
        return_value.result = ids
    except Exception as e:
        return_value.UpdateSep(False, 'Failed to create revisions: {}'.format(e))
    return return_value

# main function of this sample
def add_revisions_to_sheets_required(doc, sheet_filter_rules):
    '''
    Adds revision(s) to documents, applies revision(s) to sheet(s) and then sets the revision status to 'issued'.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param sheetFilterRules: A set of rules. If sheet matches rule it will be returned. Defaults to None which will return all sheets. Refer to `sheetRules_` below.
    :type sheetFilterRules: [[filename,[[filter rules]]]]

    :return:  
        Result class instance.
        
        - Revision(s) created, added to sheets, set to 'issued' status returned in result.status. False if an exception occurred, otherwise True.
        - result.message will contain the messages of each step required to create a revision, apply it to a sheet and set it to issued.
        - result.result: will contain list of id's of new revision created
        
        On exception:
        
        - result.status (bool) will be False.
        - result.message will contain the exception message.
    
    :rtype: :class:`.Result`
    '''

    return_value = res.Result()
    # get sheet to which revisions are to be applied
    sheets_in_model_filtered = get_sheets(doc, sheet_filter_rules)
    if(len(sheets_in_model_filtered) > 0 ):
        # set up revision
        revision_id_result = add_revision_to_document(doc)
        return_value.Update(revision_id_result)
        # check what came back
        if(revision_id_result.status):
            revIds = revision_id_result.result
            # get sheets where revisions need to be applied to:
            revit_file_name = fileIO.GetFileNameWithoutExt(REVIT_FILE_PATH)
            for file_name, sheet_rules in sheet_filter_rules:
                if (revit_file_name.startswith(file_name)):
                    # add revisions to sheets:
                    for sheet in sheets_in_model_filtered:
                        result_add_revisions_to_sheet = rRev.AddRevisionsToSheet(doc, sheet, revIds)
                        return_value.Update(result_add_revisions_to_sheet)
            # set revisions as issued
            result_mark_as_issued = mark_revisions_as_issued(doc, revIds)
            return_value.Update(result_mark_as_issued)
    else:
        return_value.UpdateSep(False, 'No sheet(s) matching filter(s) found')
    # wipe result list since it contains a mix of ids no longer required
    return_value.result = []
    return return_value

# -------------
# main:
# -------------

# store output here:
ROOT_PATH = r'C:\temp'

# list of revisions to be added to each model
REVISIONS_TO_ADD = [
    rRev.revisionData(
        'Revision description text',
        'Issue to text',
        'Issue from text',
        rdb.RevisionNumberType.Numeric, # this is a numeric revision 
        datetime.datetime.now().strftime("%d/%m/%y"), # put the current date
        rdb.RevisionVisibility.Hidden # hide revision clouds and tags
    )
]

# sheets to add revisions to rules 
SHEET_RULES = [
    [
        'FileOne',[
            ['Parameter Name', comp.ConDoesNotEqual, 'Parameter Value']
        ]
    ],# applies to files FileOneOneBeforeName and FileOneTwoBeforeName
    [
        'FileTwo', [
            ['Parameter Name', comp.ConDoesNotEqual, 'Parameter Value'],
            ['Parameter Name', comp.ConDoesNotEqual, 'Parameter Value']
        ]
    ]# applies to file FileTwoBeforeName
]

output('Add revision.... start')

#add revision to doc and to sheet named 'Splashscreen'
RESULT  = add_revisions_to_sheets_required(DOC, SHEET_RULES)
output('Add revision.... status: [{}]'.format(RESULT.status))

# synch the file
if(DEBUG == False):
  if (DOC.IsWorkshared):
      output('Add revision.... Syncing to Central: start')
      SYNCING = rFileIO.SyncFile (DOC)
      output('Syncing to Central: finished [{}]'.format (SYNCING.status))
  else:
      #none work shared
      output('Add revision.... Saving non workshared file: start')
      DOC.SaveAs(REVIT_FILE_PATH)
      output('Add revision.... Saving non workshared file: finished')

output('Add revision.... finished ')