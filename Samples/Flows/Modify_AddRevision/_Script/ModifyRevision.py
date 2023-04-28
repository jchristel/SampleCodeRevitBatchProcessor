#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#License:
#
#
# Revit Batch Processor Sample Code
#
# Copyright (c) 2023  Jan Christel
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

# this sample moves revit link instances onto a workset specified in list

# --------------------------
# Imports
# --------------------------
 
import clr
import System
import datetime

import utilAddRevBVN as utilM # sets up all commonly used variables and path locations!
#import common library
from duHast.Revit.Common import file_io as rFileIO
from duHast.Revit.Revisions import revisions as rRev
from duHast.Utilities import result as res

# required in lambda expressions!
clr.AddReference('System.Core')
clr.ImportExtensions(System.Linq)

import Autodesk.Revit.DB as rdb

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
    REVIT_FILE_PATH = revit_script_util.GetRevitFilePath()
else:
    #get default revit file name
    REVIT_FILE_PATH = utilM.DEBUG_REVIT_FILE_NAME

# -------------
# my code here:
# -------------

# output messages either to batch processor (debug = False) or console (debug = True)
def Output(message = ''):
    if not debug_:
        revit_script_util.Output(str(message))
    else:
        print (message)

def get_splash_sheet(doc):
    collector = rdb.FilteredElementCollector(doc).OfClass(rdb.View).Where(lambda e: e.Name == utilM.SPLASH_SCREEN_SHEET_NAME)
    results = collector.ToList()
    return results

def mark_revisions_as_issued(doc, revIds):
    result = res.Result()
    # get all revisions in file
    revisions_in_model = rdb.Revision.GetAllRevisionIds(doc)
    # check against what was applied
    ids_of_revisions_to_be_marked_issued = set(revIds).intersection(revisions_in_model)
    #print (idsToBeMarkedIssued)
    for id in ids_of_revisions_to_be_marked_issued:
        rev_result = rRev.mark_revision_as_issued_by_revision_id(doc, id)
        result.update(rev_result)
    return result

def add_revisions_to_document(doc):
    result = res.Result()
    # store rev id's in list
    ids=[]
    try:
        for rev in REVISIONS_TO_ADD:
            # create new revision
            new_revision_status = rRev.create_revision (doc, rev)
            if(new_revision_status.status):
                # append to existing revisions
                ids.Add(new_revision_status.result[0].Id)
            else:
                raise ValueError(new_revision_status.message)
        result.result = ids
    except Exception as e:
        result.update_sep(False, 'Failed to create revisions with exception {}'.format(e))
    return result

def add_revisions_to_sheets(doc):
    result = res.Result()
    # get splashscreen sheet
    sheets = get_splash_sheet(doc)

    # set up revision
    revision_add_to_document_result = add_revisions_to_document(doc)

    # check what came back
    if(revision_add_to_document_result.status):
        revIds = revision_add_to_document_result.result
        # add revisions to sheets:
        for sheet in sheets:
            revision_add_to_sheet_result = rRev.add_revisions_to_sheet(doc, sheet, revIds)
            result.update(revision_add_to_sheet_result)
        # set revisions as issued
        revision_marked_as_issued_result = mark_revisions_as_issued(doc, revIds)
        result.update(revision_marked_as_issued_result)
    else:
        result = revision_add_to_document_result
    return result

# -------------
# main:
# -------------


REVISIONS_TO_ADD = [
    rRev.REVISION_DATA('MODEL ISSUE - FOR INFORMATION','JC', '', rdb.RevisionNumberType.Numeric, datetime.datetime.now().strftime("%d/%m/%y"),rdb.RevisionVisibility.Hidden)
]

Output('Add revision.... start')

#add revision to doc and to sheet named 'Splashscreen'
result_  = add_revisions_to_sheets(doc)
Output('Add revision.... message: {}\nAdd revision.... status: {}'.format(result_.message, result_.status))

# synch the file
if(debug_ == False):
    if (doc.IsWorkshared):
        Output('Add revision.... Syncing to Central: start')
        result_ = rFileIO.sync_file(doc)
        Output('Add revision.... Syncing to Central: finished [{}]'.format(result_.status))
    else:
        # none work shared
        Output('Add revision.... This is a non workshared file...not saved!')
Output('Add revision.... finished ')