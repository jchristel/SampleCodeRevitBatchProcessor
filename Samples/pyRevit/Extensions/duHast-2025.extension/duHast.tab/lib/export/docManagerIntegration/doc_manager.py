# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2025, Jan Christel
# All rights reserved.

# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

# - Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# - Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# - Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
#
# This software is provided by the copyright holder "as is" and any express or implied warranties, including, but not limited to, the implied warranties of merchantability and fitness for a particular purpose are disclaimed.
# In no event shall the copyright holder be liable for any direct, indirect, incidental, special, exemplary, or consequential damages (including, but not limited to, procurement of substitute goods or services; loss of use, data, or profits;
# or business interruption) however caused and on any theory of liability, whether in contract, strict liability, or tort (including negligence or otherwise) arising in any way out of the use of this software, even if advised of the possibility of such damage.
#
#
#

import clr
import os
import sys

from System.Collections.Generic import List

from duHast.Utilities.Objects.result import Result
from duHast.Revit.ExtensibleSchemas.extensible_schemas import does_schema_exist
from duHast.Revit.Views.sheets import get_all_sheets
from duHast.Revit.NetSupport.dll_names import UTILITY,COMMUNITY_TOOLKIT_MVVM,DOC_MANAGER_UI

from duHast.pyRevit.net_dll_loader import load_net_dll_path, get_bin_path_from_script_path_within_extension
from duHast.pyRevit.console_output import print_header, print_error

from export.docManagerIntegration.settings_utils import get_name_settings_from_schema
from export.docManagerIntegration.docIntutils.revision_data_factory import get_revision_data
from export.docManagerIntegration import settings

DEBUG = True

# .net dlls to load for this script, these need to be in the bin folder of the extension
DLL_LIST = [UTILITY,COMMUNITY_TOOLKIT_MVVM,DOC_MANAGER_UI]


def doc_manager_entry(doc, uiapp, output, forms):
    """
    Set up and show the docManager  UI.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param uiapp: The Revit UI application.
    :type uiapp: Autodesk.Revit.UI.UIApplication
    :param output: pyRevit output.
    :type output: pyRevit.output
    :param forms: pyRevit forms.
    :type forms: pyRevit.forms
    :return: Result object with status and message.
    :rtype: Result
    """

    # set up a status tracker
    return_value = Result()

    try:

        print_header("Starting ...")
        # get the bin directory for the extension, this is where the required dlls should be located
        bin_directory = get_bin_path_from_script_path_within_extension(__file__)   
        if bin_directory is None:
            message = "Failed to determine bin directory for dlls."
            print_error(message)
            return_value.update_sep(False, message)
            return return_value

        # load the required dlls for the UI
        load_result = load_net_dll_path(DLL_LIST, bin_directory=bin_directory, exact_match=True)
        print(load_result.message)

        if not load_result.status:
            print_error(load_result.message)
            return_value.update_sep(False, load_result.message)
            return return_value

        # check if extensible schema exists
        if not does_schema_exist(settings.DOC_MANAGER_ADD_IN_GUID):
            message = "Cant find any settings for this file. Please run the settings add-in first."
            return_value.update_sep(False, message)
            print_error(message)
            return return_value
        
        print_header("Starting ...")
        
        # settings place holders
        doc_manager_settings = None
        
        # get the output directory from the schema
        settings_getter_result = get_name_settings_from_schema(doc=doc)
        if settings_getter_result.status is False:
            message = "It looks like there are export settings stored in this file. Run set up first.\n... {}".format(settings_getter_result.message)
            return_value.update_sep(False, message)
            print_error(message)
            return return_value
        else:
            # get the rename settings from the schema
            doc_manager_settings = settings_getter_result.result[0]
            if DEBUG:
                print_header("Got settings")
                print("... settings: [{}]".format(doc_manager_settings))

        # import the UI class from the DocManagerSettingsUI namespace
        from duHastNet.UI.DocManagerUI.Models.Revit import RevitDataModel
              
        revit_data_model = RevitDataModel(doc.Title, doc_manager_settings)

        if DEBUG:
            print("data model: model name: {}".format(revit_data_model.ModelName))
            print("data model: settings: {}".format(revit_data_model.SettingsAsJson))


        # get revisions from model:
        revision_data_status = get_revision_data(doc, revit_data_model)
        if not revision_data_status.status:
            message = "Failed to get revision data from model. Error: {}".format(revision_data_status.message)
            return_value.update_sep(False, message)
            print_error(message)
            return return_value
    
        # get the updated data model with revisions added
        revision_data_model = revision_data_status.result[0]


    except Exception as e:
        # handle any exceptions that occur during the export process
        message = "An error occurred while running doc manager: {}".format(e)
        return_value.update_sep(
            False, message
        )
        print_error(message)


    print("\nFinished.")

    return return_value