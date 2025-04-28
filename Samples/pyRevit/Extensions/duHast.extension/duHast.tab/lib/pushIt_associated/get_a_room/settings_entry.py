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

from duHast.Utilities.Objects.result import Result
from duHast.Revit.ExtensibleSchemas.extensible_schemas import create_schema, get_schema, does_schema_exist
from duHast.Revit.ExtensibleSchemas.data_storage import create_project_data_storage, find_data_storage, update_entity_on_data_storage
from duHast.pyRevit.directory_picker import get_process_directory
from duHast.pyRevit.console_output import print_error, print_header

from pushIt_associated.get_a_room import settings


# set up some options for the user to select
YES = "Yes"
NO_GET_ME_OUT_OF_HERE = "Oh No, Get me out of here!"

def schema_builder(schema_builder):
    """
    Create a field builder for the Get A Room settings schema.
    
    :param schema_builder: The schema builder to use.
    :type schema_builder: Autodesk.Revit.DB.ExtensibleStorage.SchemaBuilder
    
    :return: The schema builder with the fields added.
    :rtype: Autodesk.Revit.DB.ExtensibleStorage.SchemaBuilder
    """
    
    # add a field for the family output directory
    textField = schema_builder.AddSimpleField(settings.DU_HAST_GET_A_ROOM_FAMILY_OUT_DIRECTORY_FIELD_NAME, clr.GetClrType(str))
    textField.SetDocumentation("The family output directory for the Get A Room add-in.")
    return schema_builder


def get_user_options(forms):
    """
    Gets the user options for saving the family output directory.

    Options are: YES or NO_GET_ME_OUT_OF_HERE

    :param forms: the forms object
    :type forms: Forms
    :return: the user options
    :rtype: dict
    """

    # ask user for single directory or directory by category
    # and if existing families are to be ignored
    ops = [YES,NO_GET_ME_OUT_OF_HERE]
    configs = {
        YES: {"background": "#FF0000"},
        NO_GET_ME_OUT_OF_HERE : {"background": "#00FF00"},
    }
    ui_options = forms.CommandSwitchWindow.show(
        ops,  message="Do you want to update the family directory ?", config=configs
    )

    return ui_options


def setup_schema():
    """
    Set up the schema for the Get A Room settings add-in.
    
    :return: The schema for the Get A Room settings add-in.
    :rtype: Autodesk.Revit.DB.ExtensibleStorage.Schema
    """
    
    schema = create_schema(
        schema_name="Get_A_Room_Settings",
        schema_documentation= "This schema contains settings for the get a room add in.",
        string_guid = settings.GET_A_ROOM_ADD_IN_GUID,
        field_builder=schema_builder,
    )
    
    return schema


def verify_schema(doc):
    """
    Verify if the schema exists in the file. if not it will attempt to create it.
    
    :return: True if the schema exists, False otherwise.
    :rtype: bool
    """
    return_value = Result()
    
    schema = None
    data_storage = None
    
    try:
        # check if extended storage is set up in the file
        if not does_schema_exist(settings.GET_A_ROOM_ADD_IN_GUID):
            return_value.append_message("Schema does not exists in the file.")
            # set up the schema in the file
            schema = setup_schema()
            
            # setup the data storage in the file
            data_storage_result = create_project_data_storage(doc, schema)
            if data_storage_result==False:
                message = "Failed to create data storage: {}".format(data_storage_result.message)
                return_value.update_sep(False, message)
                return return_value
            else:
                # get the data storage element
                data_storage = data_storage_result.result[0]
        else:
            return_value.append_message("Schema exists in the file.")
            # get the schema from the file
            schema = get_schema(settings.GET_A_ROOM_ADD_IN_GUID)
            # get the data storage element from the file
            data_storage = find_data_storage(doc, settings.GET_A_ROOM_ADD_IN_GUID)
            if data_storage == None:
                return_value.append_message("Data storage element not found in the file. Attempting to create it.")
                
                # attempt to create the data storage element
                data_storage_result = create_project_data_storage(doc, schema)
                if data_storage_result==False:
                    message = "Failed to create data storage: {}".format(data_storage_result.message)
                    return_value.update_sep(False, message)
                    return return_value
                else:
                    return_value.append_message("Data storage element created in the file.")
                    # get the data storage element
                    data_storage = data_storage_result.result[0]
            else:
                return_value.append_message("Data storage element found in the file.")
                
        # add the schema and data storage to the return value as a tuple
        return_value.result.append((schema,data_storage))
        
    except Exception as e:
        message = "Failed to set up schema: {}".format(e)
        return_value.update_sep(False, message)
    
    return return_value


