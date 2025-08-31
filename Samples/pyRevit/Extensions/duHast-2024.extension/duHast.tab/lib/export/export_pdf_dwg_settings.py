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
from duHast.Revit.NetSupport.dll_names import PDF_AND_DWG_EXPORTER_SETTINGS_UI

from duHast.pyRevit.net_dll_loader import load_net_dll_path
from duHast.pyRevit.console_output import print_header, print_error


from export import settings

DEBUG = False


from Autodesk.Revit.DB import  BaseExportOptions

def get_all_dwg_export_options(doc):
    """
    Retrieves all DWG export options.

    :param doc: The Revit document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A list of DWG export options.
    :rtype: list
    """

    # Get the export option names
    setup_names = BaseExportOptions.GetPredefinedSetupNames(doc)

    return setup_names

def schema_builder(schema_builder):
    """
    Create a field builder for the export pdf and dwg settings schema.
    
    :param schema_builder: The schema builder to use.
    :type schema_builder: Autodesk.Revit.DB.ExtensibleStorage.SchemaBuilder
    
    :return: The schema builder with the fields added.
    :rtype: Autodesk.Revit.DB.ExtensibleStorage.SchemaBuilder
    """
    
    # add a field for the pdf name settings
    textField_pdf = schema_builder.AddSimpleField(settings.DU_HAST_EXPORTER_PDF_SETTING_FIELD_NAME, clr.GetClrType(str))
    textField_pdf.SetDocumentation("The json formatted pdf export name settings string.")

    # add a field for the dwg name settings
    textField_dwg = schema_builder.AddSimpleField(settings.DU_HAST_EXPORTER_DWG_SETTING_FIELD_NAME, clr.GetClrType(str))
    textField_dwg.SetDocumentation("The json formatted dwg export name settings string.")

    # add a field for the dwg export scheme name settings
    textField_dwg = schema_builder.AddSimpleField(settings.DU_HAST_EXPORTER_DWG_SCHEME_NAME_SETTING_FIELD_NAME, clr.GetClrType(str))
    textField_dwg.SetDocumentation("The dwg export scheme name.")
    
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



