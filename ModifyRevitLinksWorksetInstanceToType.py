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

# sample description
# this sample moves revit link types onto the same workset than the corresponding link instance

import clr
import System
import os.path as path

# flag whether this runs in debug or not
debug_ = False

# --------------------------
#d efault file path locations
# --------------------------
# store output here:
rootPath_ = r'C:\temp'
# path to Common.py
commonlibraryDebugLocation_ = r'C:\temp'
# debug mode revit project file name
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
    # get default revit file name
    revitFilePath_ = debugRevitFileName_

# set path to common library
import sys
sys.path.append(commonlibraryDebugLocation_)

# import common library
import CommonRevitAPI as com
import Result as res

clr.AddReference('System.Core')
clr.ImportExtensions(System.Linq)

from Autodesk.Revit.DB import *

# output messages either to batch processor (debug = False) or console (debug = True)
def Output(message = ''):
    if not debug_:
        revit_script_util.Output(str(message))
    else:
        print (message)

# -------------
# my code here:
# -------------

def GetWorksetNamebyId(doc, Id):
    name = 'unknown'
    for p in FilteredWorksetCollector(doc).OfKind(WorksetKind.UserWorkset):
        if(p.Id == Id):
            name = p.Name
            break
    return name
    
    
# returns Revit Link Instance data
def GetRevitInstanceDataByName(revitLinkName, doc):
    match = False
    # default values
    instanceWorksetName = 'unknown'
    for p in FilteredElementCollector(doc).OfClass(RevitLinkInstance):
        # Output('['+str(Element.Name.GetValue(revitLinkName))+'][' + str(Element.Name.GetValue(p))+']')
        linkTypeNameParts = Element.Name.GetValue(p).split(':')
        if(len(linkTypeNameParts) == 3):
            lN = linkTypeNameParts[0]
            if(lN[0:-1] == Element.Name.GetValue(revitLinkName)):
                match = True
                wsparam = p.get_Parameter(BuiltInParameter.ELEM_PARTITION_PARAM)
                instanceWorksetName = wsparam.AsValueString()
                break
    if(match == True):
        # Output(instanceWorksetName)
        return com.GetWorksetIdByName(doc, instanceWorksetName)
    else:
        # Output('no match')
        return ElementId.InvalidElementId

# get the revit link instance data
# this also calls GetRevitLinkInstanceDataByName() 
def ModifyRevitLinkTypeData(revitLink, doc):
    returnvalue = res.Result()
    # get the workset
    wsparam = revitLink.get_Parameter(BuiltInParameter.ELEM_PARTITION_PARAM)
    typeWorksetName = wsparam.AsValueString()
    typeWorksetId = com.GetWorksetIdByName(doc, typeWorksetName)
    instanceWorksetId = GetRevitInstanceDataByName(revitLink, doc)
    instanceWorksetName = GetWorksetNamebyId(doc, instanceWorksetId)
    if(instanceWorksetId!= ElementId.InvalidElementId and instanceWorksetId != typeWorksetId):
        Output('Moving '+ str(Element.Name.GetValue(revitLink)) + ' from ' + str(typeWorksetName) + ' to ' + str(instanceWorksetName))
        transaction = Transaction(doc, "Changing workset of " + str(Element.Name.GetValue(revitLink)))
        returnvalue = com.InTransaction(transaction, com.GetActionChangeElementWorkset(revitLink,instanceWorksetId))
        Output(str(Element.Name.GetValue(revitLink)) + ' ' + str(returnvalue.status))
    else:
        returnvalue.message = str(Element.Name.GetValue(revitLink)) + ' is already on default workset ' + str(instanceWorksetName)
    return returnvalue

# method changing the workset of Revit link types if not on the same workset than the coresponding Revit link instance
def modifyRevitLinkTypes(doc):
    returnvalue = res.Result()
    try:
        for p in FilteredElementCollector(doc).OfClass(RevitLinkType):
            changeLink = ModifyRevitLinkTypeData(p, doc)
            returnvalue.Update(changeLink)
    except Exception as e:
        returnvalue.UpdateSep(False, 'Failed to modify revit link instances with exception: ' + str(e))
    return returnvalue

# -------------
# main:
# -------------

# modify revit links
Output('Modifying Revit Link(s).... start')
result_ = modifyRevitLinkTypes(doc)
Output(str(result_.message) + ' ' + str(result_.status))

# sync changes back to central
if (doc.IsWorkshared and debug_ == False):
    Output('Syncing to Central: start')
    syncing_ = com.SyncFile (doc)
    Output('Syncing to Central: finished ' + str(syncing_.status))
Output('Modifying Revit Link(s).... finished ')
