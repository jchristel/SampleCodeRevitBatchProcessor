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

# this sample moves revit link instances onto a workset specified in list

import clr
import System
import os.path as path

# flag whether this runs in debug or not
debug_ = False

# --------------------------
#default file path locations
# --------------------------
#store output here:
rootPath_ = r'C:\temp'
#path to Common.py
commonlibraryDebugLocation_ = r'C:\temp'
#debug mode revit project file name
debugRevitFileName_ = r'C:\temp\Test_Links.rvt'

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
    #get default revit file name
    revitFilePath_ = debugRevitFileName_

#set path to common library
import sys
sys.path.append(commonlibraryDebugLocation_)

#import common library
import Common
from Common import *

clr.AddReference('System.Core')
clr.ImportExtensions(System.Linq)

from Autodesk.Revit.DB import *

#output messages either to batch processor (debug = False) or console (debug = True)
def Output(message = ''):
    if not debug_:
        revit_script_util.Output(str(message))
    else:
        print (message)

# -------------
# my code here:
# -------------

def GetWorksetIdbyName(doc, name):
    id = ElementId.InvalidElementId
    for p in FilteredWorksetCollector(doc).OfKind(WorksetKind.UserWorkset):
        if(p.Name == name):
            id = p.Id
            break
    return id

#helper changing the workset of an element
def ChangeWorkset(doc, el, linkName, fromWorksetName, toWorksetName, toWorksetId, descriptor):
    Output(str(descriptor) + ':: Moving '+ str(linkName) + ' from ' + str(fromWorksetName) + ' to ' + str(toWorksetName))
    def action():
        wsparam = el.get_Parameter(BuiltInParameter.ELEM_PARTITION_PARAM)
        wsparam.Set(toWorksetId.IntegerValue)
    transaction = Transaction(doc, "Changing workset of " + linkName)
    result = InTransaction(transaction, action)
    Output(linkName + ' ' + str(result))
    return result

#modifies revit link type workset
def ModifyRevitLinkTypeWorksetName(doc, linkName, workSetName):
    #get the target workset id
    targetWorksetId = GetWorksetIdbyName(doc, workSetName)
    match = False
    #check if workset still exists
    if(targetWorksetId != ElementId.InvalidElementId):
        #loop over link types and try to find a match
        for p in FilteredElementCollector(doc).OfClass(RevitLinkType):
            linkTypeName = Element.Name.GetValue(p)
            if (linkTypeName.startswith(linkName)):
                match = True
                wsparam = p.get_Parameter(BuiltInParameter.ELEM_PARTITION_PARAM)
                typeWorksetName = wsparam.AsValueString()
                if(typeWorksetName != workSetName):
                    #change the workset of the link type
                    ChangeWorkset(doc, p, linkTypeName, typeWorksetName, workSetName, targetWorksetId,'Type')
                else:
                    #no need to do anything
                    Output('Type ' + str(EncodeAscii(linkTypeName)) + ' is already on default workset ' + str(workSetName))
                break
    else:
        Output('Workset '+ workSetName + ' does no longer exist in file!')
    return match


#modifies revit link instance workset
def  ModifyRevitLinkInstanceWorkset(doc, linkName, workSetName):
    #get the target workset id
    targetWorksetId = GetWorksetIdbyName(doc, workSetName)
    match = False
    #check if workset still exists
    if(targetWorksetId != ElementId.InvalidElementId):
        #loop over instances and find match
        for p in FilteredElementCollector(doc).OfClass(RevitLinkInstance):
            #get the workset
            wsparam = p.get_Parameter(BuiltInParameter.ELEM_PARTITION_PARAM)
            instanceWorksetName = wsparam.AsValueString()
            lN = "unknown"
            #split revit link name at colon
            linkTypeNameParts = p.Name.split(':')
            if(len(linkTypeNameParts) == 3):
                lN = linkTypeNameParts[0][0:-1]
                linkInstanceNameEncoded = EncodeAscii(lN[0:-1])
                if (lN.startswith(linkName)):
                    match = True
                    if (instanceWorksetName != workSetName):
                        #change the workset of the link instance
                        ChangeWorkset(doc, p, linkInstanceNameEncoded, instanceWorksetName, workSetName, targetWorksetId, 'Instance')
                    else:
                        #no need to do anything
                        Output('Instance ' + linkInstanceNameEncoded + ' is already on default workset ' + str(workSetName))
            else:
                Output('Failed to split link name into 3 parts')
    else:
        Output('Workset '+ workSetName + ' does no longer exist in file!')
    return match

#method moving revit link instances and types to the same workset as defined in list
def ModifyRevitLinkData(doc, revitFilePath, linkData):
    status = True
    try:
        revitFileName = GetRevitFileName(revitFilePath)
        for fileName, worksetData in linkData:
            if (revitFileName.startswith(fileName)):
                flag = True
                #loop over link data and change link worksets as required
                for linkName, newWorksetName in worksetData:
                    status = status & ModifyRevitLinkInstanceWorkset(doc, linkName, newWorksetName)
                    status = status & ModifyRevitLinkTypeWorksetName(doc, linkName, newWorksetName)
    except Exception as e:
        status = False
        Output('Failed to modify revit link instances!')
        Output (str(e))
    return status

# -------------
# main:
# -------------

#list containing the default worksets for links in format:
# [[revit host file name],[[Link file name, workset name],[link file name, workset name]]
defaultWorksets_ = [
['Revit file name', [['Link Name','Workset Name'],['Link Name','Workset Name']]]
]

#write out revit link data
Output('Modifying Revit Link Data.... start')
result_ = ModifyRevitLinkData(doc, revitFilePath_, defaultWorksets_)
Output('Modifying Revit Link.... status: ' + str(result_))

#sync changes back to central
if (doc.IsWorkshared and debug_ == False):
    Output('Syncing to Central: start')
    SyncFile (doc)
    Output('Syncing to Central: finished')

Output('Modifying Revit Link.... finished ')
