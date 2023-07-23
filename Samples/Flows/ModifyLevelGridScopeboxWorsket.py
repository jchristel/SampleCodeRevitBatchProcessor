'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Move grid, levels, reference planes and scope boxes to a specified workset.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This flow demonstrates how move grids, levels, reference planes and scope boxes to a specific workset.

Note:

- Worksets are defined by project file to allow for maximum flexibility.
- Reference planes inside model elements (i.e. within stairs or in place families) can not have their workset changed by this flow.


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

# this sample demonstrates how to 
# modify the worksets of levels, grids, scope boxes and reference planes
# A list provides per file the default workset these elements should be on

# ---------------------------------
# default path locations
# ---------------------------------
# path to library modules
COMMON_LIBRARY_LOCATION = r'C:\temp'
# path to directory containing this script (in case there are any other modules to be loaded from here)
SCRIPT_LOCATION = r'C:\temp'
# DEBUG mode revit project file name
DEBUG_REVIT_FILE_NAME = r'C:\temp\Test_Files.rvt'

import clr
import System

# set path to library and this script
import sys
sys.path += [COMMON_LIBRARY_LOCATION, SCRIPT_LOCATION]

# import common libraries
from duHast.Revit.Common import file_io as rFileIO
from duHast.Revit.Common import worksets as rWork
from duHast.Utilities import utility as util
from duHast.Utilities.Objects import result as res
from duHast.Utilities.files_io import get_file_name_without_ext

# autodesk API
import Autodesk.Revit.DB as rdb

clr.AddReference('System.Core')
clr.ImportExtensions(System.Linq)

# flag whether this runs in DEBUG or not
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

# output messages either to batch processor (DEBUG = False) or console (DEBUG = True)
def output(message = ''):
    '''
    Output messages either to batch processor (DEBUG = False) or console (DEBUG = True)

    :param message: the message, defaults to ''
    :type message: str, optional
    '''

    if not DEBUG:
        revit_script_util.Output(str(message))
    else:
        print (message)

def modify(doc, revit_file_path, grid_data):
    '''
    Changes the worksets of grids, levels, reference planes and scope boxes.

    :param doc: Current model document
    :type doc: Autodesk.Revit.DB.Document
    :param revit_file_path: The current model (document) file path.
    :type revit_file_path: str
    :param grid_data: List of files and associated worksets names. Refer to `default_worksets` below.
    :type grid_data: [[filename, workset name]]

    :return: 
        Result class instance.

        - result.status: Change workset status returned in result.status. False if an exception occurred, otherwise True.
        - result.message: Will contain the category and fail / success counts.
        - result.result: will be an empty list
        
        On exception
        
        - Reload.status (bool) will be False
        - Reload.message will contain the exception message

    :rtype: :class:`.Result`
    '''

    return_value = res.Result()
    revit_file_name = str(get_file_name_without_ext(revit_file_path))
    flag = False
    for file_name, default_workset_name in grid_data:
        if (revit_file_name.startswith(file_name)):
            flag = True
            collector_grids = rdb.FilteredElementCollector(doc).OfClass(rdb.Grid)
            grids = rWork.modify_element_workset(doc, default_workset_name, collector_grids, 'grids')
            return_value.update(grids)

            collector_levels = rdb.FilteredElementCollector(doc).OfClass(rdb.Level)
            levels = rWork.modify_element_workset(doc, default_workset_name, collector_levels, 'levels')
            return_value.update(levels)

            collector_scope_boxes = rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_VolumeOfInterest)
            scope_boxes = rWork.modify_element_workset(doc, default_workset_name, collector_scope_boxes, 'scope boxes')
            return_value.update(scope_boxes)
            
            # fix up ref planes
            collector_ref_planes = rdb.FilteredElementCollector(doc).OfClass(rdb.ReferencePlane)
            ref_planes = rWork.modify_element_workset(doc, default_workset_name, collector_ref_planes,  'reference planes')
            return_value.update(ref_planes)
            
            break
    if (flag == False):
        return_value.update_sep(False, 'No grid data provided for current Revit file: {}'.format(revit_file_name))
    return return_value


# -------------
# main:
# -------------

# store output here:
ROOT_PATH = r'C:\temp'

output('Checking levels and grids.... start')

# a list in format
#[
#['Revit file name','workset levels, grids, scope boxes should be on'],
#['Revit file name','workset levels, grids, scope boxes should be on']
#]

DEFAULT_WORKSETS = [
    ['Test_grids', 'Shared Levels & Grids']
]

'''
List containing the workset name by project file
'''

# modify workset of levels, grids ands scope boxes
STATUS_MODIFY_WORKSETS = modify(DOC, REVIT_FILE_PATH, DEFAULT_WORKSETS)
output('{} :: [{}]'.format( STATUS_MODIFY_WORKSETS.message,STATUS_MODIFY_WORKSETS.status))

# sync changes back to central
if (DOC.IsWorkshared and DEBUG == False):
    output('Syncing to Central: start')
    SYNCING = rFileIO.sync_file (DOC)
    output('Syncing to Central: finished [{}] '.format(SYNCING.status))

output('Checking levels and grids.... finished ')