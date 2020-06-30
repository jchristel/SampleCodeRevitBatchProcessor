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

import clr
import System
import os.path as path

# flag whether this runs in debug or not
debug = False

# --------------------------
#default file path locations
# --------------------------
#store output here:
rootPath_ = r'P:\18\1803009.000\Design\BIM\_Revit\5.0 Project Resources\01 Scripts\04 BatchP\ReportLinks\_Output'
#path to Common.py
commonlibraryDebugLocation_ = r'P:\18\1803009.000\Design\BIM\_Revit\5.0 Project Resources\01 Scripts\04 BatchP\_Common'
#debug mode revit project file name
debugRevitFileName_ = r'C:\temp\Test_Links.rvt'

# Add batch processor scripting references
if not debug:
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
    if not debug:
        revit_script_util.Output(str(message))
    else:
        print (message)

# -------------
# my code here:
# -------------

#build output file names
fileNameLinkRevit_ = rootPath_ + '\\'+ GetOutPutFileName(revitFilePath_,'.txt', '_RVT')
fileNameLinkCAD_ = rootPath_ + '\\'+ GetOutPutFileName(revitFilePath_,'.txt', '_CAD')

def GetCADLinkTypeDataByName(cadLinkName, doc):
    match = False
    #default values
    modelPath = 'unknown'
    isViewSpecific = False
    ownerViewId = ElementId.InvalidElementId
    for p in FilteredElementCollector(doc).OfClass(CADLinkType):
        if (Element.Name.GetValue(p) == cadLinkName):
            match = True
            try:
                exFileRef = p.GetExternalFileReference()
                if(exFileRef.IsValidExternalFileReference(exFileRef)):
                    modelPath = ModelPathUtils.ConvertModelPathToUserVisiblePath(exFileRef.GetPath())
                    modelPath = ConvertRelativePathToFullPath(modelPath, revitFilePath_)
                break
            except Exception as e:
                Output('CAD link has no external file reference.')
    return modelPath

#get the CAD link instance data
#this also calls GetCADLinkTypeDataByName() 
def extractCADLinkInstanceData(cadLink, doc):
    #get the workset
    wsParam = cadLink.get_Parameter(BuiltInParameter.ELEM_PARTITION_PARAM)
    #get the design option
    doParam = cadLink.get_Parameter(BuiltInParameter.DESIGN_OPTION_ID)
    #get the link name, link type name and shared coordinates (true or false)
    lNameParam = cadLink.get_Parameter(BuiltInParameter.IMPORT_SYMBOL_NAME)
    #get the draw layer
    lDrawLayerParam = cadLink.get_Parameter(BuiltInParameter.IMPORT_BACKGROUND)
    #get shared location?
    #lSharedParam = cadLink.get_Parameter(BuiltInParameter.GEO_LOCATION)
    isViewSpecific= cadLink.ViewSpecific
    ownerViewId = cadLink.OwnerViewId
    linkTypeData = GetCADLinkTypeDataByName(lNameParam.AsString(), doc)
    return '\t'.join([GetOutPutFileName(revitFilePath_), str(cadLink.Id), str(lNameParam.AsString()), str(isViewSpecific), str(ownerViewId), str(wsParam.AsValueString()), str(doParam.AsString()),str(cadLink.Pinned), str(lDrawLayerParam.AsValueString()),linkTypeData, '\n'])

#returns Revit Link Type data
def GetRevitLinkTypeDataByName(revitLinkName, doc):
    match = False
    #default values
    modelPath = 'unknown'
    isLoaded = False
    isFromLocalPath = False
    pathType = 'unknown'
    for p in FilteredElementCollector(doc).OfClass(RevitLinkType):
        if (Element.Name.GetValue(p) == revitLinkName):
            match = True
            isLoaded = p.IsLoaded(doc, p.Id)
            isFromLocalPath = p.IsFromLocalPath()
            exFileRef = p.GetExternalFileReference()
            #get the workset of the link type (this can bew different to the workset of the link instance)
            wsparam = p.get_Parameter(BuiltInParameter.ELEM_PARTITION_PARAM)
            if(exFileRef.IsValidExternalFileReference(exFileRef)):
                modelPath = ModelPathUtils.ConvertModelPathToUserVisiblePath(exFileRef.GetPath())
                modelPath = ConvertRelativePathToFullPath(modelPath, revitFilePath_)
                pathType = exFileRef.PathType.ToString()
            break
    return '\t'.join([str(isLoaded), str(wsparam.AsValueString()), str(isFromLocalPath), pathType, modelPath])

