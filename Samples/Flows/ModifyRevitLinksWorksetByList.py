'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Link workset updates - by list.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This flow demonstrates how to change revit link instance and type worksets based on a list.

Notes:

- Revit Batch Processor settings:
    
    - open local copy of model
    - open all worksets

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
# Copyright © 2023, Jan Christel
# All rights reserved.

# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

# - Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# - Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# - Neither the name of Jan Christel nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
#
# This software is provided by Jan Christel "as is" and any express or implied warranties, including, but not limited to, the implied warranties of merchantability and fitness for a particular purpose are disclaimed. 
# In no event shall Jan Christel be liable for any direct, indirect, incidental, special, exemplary, or consequential damages (including, but not limited to, procurement of substitute goods or services; loss of use, data, or profits; 
# or business interruption) however caused and on any theory of liability, whether in contract, strict liability, or tort (including negligence or otherwise) arising in any way out of the use of this software, even if advised of the possibility of such damage.
#
#
#

# this sample demonstrates how to move revit link instances and types onto the a workset provided in list below

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
from duHast.Revit.Common import worksets as rWork
from duHast.Utilities import utility as util
from duHast.Utilities.Objects import result as res
from duHast.Revit.Common import transaction as rTran

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

def _changeWorkset(doc, el, link_name, from_workset_name, to_workset_name, to_workset_id, descriptor):
    '''
    Changes the workset of a link instance or link type

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param el: The element of which the workset is to be changed.
    :type el: AutoDesk.Revit.DB.Element
    :param link_name: The link name
    :type link_name: str
    :param from_workset_name: The current workset name.
    :type from_workset_name: str
    :param to_workset_name: The new workset name.
    :type to_workset_name: str
    :param to_workset_id: The new workset element id.
    :type to_workset_id: AutoDesk.Revit.DB.ElementId
    :param descriptor: Human readable description of the transaction.
    :type descriptor: str

    :return: 
        Result class instance.

        - Result.status: True if a link instance or type was successfully moved to a new workset, Otherwise False
        - Result.message: A status message for each link.
        - Result.result is empty list

        On exception:
        
        - Set parameter.status (bool) will be False.
        - Set parameter.message will contain the exception message.

    :rtype: :class:`.Result`
    '''

    output('{} :: Moving {} from: {} to: {}'.format(descriptor, link_name, from_workset_name, to_workset_name))
    transaction = rdb.Transaction(doc, "Changing workset of " + link_name)
    result = rTran.in_transaction(transaction,  rWork.get_action_change_element_workset(el,to_workset_id))
    output('{} [{}] '.format(link_name ,result.status))
    return result

def _ModifyRevitLinkTypeWorksetName(doc, link_name, workset_name):
    '''
    Modifies a revit link type workset.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param link_name: The link name.
    :type link_name: str
    :param workset_name: The target workset name.
    :type workset_name: str

    :return: 
        Result class instance.

        - Result.status: True if all link types where moved to their specified worksets, otherwise False.
        - Result.message: A status message for each link type.
        - Result.result is empty list

        On exception:
        
        - Set parameter.status (bool) will be False.
        - Set parameter.message will contain the exception message.

    :rtype: :class:`.Result`
    '''
    
    return_value = res.Result()
    # get the target workset id
    target_workset_id = rWork.get_workset_id_by_name(doc, workset_name)
    # check if workset still exists
    if(target_workset_id != rdb.ElementId.InvalidElementId):
        # loop over link types and try to find a match
        for p in rdb.FilteredElementCollector(doc).OfClass(rdb.RevitLinkType):
            link_type_name = rdb.Element.Name.GetValue(p)
            if (link_type_name.startswith(link_name)):
                workset_param = p.get_Parameter(rdb.BuiltInParameter.ELEM_PARTITION_PARAM)
                type_workset_name = workset_param.AsValueString()
                if(type_workset_name != workset_name):
                    # change the workset of the link type
                    return_value = _changeWorkset(doc, p, link_type_name, type_workset_name, workset_name, target_workset_id,'Type')
                else:
                    # no need to do anything
                    return_value.message = 'Type {} is already on default workset {}.'.format(link_type_name, workset_name)
                break
    else:
        return_value.update_sep(False, 'Workset {} does no longer exist in file!'.format(workset_name ))
    return return_value

