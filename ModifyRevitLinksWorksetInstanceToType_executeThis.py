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

# this sample moves revit link types onto the same workset than the corresponding link instances

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
commonlibraryDebugLocation_ = r'P:\18\1803009.000\Design\BIM\_Revit\5.0 Project Resources\01 Scripts\04 BatchP\_Common'
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

def InTransaction(tranny, action):
    result = None
    tranny.Start()
    try:
        result = action()
        tranny.Commit()
    except Exception as e:
        Output ("exception: " + str(e))
        tranny.RollBack()
    return result

def GetWorksetIdbyName(doc, name):
    id = ElementId.InvalidElementId
    for p in FilteredWorksetCollector(doc).OfKind(WorksetKind.UserWorkset):
        if(p.Name == name):
            id = p.Id
            break
    return id

def GetWorksetNamebyId(doc, Id):
    name = 'unknown'
    for p in FilteredWorksetCollector(doc).OfKind(WorksetKind.UserWorkset):
        if(p.Id == Id):
            name = p.Name
            break
    return name
    
    
#returns Revit Link Type data
def GetRevitInstanceDataByName(revitLinkName, doc):
    match = False
    #default values
    instanceWorksetName = 'unknown'
    for p in FilteredElementCollector(doc).OfClass(RevitLinkInstance):
        #Output('['+str(Element.Name.GetValue(revitLinkName))+'][' + str(Element.Name.GetValue(p))+']')
        linkTypeNameParts = Element.Name.GetValue(p).split(':')
        if(len(linkTypeNameParts) == 3):
            lN = linkTypeNameParts[0]
            if(lN[0:-1] == Element.Name.GetValue(revitLinkName)):
                match = True
                wsparam = p.get_Parameter(BuiltInParameter.ELEM_PARTITION_PARAM)
                instanceWorksetName = wsparam.AsValueString()
                break
    if(match == True):
        #Output(instanceWorksetName)
        return GetWorksetIdbyName(doc, instanceWorksetName)
    else:
        #Output('no match')
        return ElementId.InvalidElementId

#get the revit link instance data
#this also calls GetRevitLinkTypeDataByName() 
def ModifyRevitLinkTypeData(revitLink, doc):
    #get the workset
    wsparam = revitLink.get_Parameter(BuiltInParameter.ELEM_PARTITION_PARAM)
    typeWorksetName = wsparam.AsValueString()
    typeWorksetId = GetWorksetIdbyName(doc, typeWorksetName)
    instanceWorksetId = GetRevitInstanceDataByName(revitLink, doc)
    instanceWorksetName = GetWorksetNamebyId(doc, instanceWorksetId)
    if(instanceWorksetId!= ElementId.InvalidElementId and instanceWorksetId != typeWorksetId):
        Output('Moving '+ str(Element.Name.GetValue(revitLink)) + ' from ' + str(typeWorksetName) + ' to ' + str(instanceWorksetName))
        def action():
            wsparam = revitLink.get_Parameter(BuiltInParameter.ELEM_PARTITION_PARAM)
            wsparam.Set(instanceWorksetId.IntegerValue)
        transaction = Transaction(doc, "Changing workset of " + str(Element.Name.GetValue(revitLink)))
        result = InTransaction(transaction, action)
        Output(str(Element.Name.GetValue(revitLink)) + ' ' + str(result))
    else:
        Output(str(Element.Name.GetValue(revitLink)) + ' is already on default workset ' + str(instanceWorksetName))

#method writing out Revit link information
def writeRevitLinkData(doc):
    status = True
    try:
        for p in FilteredElementCollector(doc).OfClass(RevitLinkType):
            ModifyRevitLinkTypeData(p, doc)
    except Exception as e:
        status = False
        Output('Failed to modify revit link instances!')
        Output (str(e))
    return status

# -------------
# main:
# -------------

#write out revit link data
Output('Modifying Revit Link Data.... start')
result_ = writeRevitLinkData(doc)
Output('Modifying Revit Link.... status: ' + str(result_))
Output('Modifying Revit Link.... finished ')