def settings_export_pdf_dwg_entry(doc, output, forms):
    """
    Exports sheets to pdf and dwg files.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
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
        set_dll_path_result = load_net_dll_path([PDF_AND_DWG_EXPORTER_SETTINGS_UI]) #"Utils.23.0.0.3.dll",

        if not set_dll_path_result.status:
            print_error(set_dll_path_result.message)


        # check if extensible schema is available
        schema_check_result = verify_schema_data_storage_based(
            doc=doc,
            schema_name=settings.DU_HAST_EXPORTER_PDF_SETTING_SCHEMA_NAME,
            schema_docs=settings.DU_HAST_EXPORTER_PDF_SETTING_SCHEMA_DOCUMENTATION,
            schema_guid=settings.EXPORTER_ADD_IN_GUID,
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
        pdf_settings = None
        dwg_settings = None

        dwg_export_scheme_name = "test"

        # get the stored entity from the data storage and retrieve settings
        stored_entity = data_storage.GetEntity(schema)
        
        if DEBUG:
            print("...stored entity: [{}]".format(stored_entity))
        
        if stored_entity.IsValid():
            # get the pdf name settings from the entity
            pdf_settings = stored_entity.Get[str](settings.DU_HAST_EXPORTER_PDF_SETTING_FIELD_NAME)
            if DEBUG:
                print("...pdf settings from storage: [{}]".format( pdf_settings))
            # get the dwg name settings from the entity
            dwg_settings = stored_entity.Get[str](settings.DU_HAST_EXPORTER_DWG_SETTING_FIELD_NAME)
            if DEBUG:
                print("...dwg settings from storage: [{}]".format( dwg_settings))
            # get the dwg export scheme name from the entity
            dwg_export_scheme_name=stored_entity.Get[str](settings.DU_HAST_EXPORTER_DWG_SCHEME_NAME_SETTING_FIELD_NAME)
            if DEBUG:
                print("...dwg export scheme settings from storage: [{}]".format( dwg_settings))
        else:
            print_error("...invalid Entity: [{}]".format(stored_entity))
            return_value.update_sep(
                False, "Invalid entity: [{}]".format(stored_entity)
            )
            return return_value
        
        # get the dwg export options names in the model ( this is a .net list of strings )
        dwg_export_scheme_names = get_all_dwg_export_options(doc)

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

        # import the UI class from the PDFDWGExporterUI namespace
        from duHastNet.UI.PDFDWGExporterUI import Main
       
        # create an instance of the Main class
        main = Main(pdf_settings, dwg_settings, parameter_names,dwg_export_scheme_names, dwg_export_scheme_name)
        # show the output window
        export_settings = main.Execute()

        if DEBUG:
            # get the settings from the UI
            print("pdf settings: {}\nDWG settings: {}\nDWG Export scheme: [{}]".format(
                export_settings.PDFRenameString, 
                export_settings.DWGRenameString, 
                export_settings.DWGExportScheme))
        
        pdf_string = export_settings.PDFRenameString if export_settings.PDFRenameString else ""
        dwg_string = export_settings.DWGRenameString if export_settings.DWGRenameString else ""
        dwg_export_scheme_name = export_settings.DWGExportScheme if export_settings.DWGExportScheme else ""
        
        # save the settings in the file
        # Set the fields for dwg and pdf settings
        stored_entity.Set(settings.DU_HAST_EXPORTER_PDF_SETTING_FIELD_NAME, pdf_string)
        stored_entity.Set(settings.DU_HAST_EXPORTER_DWG_SETTING_FIELD_NAME, dwg_string)
        stored_entity.Set(settings.DU_HAST_EXPORTER_DWG_SCHEME_NAME_SETTING_FIELD_NAME, dwg_export_scheme_name)

        if DEBUG:
            print("...stored pdf settings: [{}]".format(pdf_string))
            print("...stored dwg settings: [{}]".format(dwg_string))
            print("...stored dwg export scheme settings: [{}]".format(dwg_export_scheme_name))
            
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
        
        pdf_verify = stored_entity.Get[str](settings.DU_HAST_EXPORTER_PDF_SETTING_FIELD_NAME)
        dwg_verify = stored_entity.Get[str](settings.DU_HAST_EXPORTER_DWG_SETTING_FIELD_NAME)
        dwg_scheme_verify = stored_entity.Get[str](settings.DU_HAST_EXPORTER_DWG_SCHEME_NAME_SETTING_FIELD_NAME)

        # check if the pdf name settings name have been stored successfully
        if pdf_verify != pdf_string:
            message = "Failed to verify pdf settings: [{}]".format(pdf_verify)
            print_error(message)
            return_value.update_sep(False, message)
        else:
            message = "Verified pdf settings: [{}]".format(pdf_verify)
            return_value.append_message(message)
            if DEBUG:
                print("...verified pdf settings: [{}]".format(pdf_verify))

        # check if the dwg name settings name have been stored successfully
        if dwg_verify != dwg_string:
            message = "Failed to verify dwg settings: [{}]".format(dwg_verify)
            print_error(message)
            return_value.update_sep(False, message)
        else:
            message = "Verified dwg settings: [{}]".format(dwg_verify)
            return_value.append_message(message)
            if DEBUG:
                print("...verified dwg settings: [{}]".format(dwg_verify))
    
        # check if the export scheme name has been stored successfully
        if dwg_scheme_verify != dwg_export_scheme_name:
            message = "Failed to verify dwg export scheme settings: [{}]".format(dwg_scheme_verify)
            print_error(message)
            return_value.update_sep(False, message)
        else:
            message = "Verified dwg export scheme settings: [{}]".format(dwg_scheme_verify)
            return_value.append_message(message)
            if DEBUG:
                print("...verified dwg export scheme settings: [{}]".format(dwg_scheme_verify))

        if DEBUG:
            print("...export settings updated successfully.")
        return return_value

    except Exception as e:
        # handle any exceptions that occur during the export process
        message = "An error occurred while processing export settings: {}".format(e)
        return_value.update_sep(
            False, message
        )
        print_error(message)


    print("\nFinished pdf and dwg export settings.")

    return return_value