def _ModifyRevitLinkInstanceWorkset(doc, link_name, workset_name):
    '''
    Modifies a revit link instance workset.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param link_name: The link instance name.
    :type link_name: str
    :param workset_name: the target workset name.
    :type workset_name: str

    :return: 
        Result class instance.

        - Result.status: True if all link instances where moved to their specified worksets, otherwise False.
        - Result.message: A status message for each link instance.
        - Result.result is empty list

        On exception:
        
        - Set parameter.status (bool) will be False.
        - Set parameter.message will contain the exception message.

    :rtype: :class:`.Result`
    '''

    return_value = res.Result()
    # get the target workset id
    target_workset_id = rWork.get_workset_id_by_name(doc, workset_name)
    # check if workset still exists
    if(target_workset_id != rdb.ElementId.InvalidElementId):
        # loop over instances and find match
        for p in rdb.FilteredElementCollector(doc).OfClass(rdb.RevitLinkInstance):
            #get the workset
            workset_param = p.get_Parameter(rdb.BuiltInParameter.ELEM_PARTITION_PARAM)
            instance_workset_name = workset_param.AsValueString()
            link_name = "unknown"
            # split revit link name at colon
            link_type_name_parts = p.Name.split(':')
            if(len(link_type_name_parts) == 3):
                link_name = link_type_name_parts[0][0:-1]
                link_instance_name_encoded = util.encode_ascii(link_name[0:-1])
                if (link_name.startswith(link_name)):
                    if (instance_workset_name != workset_name):
                        # change the workset of the link instance
                        return_value = _changeWorkset(doc, p, link_instance_name_encoded, instance_workset_name, workset_name, target_workset_id, 'Instance')
                    else:
                        # no need to do anything
                        return_value.message = 'Instance {} is already on default workset: '.format(link_instance_name_encoded ,workset_name)
            else:
                return_value.update_sep(False, 'Failed to split link name into 3 parts')
    else:
        return_value.update_sep(False, 'Workset: {} does no longer exist in file!'.format(workset_name ))
    return return_value

# 
def ModifyRevitLinkData(doc, revitFilePath, linkData):
    '''
    Method moving revit link instances and types to the same workset as defined in list

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param revitFilePath: The current model file path.
    :type revitFilePath: str
    :param linkData: List containing the default worksets for links. Refer to `defaultWorksets_`
    :type linkData: [[str],[[str, str],[str, str],...]

    :return: 
        Result class instance.

        - Result.status: True if all links where moved to their specified worksets, otherwise False.
        - Result.message: A status message for each link instance and link type.
        - Result.result is empty list

        On exception:
        
        - Set parameter.status (bool) will be False.
        - Set parameter.message will contain the exception message.

    :rtype: :class:`.Result`
    '''

    returnValue = res.Result()
    match = False
    try:
        revitFileName = util.GetFileNameWithoutExt(revitFilePath)
        for fileName, worksetData in linkData:
            if (revitFileName.startswith(fileName)):
                match = True   
                # loop over link data and change link worksets as required
                for linkName, newWorksetName in worksetData:
                    changeLinkInstance = _ModifyRevitLinkInstanceWorkset(doc, linkName, newWorksetName)
                    returnValue.update(changeLinkInstance)
                    changeLinkType = _ModifyRevitLinkTypeWorksetName(doc, linkName, newWorksetName)
                    returnValue.update(changeLinkType)
                break
        if (match == False):
            output('Failed to find current Revit file link workset data!')
    except Exception as e:
        returnValue.update_sep(False, 'Failed to modify revit link instances with exception: ' + str(e))
    return returnValue

# -------------
# main:
# -------------

# store output here:
rootPath_ = r'C:\temp'

# list containing the default worksets for links in format:
# [[revit host file name],[[Link file name, workset name],[link file name, workset name]]
defaultWorksets_ = [
    ['Test_Links', 
        [
            ['Link Name','Workset Name'],
            ['Link Name','Workset Name']
        ]
    ],
    ['Test_Links', 
        [
            ['Link Name','Workset Name']
        ]
    ],
]

# modify revit links
output('Modifying Revit Link(s).... start')
result_ = ModifyRevitLinkData(
    DOC, 
    REVIT_FILE_PATH, 
    defaultWorksets_
)

output('{} [{}]'.format(result_.message, result_.status))

# sync changes back to central
if (DOC.IsWorkshared and DEBUG == False):
    output('Syncing to Central: start')
    syncing_ = rFileIO.sync_file (DOC)
    output('Syncing to Central: finished [{}]'.format(syncing_.status))

output('Modifying Revit Link(s).... finished ')
