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

# import libraries
from duHast.Utilities.Objects import result as res
from duHast.Revit.Exports import export_navis as rExNavis
from duHast.Revit.Exports import export_ifc as rExIFC
from duHast.Revit.Exports.Utility import  ifc_export_coordinates, ifc_export_space_boundaries

# autodesk API
import Autodesk.Revit.DB as rdb

clr.AddReference('System.Core')
clr.ImportExtensions(System.Linq)

# flag whether this runs in debug or not
DEBUG = True

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
    REVIT_FILE_PATH = DEBUG_REVIT_FILE_NAME
    # get document from python shell
    DOC = doc

# -------------
# my code here:
# -------------

# output messages either to batch processor (debug = False) or console (debug = True)
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
        ifc_export_option = rExIFC.ifc_get_third_party_export_config_by_view(doc, rdb.IFCVersion.IFC2x3)
        # exports 3D view where name starts with 'NWCP', Origin is project base point
        return_value = rExIFC.export_3d_views_to_ifc(doc, 'NWCP', ifc_export_option, ROOT_PATH, ifc_export_coordinates.IFCCoords.project_base_point)
    except Exception as e:
        return_value.update_sep(False, 'Failed to export view to IFC with exception{}'.format(e))
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
        ifc_export_option_default = rExIFC.ifc_get_export_config_by_view(rdb.IFCVersion.IFC2x3, ifc_export_space_boundaries.IFCSpaceBoundaries.no_boundaries)
        return_value = rExIFC.export_3d_views_to_ifc_default(doc, 'NWCS', ifc_export_option_default, ROOT_PATH)
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
        nwc_export_option = rExNavis.setup_nwc_default_export_option_shared_by_view()
        return_value = rExNavis.export_3d_views_to_nwc(doc, 'NWCS', nwc_export_option,  ROOT_PATH)
    except Exception as e:
        return_value.update_sep(False, 'Failed to export view to NWC with exception{}'.format(e))
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
        nwc_export_option = rExNavis.setup_nwc_custom_export_option(False, True, False, True, False, False, True, False)
        return_value = rExNavis.export_model_to_nwc(doc, nwc_export_option, ROOT_PATH, 'test_project Coords.nwc')
    except Exception as e:
        return_value.update_sep(False, 'Failed to export model to NWC with exception{}'.format(e))
    return return_value


# -------------
# main:
# -------------

# store output here:
ROOT_PATH = r'C:\temp'

output('Exporting.... start')

# export to IFC file format - view
STATUS_EXPORT_VIEW = ifc_export_view(DOC)
# export to IFC file format - view but use default out of the box ifc exporter
STATUS_EXPORT_IFC_DEFAULT = ifc_export_view_default(DOC)
STATUS_EXPORT_VIEW.update(STATUS_EXPORT_IFC_DEFAULT)

# nwc by model
STATUS_EXPORT_NWC_MODEL = nwc_export_model(DOC)
STATUS_EXPORT_VIEW.update(STATUS_EXPORT_NWC_MODEL)

# nwc by view
STATUS_EXPORT_NWC_3D_VIEWS = nwc_export_by_view(DOC)
STATUS_EXPORT_VIEW.update(STATUS_EXPORT_NWC_3D_VIEWS)

output('{} :: [{}]'.format(STATUS_EXPORT_VIEW.message, STATUS_EXPORT_VIEW.status))

output('Exporting.... finished ')