def get_a_room_settings_entry(doc, uiapp, output, forms):
    """
    Entry for the Get A Room settings add-in.
    
    :param doc: The Revit document.
    :type doc: Autodesk.Revit.DB.Document
    :param uiapp: The Revit UI application.
    :type uiapp: Autodesk.Revit.UI.UIApplication
    :param output: The pyRevit output object.
    :type output: pyRevit.output.Output
    :param forms: The forms object.
    :type forms: Forms
    
    :return: The result of the operation.
    :rtype: Result
    """
    
    # set up a status tracker
    return_value = Result()
    try:
        # output a header to the console
        print_header("Get A Room Settings Entry")
        
        schema_check_result = verify_schema(doc)
        # check if the schema check was successful. if not return the error message
        if schema_check_result.status==False:
            print_error (schema_check_result.message)
            return_value.update(schema_check_result)
            return return_value
        
        # get the schema and data storage from the result
        schema_tuple = schema_check_result.result[0]
        schema = schema_tuple[0]
        data_storage = schema_tuple[1]
        
        stored_entity = data_storage.GetEntity(schema)
        if stored_entity.IsValid():
            # get the output directory from the entity
            family_output_directory = stored_entity.Get[str](settings.DU_HAST_GET_A_ROOM_FAMILY_OUT_DIRECTORY_FIELD_NAME)
            print("...Family output directory: [{}]".format(family_output_directory))
        else:
            print_error("...invalid Entity: [{}]".format(stored_entity))
        
        if family_output_directory == None or family_output_directory == "":
            print("...No family output directory set.")
        
        # get user options for saving the family output directory
        user_selection = get_user_options(forms)

        # check if user selection is valid
        if user_selection == None or user_selection == NO_GET_ME_OUT_OF_HERE:
            return_value.update_sep(False, "User cancelled operation")
            print_error("User cancelled operation")
            return return_value
      
        # get a new directory from the user
        directory_result = get_process_directory(
            forms=forms,
            form_title="Select Family Output Directory",
        )
        
        # check if the user selected a directory
        if directory_result.status==False:
            message = "Failed to get family output directory: {}".format(directory_result.message)
            print_error(message)
            return_value.update_sep(False, message)
            return return_value
        
        # get the actual directory from the result
        new_directory = directory_result.result[0]
        
        # Set the FAMILY_OUT_DIRECTORY value on the entity
        stored_entity.Set(settings.DU_HAST_GET_A_ROOM_FAMILY_OUT_DIRECTORY_FIELD_NAME, new_directory)

        # update the data storage with the new entity and save it to the project information object
        update_entity_result = update_entity_on_data_storage(doc, data_storage, stored_entity)
        
        # check if the user selected a directory
        if update_entity_result.status==False:
            message = "Failed to update data storage: {}".format(update_entity_result.message)
            print_error(message)
            return_value.update_sep(False, message)
            return return_value
        
        print("...Family output directory updated to: [{}]".format(update_entity_result.message))
        
        # Retrieve it to verify
        family_output_directory_updated = stored_entity.Get[str](settings.DU_HAST_GET_A_ROOM_FAMILY_OUT_DIRECTORY_FIELD_NAME)
        
        # check if update was successful
        if family_output_directory_updated == new_directory:
            print("...Confirmed: family output directory updated to: [{}]".format(family_output_directory_updated))
            return_value.update_sep(True, "Family output directory updated to: [{}]".format(family_output_directory_updated))
        else:
            message = "Failed to update family output directory"
            print_error(message)
            return_value.update_sep(False, message)
        
    except Exception as e:
        message = "Failed to update settings: {}".format(e)
        return_value.update_sep(False, message)
        print_error(message)
    
    
    print("Get A Room settings entry completed.")
    # close the output window after 5 seconds
    output.self_destruct(5)
    return return_value