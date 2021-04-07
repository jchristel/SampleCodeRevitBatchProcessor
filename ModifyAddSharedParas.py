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

# this sample demonstrates how to add shared parameters to project files

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
import CommonRevitAPI as com
import Result as res
import RevitSharedParameterAdd as paraAdd

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

def UpDateParameters (doc, data):
    status = res.Result()
    try:
        for paraName, groupName, paraType, isVisible, elementCategory, paraGroup, isInstance in data:
            # add parameter to multiple categories if requiered
            for cat in elementCategory:
                statusBind =  paraAdd.BindSharedParameter(doc, cat, paraName, groupName, paraType, isVisible, isInstance, paraGroup, sharedParameterFilePath_)
                status.Update(statusBind)
    except Exception as e:
        status.status = False
        status.message = 'Terminated with exception: '+ str(e)
    return status

# -------------
# main:
# -------------

# store output here:
rootPath_ = r'C:\temp'

# fully qualified path to shared parameter file
sharedParameterFilePath_ = r'C:\temp\Shared Parameters.txt'

# list of properties per parameter
# para name - string
# group name - string (in Shared Para file)
# parameter Type (storage type) is an enum
#   refer to for options: https://www.revitapidocs.com/2015/f38d847e-207f-b59a-3bd6-ebea80d5be63.htm
# visible (?) boolean - is the parameter visible
# category(?) to which the parameter will be attached (BuiltInCategory)
# parameter Group (in UI parameters appears under):
            #{"Analysis Results", BuiltInParameterGroup.PG_ANALYSIS_RESULTS},
            #{"Analytical Alignment",BuiltInParameterGroup.PG_ANALYTICAL_ALIGNMENT},
            #{"Analytical Model",BuiltInParameterGroup.PG_ANALYTICAL_MODEL},
            #{"Constraints",BuiltInParameterGroup.PG_CONSTRAINTS},
            #{"Construction", BuiltInParameterGroup.PG_CONSTRUCTION},
            #{"Data",BuiltInParameterGroup.PG_DATA},
            #{"Dimensions",BuiltInParameterGroup.PG_GEOMETRY},
            #{"Electrical",BuiltInParameterGroup.PG_AELECTRICAL},
            #{"Electrical-Circuiting", BuiltInParameterGroup.PG_ELECTRICAL_CIRCUITING},
            #{"Electrical-Lighting", BuiltInParameterGroup.PG_ELECTRICAL_LIGHTING},
            #"Electrical-Loads", BuiltInParameterGroup.PG_ELECTRICAL_LOADS},
            #{"Electrical Engineering",BuiltInParameterGroup.PG_ELECTRICAL},
            #{"Energy Analysis",BuiltInParameterGroup.PG_ENERGY_ANALYSIS},
            #{"Fire Protection",BuiltInParameterGroup.PG_FIRE_PROTECTION},
            #{"General",BuiltInParameterGroup.PG_GENERAL},
            #{"Graphics",BuiltInParameterGroup.PG_GRAPHICS},
            #{"Green Building Properties",BuiltInParameterGroup.PG_GREEN_BUILDING},
            #{"Identity Data",BuiltInParameterGroup.PG_IDENTITY_DATA},
            #{"IFC Parameters",BuiltInParameterGroup.PG_IFC},
            #{"Layers",BuiltInParameterGroup.PG_REBAR_SYSTEM_LAYERS},
            #{"Materials",BuiltInParameterGroup.PG_MATERIALS},
            #{"Mechanical",BuiltInParameterGroup.PG_MECHANICAL},
            #{"Mechanical-Flow",BuiltInParameterGroup.PG_MECHANICAL_AIRFLOW},
            #{"Mechanical-Loads",BuiltInParameterGroup.PG_MECHANICAL_LOADS},
            #{"Model Properties",BuiltInParameterGroup.PG_ADSK_MODEL_PROPERTIES},
            #"Other",BuiltInParameterGroup.INVALID},
            #{"Overall Legend",BuiltInParameterGroup.PG_OVERALL_LEGEND},
            #{"Phasing",BuiltInParameterGroup.PG_PHASING},
            #{"Photometric",BuiltInParameterGroup.PG_LIGHT_PHOTOMETRICS},
            #{"Plumbing",BuiltInParameterGroup.PG_PLUMBING},
            #{"Rebar Set",BuiltInParameterGroup.PG_REBAR_ARRAY},
            #{"Segments and Fittings",BuiltInParameterGroup.PG_SEGMENTS_FITTINGS},
            #{"Slab Shape Edit",BuiltInParameterGroup.PG_SLAB_SHAPE_EDIT},
            #{"Structural",BuiltInParameterGroup.PG_STRUCTURAL},
            #{"Structural Analysis",BuiltInParameterGroup.PG_STRUCTURAL_ANALYSIS},
            #{"Text",BuiltInParameterGroup.PG_TEXT},
            #{"Title Text",BuiltInParameterGroup.PG_TITLE},
            #{"Visibility",BuiltInParameterGroup.PG_VISIBILITY}
# iS Instance - boolean

listOfParameters = [
    ['ParameterOne','Exported Parameters',ParameterType.Length, True, [BuiltInCategory.OST_Ceilings], BuiltInParameterGroup.PG_GEOMETRY, True],
    ['ParameterTwo','Exported Parameters',ParameterType.YesNo, True, [BuiltInCategory.OST_Windows,BuiltInCategory.OST_CurtainWallPanels,BuiltInCategory.OST_Walls], BuiltInParameterGroup.PG_IDENTITY_DATA, True],
    ['ParameterThree','Exported Parameters',ParameterType.Text, True, [BuiltInCategory.OST_Rooms], BuiltInParameterGroup.PG_IDENTITY_DATA, True]
]

Output('Updating Shared Parameter Data.... start')

result = UpDateParameters (doc, listOfParameters)
Output(str(result.message) + '....' + str(result.status))

# sync changes back to central
if (doc.IsWorkshared and debug_ == False):
    Output('Syncing to Central: start')
    syncing_ = com.SyncFile (doc)
    Output('Syncing to Central: finished ' + str(syncing_.status))

Output('Modifying Revit File.... finished ')