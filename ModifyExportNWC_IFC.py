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
# this sample exports a model or 3D view to IFC and NWC files
# batch processor should have enabled:
#    - open all worksets

import clr
import System

# flag whether this runs in debug or not
debug_ = True

# --------------------------
# default file path locations
# --------------------------
# store output here:
rootPath_ = r'C:\temp'
# path to Common.py
commonlibraryDebugLocation_ = r'C:\temp'
# debug mode revit project file name
debugRevitFileName_ = r'C:\temp\Test_Export.rvt'

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

# import common library
import sys
sys.path.append(commonlibraryDebugLocation_)

import Result as res
import RevitExport as rex

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


def IFCExportView(doc):
    returnvalue = res.Result()
    ifcExportOption = rex.IFCGetThirdPartyExportConfifgByView(IFCVersion.IFC2x3)
    # exports 3D view where name starts with 'NWCP', Origin is project base point
    returnvalue = rex.Export3DViewsToIFC(doc, 'NWCP', ifcExportOption, rootPath_, rex.IFCCoords.ProjectBasePoint)
    return returnvalue

def IFCExportViewDefault(doc):
    returnvalue = res.Result()
    ifcExportOptionDefault = rex.IFCGetExportConfifgByView(IFCVersion.IFC2x3, rex.IFCSpaceBoundaries.noBoundaries)
    returnvalue = rex.Export3DViewsToIFCDefault(doc, 'NWCS', ifcExportOptionDefault,  rootPath_)
    return returnvalue

def NWCExportByView(doc):
    returnvalue = res.Result()
    nwcExportOption = rex.SetUpNWCDefaultExportOptionSharedByView()
    returnvalue = rex.Export3DViewsToNWC(doc, 'NWCS', nwcExportOption,  rootPath_)
    return returnvalue

def NWCExportModel(doc):
    returnvalue = res.Result()
    nwcExportOption = rex.SetUpNWCCustomExportOption(False,True,False,True,False,False,True,False)
    returnvalue = rex.ExportModelToNWC(doc, nwcExportOption, rootPath_, 'test_project Coords.nwc')
    return returnvalue

# -------------
# main:
# -------------


Output('Exporting.... start')

# export to IFC file format - view
statusExport_ = IFCExportView(doc)
# export to IFC file format - view but use default ootb ifc exporter
statusExportIFCDefault_ = IFCExportViewDefault(doc)
statusExport_.Update(statusExportIFCDefault_)

# nwc by model
statusExportNWCModel_ = NWCExportModel(doc)
statusExport_.Update(statusExportNWCModel_)

# nwc by view
statusExportNWCThreeDViews_= NWCExportByView(doc)
statusExport_.Update(statusExportNWCThreeDViews_)

Output(statusExport_.message + ' :: ' + str(statusExport_.status))

Output('Exporting.... finished ')
