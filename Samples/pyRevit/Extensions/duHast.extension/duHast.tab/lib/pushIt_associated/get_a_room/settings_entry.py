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
from System import Guid

from duHast.Utilities.Objects.result import Result
from duHast.Revit.ExtensibleSchemas.extensible_schemas import create_schema, get_schema, does_schema_exist
from duHast.Revit.ExtensibleSchemas.data_storage import create_project_data_storage, find_data_storage


from pushIt_associated.get_a_room import settings

from Autodesk.Revit.DB.ExtensibleStorage import Entity

def schema_builder(schema_builder):
    """
    Create a field builder for the Get A Room settings schema.
    
    :param schema_builder: The schema builder to use.
    :type schema_builder: Autodesk.Revit.DB.ExtensibleStorage.SchemaBuilder
    
    :return: The schema builder with the fields added.
    :rtype: Autodesk.Revit.DB.ExtensibleStorage.SchemaBuilder
    """
    
    # add a field for the family output directory
    textField = schema_builder.AddSimpleField("FAMILY_OUT_DIRECTORY", clr.GetClrType(str))
    textField.SetDocumentation("The family output directory for the Get A Room add-in.")
    return schema_builder


def setup_schema():
    print("Setting up schema.")
    schema = create_schema(
        "Get_A_Room_Settings",
        None,
        settings.GET_A_ROOM_GUID_ADD_IN_GUID,
        field_builder=schema_builder,
    )
    
    return schema




def get_a_room_settings_entry(doc, uiapp,output, forms):
    # set up a status tracker
    return_value = Result()
    try:
        
        # schema place holder
        schema = None
        data_storage = None
        
        # check if extended storage is set up in the file
        if not does_schema_exist(settings.GET_A_ROOM_GUID_ADD_IN_GUID):
            print("Schema does not exists in the file.")
            # set up the schema in the file
            schema = setup_schema()
            # setup the data storage in the file
            data_storage_result = create_project_data_storage(doc, schema)
            if data_storage_result==False:
                message = "Failed to create data storage: {}".format(data_storage_result.error_message)
                return_value.update_sep(False, message)
                return return_value
            else:
                # get the data storage element
                data_storage = data_storage_result.result[0]
            
        else:
            print("Schema already exists in the file.")
            # get the schema from the file
            schema = get_schema(settings.GET_A_ROOM_GUID_ADD_IN_GUID)
            # get the data storage element from the file
            data_storage = find_data_storage(doc, settings.GET_A_ROOM_GUID_ADD_IN_GUID)
            if data_storage == None:
                message = "Failed to find data storage element in the file."
                return_value.update_sep(False, message)
                print("Data storage element not found in the file.")
                
                data_storage_result = create_project_data_storage(doc, schema)
                print("Data storage result: {}".format(data_storage_result))
                if data_storage_result==False:
                    message = "Failed to create data storage: {}".format(data_storage_result.error_message)
                    return_value.update_sep(False, message)
                    return return_value
                return return_value
                
            else:
                print("Data storage element found in the file.")
            
        # get the current directory of the family output directory
        # set up an entity
        entity = Entity(schema)
        family_output_directory = entity.Get("FAMILY_OUT_DIRECTORY")
        
        if family_output_directory == None:
            print("No family output directory set.")
        
    except Exception as e:
        message = "Failed to update settings: {}".format(e)
        return_value.update_sep(False, message)
        print(message)
    
    return return_value