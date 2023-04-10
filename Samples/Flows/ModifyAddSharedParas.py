'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Add shared parameters to project files.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This flow demonstrates how to add any number of shared parameters to workshared Revit project files.

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

# import from duHast
from duHast.Utilities import FilesIO as fileIO
from duHast.Utilities import Result as res
from duHast.APISamples.SharedParameters import RevitSharedParameterAdd as paraAdd

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
    #get default revit file name
    revitFilePath_ = debugRevitFileName_

# -------------
# my code here:
# -------------

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

def UpDateParameters (doc, data):
    '''
    Bind parameters to category

    :param doc: Current model document
    :type doc: Autodesk.Revit.DB.Document
    :param data: List describing shared parameter to be added. Refer to `listOfParameters_` below
    :type data: [[str, str, ParameterType, bool,[BuiltInCategory],BuiltInParameterGroup, bool],...]

    :return: 
        Result class instance.

        - result.status: Parameters binding status returned in result.status. False if an exception occurred or a parameter bind failed, otherwise True.
        - result.message will contain the names of the shared parameters added.
        - result.result will be an empty list
        
        On exception
        
        - Reload.status (bool) will be False
        - Reload.message will contain the exception message

    :rtype: :class:`.Result`
    '''

    status = res.Result()
    try:
        for parameter_name, group_name, parameter_type, is_visible, element_category, parameter_group, is_instance in data:
            # add parameter to multiple categories if required
            for cat in element_category:
                statusBind =  paraAdd.BindSharedParameter(
                    doc, 
                    cat, 
                    parameter_name, 
                    group_name, 
                    parameter_type, 
                    is_visible, 
                    is_instance, 
                    parameter_group, 
                    shared_parameter_file_path_
                )
                status.Update(statusBind)
    except Exception as e:
        status.UpdateSep(False, 'Terminated with exception: '+ str(e))
    return status

# -------------
# main:
# -------------

# store output here:
rootPath_ = r'C:\temp'

shared_parameter_file_path_ = r'C:\temp\Shared Parameters.txt'
'''
Fully qualified path to shared parameter file
'''

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

list_of_parameters_ = [
    ['ParameterOne','Exported Parameters',rdb.ParameterType.Length, True, [rdb.BuiltInCategory.OST_Ceilings], rdb.BuiltInParameterGroup.PG_GEOMETRY, True],
    ['ParameterTwo','Exported Parameters',rdb.ParameterType.YesNo, True, [rdb.BuiltInCategory.OST_Windows,rdb.BuiltInCategory.OST_CurtainWallPanels, rdb.BuiltInCategory.OST_Walls], rdb.BuiltInParameterGroup.PG_IDENTITY_DATA, True],
    ['ParameterThree','Exported Parameters',rdb.ParameterType.Text, True, [rdb.BuiltInCategory.OST_Rooms], rdb.BuiltInParameterGroup.PG_IDENTITY_DATA, True]
]
'''
List containing the parameters to be added and their properties

    - Parameter Name,
    - parameter group name ( in shared parameter file),
    - the parameter storage type as rdb.ParameterType
    - a list of all categories as rdb.BuiltInCategory the parameter is to be added to 
    - the property group the parameter is to be added to as rdb.BuiltInParameterGroup
    - True if parameter is an instance parameter, False if it is a type parameter

'''

Output('Updating Shared Parameter Data.... start')

result = UpDateParameters (doc, list_of_parameters_)
Output('{} [{}]'.format (result.message,result.status))

# sync changes back to central
if (doc.IsWorkshared and debug_ == False):
    Output('Syncing to Central: start')
    syncing_ = fileIO.SyncFile (doc)
    Output('Syncing to Central: finished [{}] '.format(syncing_.status))

Output('Modifying Revit File.... finished ')