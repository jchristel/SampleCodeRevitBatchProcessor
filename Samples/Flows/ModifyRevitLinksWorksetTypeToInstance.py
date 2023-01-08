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

# this sample demonstrates how to move revit link instances onto the same workset than the corresponding link type

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
import RevitCommonAPI as com
import RevitWorksets as rWork
import Utility as util
import Result as res

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
    #get default revit file name
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

# returns Revit Link Type data
def GetRevitLinkTypeDataByName(revitLinkName, doc):
    # default values
    typeWorksetName = 'unknown'
    for p in FilteredElementCollector(doc).OfClass(RevitLinkType):
        # Output('['+str(revitLinkName)+'][' + str(Element.Name.GetValue(p))+']')
        if (Element.Name.GetValue(p) == revitLinkName):
            wsparam = p.get_Parameter(BuiltInParameter.ELEM_PARTITION_PARAM)
            typeWorksetName = wsparam.AsValueString()
            break
    return rWork.GetWorksetIdByName(doc, typeWorksetName)

# get the revit link instance data
# this also calls GetRevitLinkTypeDataByName() 
def ModifyRevitLinkInstanceData(revitLink, doc):
    returnValue = res.Result()
    #get the workset
    wsparam = revitLink.get_Parameter(BuiltInParameter.ELEM_PARTITION_PARAM)
    instanceWorksetName = wsparam.AsValueString()
    instanceWorksetId = rWork.GetWorksetIdByName(doc, instanceWorksetName)
    lN = "unknown"
    #split revit link name at colon
    linkTypeNameParts = revitLink.Name.split(':')
    if(len(linkTypeNameParts) == 3):
        lN = linkTypeNameParts[0]
        #get the link type data before extension is stripped from the name,
        #strip space of end of name too
        typeWorksetId = GetRevitLinkTypeDataByName(lN[0:-1], doc)
        typeWorksetName = rWork.GetWorksetNameById(doc, typeWorksetId)
        #revit will return a -1 if link is not loaded...
        if(typeWorksetId != ElementId.InvalidElementId):
            linkInstanceNameEncoded = util.EncodeAscii(lN[0:-1])
            if(instanceWorksetId != typeWorksetId):
                Output('Moving '+ str(linkInstanceNameEncoded) + ' from ' + str(instanceWorksetName) + ' to ' + str(typeWorksetName))
                transaction = Transaction(doc, "Changing workset of " + linkInstanceNameEncoded)
                returnValue = com.InTransaction(transaction,  rWork.GetActionChangeElementWorkset(revitLink, typeWorksetId))
                Output(linkInstanceNameEncoded + ' ' + str(returnValue.status))
            else:
               returnValue.message = str(linkInstanceNameEncoded + ' is already on default workset ' + str(typeWorksetName))
        else:
          returnValue.message = str('Link is not loaded' + str(util.EncodeAscii(lN[0:-1])))
    else:
        returnValue.UpdateSep(False, 'Failed to split link name into 3 parts')
    return returnValue

#method moving revit link instances to the same workset as their types
def modifyRevitLinkInstance(doc):
    returnValue = res.Result()
    try:
        for p in FilteredElementCollector(doc).OfClass(RevitLinkInstance):
            changeLink = ModifyRevitLinkInstanceData(p, doc)
            returnValue.Update(changeLink)
    except Exception as e:
        returnValue.UpdateSep(False, 'Failed to modify revit link instances with exception: ' + str(e))
    return returnValue

# -------------
# main:
# -------------

# store output here:
rootPath_ = r'C:\temp'

# modify revit links
Output('Modifying Revit Link(s).... start')
result_ = modifyRevitLinkInstance(doc)
Output(str(result_.message) + ' ' + str(result_.status))

#sync changes back to central
if (doc.IsWorkshared and debug_ == False):
    Output('Syncing to Central: start')
    syncing_ = com.SyncFile (doc)
    Output('Syncing to Central: finished ' + str(syncing_.status))

Output('Modifying Revit Link(s).... finished ')
