'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Export views or entire models to IFC or NavisWorks.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This flow demonstrates how to export views or entire models to IFC or NavisWorks.

Note:

- Revit Batch Processor settings:

    - open all worksets to ensure everything required gets exported

- the model will not be saved after the export

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

# import libraries
import Result as res
import RevitExport as rex

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
    # get default revit file name
    revitFilePath_ = debugRevitFileName_

# -------------
# my code here:
# -------------

# output messages either to batch processor (debug = False) or console (debug = True)
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

def IFCExportView(doc):
    '''
    Exports a view to IFC using open source third party IFC exporter supported by Autodesk.

    :param doc: Current model document
    :type doc: Autodesk.Revit.DB.Document

    :return: 
        Result class instance.

        - result.status: View export status returned in result.status. False if an exception occurred, otherwise True.
        - result.message: will contain the fully qualified file path of the exported file.
        - result.result: will be an empty list
        
        On exception
        
        - Reload.status (bool) will be False
        - Reload.message will contain the exception message

    :rtype: :class:`.Result`
    '''

    returnValue = res.Result()
    try:
        ifcExportOption = rex.IFCGetThirdPartyExportConfigByView(doc, rdb.IFCVersion.IFC2x3)
        # exports 3D view where name starts with 'NWCP', Origin is project base point
        returnValue = rex.Export3DViewsToIFC(doc, 'NWCP', ifcExportOption, rootPath_, rex.IFCCoords.ProjectBasePoint)
    except Exception as e:
        returnValue.UpdateSep(False, 'Failed to export view to IFC with exception{}'.format(e))
    return returnValue

def IFCExportViewDefault(doc):
    '''
    Exports a view to IFC using the build in (basic) IFC exporter.

    :param doc: Current model document
    :type doc: Autodesk.Revit.DB.Document

    :return: 
        Result class instance.

        - result.status: View deletion status returned in result.status. False if an exception occurred, otherwise True.
        - result.message: will contain the fully qualified file path of the exported file.
        - result.result: will be an empty list
        
        On exception
        
        - Reload.status (bool) will be False
        - Reload.message will contain the exception message

    :rtype: :class:`.Result`
    '''

    returnValue = res.Result()
    try:
        ifcExportOptionDefault = rex.IFCGetExportConfigByView(rdb.IFCVersion.IFC2x3, rex.IFCSpaceBoundaries.noBoundaries)
        returnValue = rex.Export3DViewsToIFCDefault(doc, 'NWCS', ifcExportOptionDefault,  rootPath_)
    except Exception as e:
        returnValue.UpdateSep(False, 'Failed to export view to IFC with exception{}'.format(e))
    return returnValue

def NWCExportByView(doc):
    '''
    Exports a view as a NavisWorks cache file.

    :param doc: Current model document
    :type doc: Autodesk.Revit.DB.Document

    :return: 
        Result class instance.

        - result.status: View deletion status returned in result.status. False if an exception occurred, otherwise True.
        - result.message: will contain the fully qualified file path of the exported file
        - result.result: will be an empty list
        
        On exception
        
        - Reload.status (bool) will be False
        - Reload.message will contain the exception message

    :rtype: :class:`.Result`
    '''

    returnValue = res.Result()
    try:
        nwcExportOption = rex.SetUpNWCDefaultExportOptionSharedByView()
        returnValue = rex.Export3DViewsToNWC(doc, 'NWCS', nwcExportOption,  rootPath_)
    except Exception as e:
        returnValue.UpdateSep(False, 'Failed to export view to NWC with exception{}'.format(e))
    return returnValue

def NWCExportModel(doc):
    '''
    Exports the entire model as a NavisWorks cache file.

    :param doc: Current model document
    :type doc: Autodesk.Revit.DB.Document

    :return: 
        Result class instance.

        - result.status: View deletion status returned in result.status. False if an exception occurred, otherwise True.
        - result.message: will contain the fully qualified file path of the exported file.
        - result.result: will be an empty list
        
        On exception
        
        - Reload.status (bool) will be False
        - Reload.message will contain the exception message

    :rtype: :class:`.Result`
    '''

    returnValue = res.Result()
    try:
        nwcExportOption = rex.SetUpNWCCustomExportOption(False,True,False,True,False,False,True,False)
        returnValue = rex.ExportModelToNWC(doc, nwcExportOption, rootPath_, 'test_project Coords.nwc')
    except Exception as e:
        returnValue.UpdateSep(False, 'Failed to export model to NWC with exception{}'.format(e))
    return returnValue

# -------------
# main:
# -------------

# store output here:
rootPath_ = r'C:\temp'

Output('Exporting.... start')

# export to IFC file format - view
statusExport_ = IFCExportView(doc)
# export to IFC file format - view but use default out of the box ifc exporter
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