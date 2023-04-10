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
from duHast.Utilities import Result as res
from duHast.APISamples.Exports import RevitExportNavis as rExNavis
from duHast.APISamples.Exports import RevitExportIFC as rExIFC
from duHast.APISamples.Exports.Utility import  IFCCoordinates, IFCSpaceBoundaries

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
    # get default revit file name
    REVIT_FILE_PATH = debugRevitFileName_

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

    if not DEBUG:
        revit_script_util.Output(str(message))
    else:
        print (message)

def ifc_export_view(doc):
    """
    Exports a view to IFC using open source third party IFC exporter supported by Autodesk.

    :param doc: Current model document
    :type doc: Autodesk.Revit.DB.Document

    :return:
        Result class instance.

        - result.status: View export status returned in result.status. False if an exception occurred, otherwise True.
        - result.message: will contain the fully qualified file path of the exported file.
        - result.result: will be an empty list

        On exception

        - reload_status (bool) will be False
        - reload_message will contain the exception message

    :rtype: :class:`.Result`
    """

    return_value = res.Result()
    try:
        ifc_export_option = rExIFC.IFCGetThirdPartyExportConfigByView(doc, rdb.IFCVersion.IFC2x3)
        # exports 3D view where name starts with 'NWCP', Origin is project base point
        return_value = rExIFC.Export3DViewsToIFC(doc, 'NWCP', ifc_export_option, ROOT_PATH, IFCCoordinates.IFCCoords.ProjectBasePoint)
    except Exception as e:
        return_value.UpdateSep(False, 'Failed to export view to IFC with exception{}'.format(e))
    return return_value


def ifc_export_view_default(doc):
    '''
    Exports a view to IFC using the built-in (basic) IFC exporter.

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

    return_value = res.Result()
    try:
        ifc_export_option_default = rExIFC.IFCGetExportConfigByView(rdb.IFCVersion.IFC2x3, IFCSpaceBoundaries.IFCSpaceBoundaries.noBoundaries)
        return_value = rExIFC.Export3DViewsToIFCDefault(doc, 'NWCS', ifc_export_option_default, ROOT_PATH)
    except Exception as e:
        return_value.update_sep(False, 'Failed to export view to IFC with exception{}'.format(e))
    return return_value


def nwc_export_by_view(doc):
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

    return_value = res.Result()
    try:
        nwc_export_option = rExNavis.SetUpNWCDefaultExportOptionSharedByView()
        return_value = rExNavis.Export3DViewsToNWC(doc, 'NWCS', nwc_export_option,  ROOT_PATH)
    except Exception as e:
        return_value.UpdateSep(False, 'Failed to export view to NWC with exception{}'.format(e))
    return return_value


def nwc_export_model(doc):
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

    return_value = res.Result()
    try:
        nwc_export_option = rExNavis.SetUpNWCCustomExportOption(False, True, False, True, False, False, True, False)
        return_value = rExNavis.ExportModelToNWC(doc, nwc_export_option, ROOT_PATH, 'test_project Coords.nwc')
    except Exception as e:
        return_value.UpdateSep(False, 'Failed to export model to NWC with exception{}'.format(e))
    return return_value


# -------------
# main:
# -------------

# store output here:
ROOT_PATH = r'C:\temp'

Output('Exporting.... start')

# export to IFC file format - view
status_export_view = ifc_export_view(DOC)
# export to IFC file format - view but use default out of the box ifc exporter
status_export_ifc_default = ifc_export_view_default(DOC)
status_export_view.Update(status_export_ifc_default)

# nwc by model
status_export_nwc_model = nwc_export_model(DOC)
status_export_view.Update(status_export_nwc_model)

# nwc by view
status_export_nwc_3d_views = nwc_export_by_view(DOC)
status_export_view.Update(status_export_nwc_3d_views)

Output('{} :: [{}]'.format(status_export_view.message, status_export_view.status))

Output('Exporting.... finished ')

