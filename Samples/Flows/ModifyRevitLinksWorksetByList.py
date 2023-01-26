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
from duHast.APISamples import Utility as util
from duHast.APISamples import Result as res

# autodesk API
from Autodesk.Revit.DB import *

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
    if not debug_:
        revit_script_util.Output(str(message))
    else:
        print (message)

def ChangeWorkset(doc, el, linkName, fromWorksetName, toWorksetName, toWorksetId, descriptor):
    Output(str(descriptor) + ':: Moving '+ str(linkName) + ' from ' + str(fromWorksetName) + ' to ' + str(toWorksetName))
    transaction = Transaction(doc, "Changing workset of " + linkName)
    result = com.InTransaction(transaction,  rWork.GetActionChangeElementWorkset(el,toWorksetId))
    Output(linkName + ' ' + str(result.status))
    return result

def ModifyRevitLinkTypeWorksetName(doc, linkName, workSetName):
    returnValue = res.Result()
    # get the target workset id
    targetWorksetId = rWork.GetWorksetIdByName(doc, workSetName)
    # check if workset still exists
    if(targetWorksetId != ElementId.InvalidElementId):
        # loop over link types and try to find a match
        for p in FilteredElementCollector(doc).OfClass(RevitLinkType):
            linkTypeName = Element.Name.GetValue(p)
            if (linkTypeName.startswith(linkName)):
                wsparam = p.get_Parameter(BuiltInParameter.ELEM_PARTITION_PARAM)
                typeWorksetName = wsparam.AsValueString()
                if(typeWorksetName != workSetName):
                    # change the workset of the link type
                    returnValue = ChangeWorkset(doc, p, linkTypeName, typeWorksetName, workSetName, targetWorksetId,'Type')
                else:
                    # no need to do anything
                    returnValue.message = 'Type ' + str(util.EncodeAscii(linkTypeName)) + ' is already on default workset ' + str(workSetName)
                break
    else:
        returnValue.UpdateSep(False, 'Workset ' + workSetName + ' does no longer exist in file!')
    return returnValue


# get the revit link instance data
def ModifyRevitLinkInstanceWorkset(doc, linkName, workSetName):
    returnValue = res.Result()
    # get the target workset id
    targetWorksetId = rWork.GetWorksetIdByName(doc, workSetName)
    # check if workset still exists
    if(targetWorksetId != ElementId.InvalidElementId):
        # loop over instances and find match
        for p in FilteredElementCollector(doc).OfClass(RevitLinkInstance):
            #get the workset
            wsparam = p.get_Parameter(BuiltInParameter.ELEM_PARTITION_PARAM)
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
                        returnValue = ChangeWorkset(doc, p, linkInstanceNameEncoded, instanceWorksetName, workSetName, targetWorksetId, 'Instance')
                    else:
                        # no need to do anything
                        returnValue.message = 'Instance ' + linkInstanceNameEncoded + ' is already on default workset ' + str(workSetName)
            else:
                returnValue.UpdateSep(False, 'Failed to split link name into 3 parts')
    else:
        returnValue.UpdateSep(False, 'Workset '+ workSetName + ' does no longer exist in file!')
    return returnValue

# method moving revit link instances and types to the same workset as defined in list
def ModifyRevitLinkData(doc, revitFilePath, linkData):
    returnValue = res.Result()
    match = False
    try:
        revitFileName = util.GetFileNameWithoutExt(revitFilePath)
        for fileName, worksetData in linkData:
            if (revitFileName.startswith(fileName)):
                match = True   
                # loop over link data and change link worksets as required
                for linkName, newWorksetName in worksetData:
                    changeLinkInstance = ModifyRevitLinkInstanceWorkset(doc, linkName, newWorksetName)
                    returnValue.Update(changeLinkInstance)
                    changeLinkType = ModifyRevitLinkTypeWorksetName(doc, linkName, newWorksetName)
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
result_ = ModifyRevitLinkData(doc, revitFilePath_, defaultWorksets_)
Output(str(result_.message) + str(result_.status))

# sync changes back to central
if (doc.IsWorkshared and debug_ == False):
    Output('Syncing to Central: start')
    syncing_ = com.SyncFile (doc)
    Output('Syncing to Central: finished ' + str(syncing_.status))

Output('Modifying Revit Link(s).... finished ')
