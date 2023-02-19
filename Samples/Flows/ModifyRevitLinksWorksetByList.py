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

# this sample demonstrates how to move revit link instances and types onto the a workset provided in list below

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
from duHast.APISamples import RevitCommonAPI as com
from duHast.APISamples import RevitWorksets as rWork
from duHast.Utilities import Utility as util
from duHast.Utilities import Result as res

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

def _changeWorkset(doc, el, linkName, fromWorksetName, toWorksetName, toWorksetId, descriptor):
    '''
    Changes the workset of a link instance or link type

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param el: The element of which the workset is to be changed.
    :type el: AutoDesk.Revit.DB.Element
    :param linkName: The link name
    :type linkName: str
    :param fromWorksetName: The current workset name.
    :type fromWorksetName: str
    :param toWorksetName: The new workset name.
    :type toWorksetName: str
    :param toWorksetId: The new workset element id.
    :type toWorksetId: AutoDesk.Revit.DB.ElementId
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

    Output(str(descriptor) + ':: Moving '+ str(linkName) + ' from ' + str(fromWorksetName) + ' to ' + str(toWorksetName))
    transaction = rdb.Transaction(doc, "Changing workset of " + linkName)
    result = com.InTransaction(transaction,  rWork.GetActionChangeElementWorkset(el,toWorksetId))
    Output(linkName + ' ' + str(result.status))
    return result

def _ModifyRevitLinkTypeWorksetName(doc, linkName, workSetName):
    '''
    Modifies a revit link type workset.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param linkName: The link name.
    :type linkName: str
    :param workSetName: The target workset name.
    :type workSetName: str

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
    
    returnValue = res.Result()
    # get the target workset id
    targetWorksetId = rWork.GetWorksetIdByName(doc, workSetName)
    # check if workset still exists
    if(targetWorksetId != rdb.ElementId.InvalidElementId):
        # loop over link types and try to find a match
        for p in rdb.FilteredElementCollector(doc).OfClass(rdb.RevitLinkType):
            linkTypeName = rdb.Element.Name.GetValue(p)
            if (linkTypeName.startswith(linkName)):
                wsparam = p.get_Parameter(rdb.BuiltInParameter.ELEM_PARTITION_PARAM)
                typeWorksetName = wsparam.AsValueString()
                if(typeWorksetName != workSetName):
                    # change the workset of the link type
                    returnValue = _changeWorkset(doc, p, linkTypeName, typeWorksetName, workSetName, targetWorksetId,'Type')
                else:
                    # no need to do anything
                    returnValue.message = 'Type ' + str(util.EncodeAscii(linkTypeName)) + ' is already on default workset ' + str(workSetName)
                break
    else:
        returnValue.UpdateSep(False, 'Workset ' + workSetName + ' does no longer exist in file!')
    return returnValue

def _ModifyRevitLinkInstanceWorkset(doc, linkName, workSetName):
    '''
    Modifies a revit link instance workset.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param linkName: The link instance name.
    :type linkName: str
    :param workSetName: the target workset name.
    :type workSetName: str

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

    returnValue = res.Result()
    # get the target workset id
    targetWorksetId = rWork.GetWorksetIdByName(doc, workSetName)
    # check if workset still exists
    if(targetWorksetId != rdb.ElementId.InvalidElementId):
        # loop over instances and find match
        for p in rdb.FilteredElementCollector(doc).OfClass(rdb.RevitLinkInstance):
            #get the workset
            wsparam = p.get_Parameter(rdb.BuiltInParameter.ELEM_PARTITION_PARAM)
            instanceWorksetName = wsparam.AsValueString()
            lN = "unknown"
            # split revit link name at colon
            linkTypeNameParts = p.Name.split(':')
            if(len(linkTypeNameParts) == 3):
                lN = linkTypeNameParts[0][0:-1]
                linkInstanceNameEncoded = util.EncodeAscii(lN[0:-1])
                if (lN.startswith(linkName)):
                    if (instanceWorksetName != workSetName):
                        # change the workset of the link instance
                        returnValue = _changeWorkset(doc, p, linkInstanceNameEncoded, instanceWorksetName, workSetName, targetWorksetId, 'Instance')
                    else:
                        # no need to do anything
                        returnValue.message = 'Instance ' + linkInstanceNameEncoded + ' is already on default workset ' + str(workSetName)
            else:
                returnValue.UpdateSep(False, 'Failed to split link name into 3 parts')
    else:
        returnValue.UpdateSep(False, 'Workset '+ workSetName + ' does no longer exist in file!')
    return returnValue

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
                    returnValue.Update(changeLinkInstance)
                    changeLinkType = _ModifyRevitLinkTypeWorksetName(doc, linkName, newWorksetName)
                    returnValue.Update(changeLinkType)
                break
        if (match == False):
            Output('Failed to find current Revit file link workset data!')
    except Exception as e:
        returnValue.UpdateSep(False, 'Failed to modify revit link instances with exception: ' + str(e))
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
Output('Modifying Revit Link(s).... start')
result_ = ModifyRevitLinkData(
    doc, 
    revitFilePath_, 
    defaultWorksets_
)

Output(str(result_.message) + str(result_.status))

# sync changes back to central
if (doc.IsWorkshared and debug_ == False):
    Output('Syncing to Central: start')
    syncing_ = com.SyncFile (doc)
    Output('Syncing to Central: finished ' + str(syncing_.status))

Output('Modifying Revit Link(s).... finished ')
