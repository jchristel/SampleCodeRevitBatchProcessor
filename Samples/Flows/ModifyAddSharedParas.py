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
# BSD License
# Copyright © 2023, Jan Christel
# All rights reserved.

# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

# - Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# - Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# - Neither the name of Jan Christel nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
#
# This software is provided by Jan Christel "as is" and any express or implied warranties, including, but not limited to, the implied warranties of merchantability and fitness for a particular purpose are disclaimed. 
# In no event shall Jan Christel be liable for any direct, indirect, incidental, special, exemplary, or consequential damages (including, but not limited to, procurement of substitute goods or services; loss of use, data, or profits; 
# or business interruption) however caused and on any theory of liability, whether in contract, strict liability, or tort (including negligence or otherwise) arising in any way out of the use of this software, even if advised of the possibility of such damage.
#
#
#

# ---------------------------------
# default path locations
# ---------------------------------
# path to library modules
COMMON_LIBRARY_LOCATION = r'C:\temp'
# path to directory containing this script (in case there are any other modules to be loaded from here)
SCRIPT_LOCATION = r'C:\temp'
# debug mode revit project file name
DEBUG_REVIT_FILE_NAME = r'C:\temp\Test_Files.rvt'

import clr
import System

# set path to library and this script
import sys
sys.path += [COMMON_LIBRARY_LOCATION, SCRIPT_LOCATION]

# import from duHast
from duHast.Utilities import files_io as fileIO
from duHast.Utilities.Objects import result as res
from duHast.Revit.SharedParameters import shared_parameter_add as paraAdd

# autodesk API
import Autodesk.Revit.DB as rdb

clr.AddReference('System.Core')
clr.ImportExtensions(System.Linq)

# flag whether this runs in debug or not
DEBUG = False

# Add batch processor scripting references
if not DEBUG:
    import revit_script_util
    import revit_file_util
    clr.AddReference('RevitAPI')
    clr.AddReference('RevitAPIUI')
    # NOTE: these only make sense for batch Revit file processing mode.
    DOC = revit_script_util.GetScriptDocument()
    REVIT_FILE_PATH = revit_script_util.GetRevitFilePath()
else:
    #get default revit file name
    REVIT_FILE_PATH = DEBUG_REVIT_FILE_NAME
    # get document from python shell
    DOC = doc

# -------------
# my code here:
# -------------

def output(message = ''):
    '''
    Output messages either to batch processor (debug = False) or console (debug = True)

    :param message: the message, defaults to ''
    :type message: str, optional
    '''

    if not DEBUG:
        revit_script_util.Output(str(message))
    else:
        print (message)

def update_parameters (doc, data):
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
                statusBind =  paraAdd.bind_shared_parameter(
                    doc, 
                    cat, 
                    parameter_name, 
                    group_name, 
                    parameter_type, 
                    is_visible, 
                    is_instance, 
                    parameter_group, 
                    SHARED_PARAMETER_FILE_PATH
                )
                status.update(statusBind)
    except Exception as e:
        status.update_sep(False, 'Terminated with exception: '+ str(e))
    return status

# -------------
# main:
# -------------

# store output here:
ROOT_PATH = r'C:\temp'

SHARED_PARAMETER_FILE_PATH = r'C:\temp\Shared Parameters.txt'
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

LIST_OF_PARAMETERS = [
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

output('Updating Shared Parameter Data.... start')

RESULT = update_parameters (DOC, LIST_OF_PARAMETERS)
output('{} [{}]'.format (RESULT.message,RESULT.status))

# sync changes back to central
if (DOC.IsWorkshared and DEBUG == False):
    output('Syncing to Central: start')
    SYNCING = fileIO.SyncFile (DOC)
    output('Syncing to Central: finished [{}] '.format(SYNCING.status))

output('Modifying Revit File.... finished ')