#get the revit link instance data
#this also calls GetRevitLinkTypeDataByName() 
def extractRevitLinkInstanceData(revitLink, doc):
    #get the workset
    wsparam = revitLink.get_Parameter(BuiltInParameter.ELEM_PARTITION_PARAM)
    #get the design option
    doparam = revitLink.get_Parameter(BuiltInParameter.DESIGN_OPTION_ID)
    #get the link name, link type name and shared coordinates (true or false)
    lN = "unknown"
    linkTypeName = "unknown"
    lS = False
    #split revit link name at colon
    linkTypeNameParts = revitLink.Name.split(':')
    if(len(linkTypeNameParts) == 3):
        lN = linkTypeNameParts[0]
        #get the link type data before extension is stripped from the name,
        #strip space of end of name too
        linkTypeData = GetRevitLinkTypeDataByName(lN[0:-1], doc)
        #strip file extension of link name + 1 digit for sapce at end of name
        lN = lN[0:-5] if '.rvt' in lN.lower() else lN
        linkTypeName = linkTypeNameParts[2]
        #check whether link is using shared coordinates positioning
        lS = False if '<not shared>' in linkTypeName.lower() else True
    else:
        Output('Failed to split link name into 3 parts')
    return '\t'.join([GetOutPutFileName(revitFilePath_), str(revitLink.Id), lN, str(lS), linkTypeName, str(wsparam.AsValueString()), str(doparam.AsString()), linkTypeData, '\n'])

#method writing out Revit link information
def writeRevitLinkData(doc, fileName):
    status = True
    try:
        f = open(fileName, 'w')
        f.write('\t'.join(['HOSTFILE' ,'ID', 'LINKNAME', 'SHAREDSITE', 'SHAREDSITENAME', 'INSTANCEWORKSET', 'DESIGNOPTION', 'ISLOADED', 'TYPEWORKSET', 'ISFROMLOCALPATH','PATHTYPE','FILEPATH', '\n']))
        for p in FilteredElementCollector(doc).OfClass(RevitLinkInstance):
            f.write(extractRevitLinkInstanceData(p, doc))
        f.close()
    except Exception as e:
        status = False
        Output('Failed to write data file!' + fileName)
        Output (str(e))
    return status

#method writing out CAD link information
def writeCADLinkData(doc, fileName):
    status = True
    try:
        f = open(fileName, 'w')
        f.write('\t'.join(['HOSTFILE' ,'ID', 'LINKNAME', 'ISVIEWSPECIFIC', 'VIEWID', 'WORKSET', 'DESIGNOPTION','ISPINNED','DRAWLAYER', 'FILEPATH', '\n']))
        for p in FilteredElementCollector(doc).OfClass(ImportInstance):
            f.write(extractCADLinkInstanceData(p, doc))
        f.close()
    except Exception as e:
        status = False
        Output('Failed to write data file!' + fileName)
        Output (str(e))
    return status

# -------------
# main:
# -------------

#write out revit link data
Output('Writing Revit Link Data.... start')
result_ = writeRevitLinkData(doc, fileNameLinkRevit_)
Output('Writing Revit Link.... status: ' + str(result_))
Output('Writing Revit Link.... finished ' + fileNameLinkRevit_)

#write out cad link data
Output('Writing CAD Link Data.... start')
result_ = writeCADLinkData(doc, fileNameLinkCAD_)
Output('Writing CAD Link Data.... status: ' + str(result_))
Output('Writing CAD Link Data.... finished ' + fileNameLinkCAD_)
