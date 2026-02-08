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
from duHast.Revit.ExtensibleSchemas.extensible_schemas_create import verify_schema_data_storage_based
from duHast.Revit.ExtensibleSchemas.data_storage import update_entity_on_data_storage
from duHast.Revit.Views.sheets import get_all_sheets
from duHast.Revit.NetSupport.dll_names import UTILITY,COMMUNITY_TOOLKIT_MVVM,DOC_MANAGER_SETTINGS_UI

from duHast.pyRevit.net_dll_loader import load_net_dll_path, get_bin_path_from_script_path_within_extension
from duHast.pyRevit.console_output import print_header, print_error


from export.docManagerIntegration import settings

DEBUG = True

# .net dlls to load for this script, these need to be in the bin folder of the extension
DLL_LIST = [UTILITY,COMMUNITY_TOOLKIT_MVVM,DOC_MANAGER_SETTINGS_UI]


def schema_builder(schema_builder):
    """
    Create a field builder for the docManager settings schema.
    
    :param schema_builder: The schema builder to use.
    :type schema_builder: Autodesk.Revit.DB.ExtensibleStorage.SchemaBuilder
    
    :return: The schema builder with the fields added.
    :rtype: Autodesk.Revit.DB.ExtensibleStorage.SchemaBuilder
    """
    
    # add a field settings ( this field will contain json formatted settings strings )
    textField_pdf = schema_builder.AddSimpleField(settings.DU_HAST_DOC_MANAGER_SETTINGS_FIELD_NAME, clr.GetClrType(str))
    textField_pdf.SetDocumentation("The json formatted settings string.")

    return schema_builder


def get_sheet_parameter_names(doc):

    """
    Get the parameter names assigned to sheets.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of parameter names assigned to sheets.
    :rtype: List[str]
    """
    
    # get all sheets in the document
    sheets = get_all_sheets(doc)

    parameter_names = List[str]()

    parameter_names_not_ordered =[]
    # get the parameter names from the first sheet
    for sheet in sheets:
        parameters = sheet.GetOrderedParameters()
        for p in parameters:
            parameter_names_not_ordered.append(p.Definition.Name)
       
        break
   
    # order the parameter names
    parameter_names_not_ordered = sorted(parameter_names_not_ordered, key=lambda x: x.lower())

    # add to .net list to be returned
    for name in parameter_names_not_ordered:
        parameter_names.Add(name)

    return parameter_names


def doc_manager_settings_entry(doc, uiapp, output, forms):
    """
    Set up and show the docManager settings UI and save the settings to extended storage in the model.

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

        #set_dll_path_result = load_net_dll_path([PDF_AND_DWG_EXPORTER_SETTINGS_UI]) #"Utils.23.0.0.3.dll",

        if not load_result.status:
            print_error(load_result.message)
            return_value.update_sep(False, load_result.message)
            return return_value

        # check if extensible schema is available
        schema_check_result = verify_schema_data_storage_based(
            doc=doc,
            schema_name=settings.DU_HAST_DOC_MANAGER_SCHEMA_NAME,
            schema_docs=settings.DU_HAST_DOC_MANAGER_SCHEMA_DOCUMENTATION,
            schema_guid=settings.DOC_MANAGER_ADD_IN_GUID,
            field_builder = schema_builder,
        )
        # check if the schema check was successful. if not return the error message
        if schema_check_result.status==False:
            print_error (schema_check_result.message)
            return_value.update(schema_check_result)
            return return_value
        else:
            if DEBUG:
                print(schema_check_result.message)
        
        # get the schema and data storage from the result
        schema_tuple = schema_check_result.result[0]
        schema = schema_tuple[0]
        data_storage = schema_tuple[1]

        # settings place holders
        doc_manager_settings = None
        
        # get the stored entity from the data storage and retrieve settings
        stored_entity = data_storage.GetEntity(schema)
        
        if DEBUG:
            print("...stored entity: [{}]".format(stored_entity))
        
        if stored_entity.IsValid():
            # get the docManager settings from the entity
            doc_manager_settings = stored_entity.Get[str](settings.DU_HAST_DOC_MANAGER_SETTINGS_FIELD_NAME )
            if DEBUG:
                print("...docManager settings from storage: [{}]".format( doc_manager_settings))
            
        else:
            print_error("...invalid Entity: [{}]".format(stored_entity))
            return_value.update_sep(
                False, "Invalid entity: [{}]".format(stored_entity)
            )
            return return_value

        # get the parameters assigned to sheets
        parameter_names = get_sheet_parameter_names(doc)
        
        if DEBUG:
            print("...parameter names assigned to sheets: [{}]".format(parameter_names))
        
        # check if the parameters are empty
        if parameter_names.Count == 0:
            print_error("No parameters assigned to sheets.")
            return_value.update_sep(
                False, "No parameters assigned to sheets."
            )
            return return_value

        # import the UI class from the DocManagerSettingsUI namespace
        from duHastNet.UI.DocManagerSettingsUI import Main
       
        # create an instance of the Main class
        main = Main(doc_manager_settings,  parameter_names)
        
        # show the output window
        export_settings = main.Execute()

        if DEBUG:
            # get the settings from the UI
            print("Document number string: [{}]".format(
                export_settings.DocumentNumberString
                ))
        
        settings_string = export_settings.DocumentNumberString if export_settings.DocumentNumberString else ""
        
        # save the settings in the file
        # Set the fields for docManager settings
        stored_entity.Set(settings.DU_HAST_DOC_MANAGER_SETTINGS_FIELD_NAME, settings_string)
        

        if DEBUG:
            print("...stored pdf settings: [{}]".format(settings_string))
            
        # update the data storage with the new entity and save it to the project information object
        update_entity_result = update_entity_on_data_storage(doc, data_storage, stored_entity)
        
        # check if the settings got stored
        if update_entity_result.status==False:
            message = "Failed to update data storage: {}".format(update_entity_result.message)
            print_error(message)
            return_value.update_sep(False, message)
        else:
            if DEBUG:
                print("...updated data storage: [{}]".format(update_entity_result.message))
        
        settings_verify = stored_entity.Get[str](settings.DU_HAST_DOC_MANAGER_SETTINGS_FIELD_NAME)

        # check if the settings have been stored successfully
        if settings_verify != settings_string:
            message = "Failed to verify settings: [{}]".format(settings_verify)
            print_error(message)
            return_value.update_sep(False, message)
        else:
            message = "Verified settings: [{}]".format(settings_verify)
            return_value.append_message(message)
            if DEBUG:
                print("...verified settings: [{}]".format(settings_verify))

        if DEBUG:
            print("...export settings updated successfully.")

    except Exception as e:
        # handle any exceptions that occur during the export process
        message = "An error occurred while processing export settings: {}".format(e)
        return_value.update_sep(
            False, message
        )
        print_error(message)


    print("\nFinished settings export.")

    return return_value