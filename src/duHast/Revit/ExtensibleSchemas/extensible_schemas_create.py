"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of functions around Extensible storage in Revit.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2024, Jan Christel
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

from duHast.Revit.Common.adesk_info import VENDOR_ID
from duHast.Revit.ExtensibleSchemas.data_storage_create import create_project_data_storage
from duHast.Revit.ExtensibleSchemas.data_storage import find_data_storage
from duHast.Revit.ExtensibleSchemas.extensible_schemas import does_schema_exist, get_schema

from Autodesk.Revit.DB.ExtensibleStorage import AccessLevel, Schema, SchemaBuilder
from System import Guid


def create_schema(
    schema_name,
    schema_documentation,
    string_guid,
    vendor_id = VENDOR_ID,
    access_level_read=AccessLevel.Public,
    access_level_write=AccessLevel.Public,
    field_builder=None,
):
    """
    Basic schema creation sample (excludes any fields).
    Creates a scheme or returns the already existing scheme with the same guid.

    :param schema_name: The name of the schema
    :type schema_name: str
    :param schema_documentation: A short description of the schema
    :type schema_documentation: str
    :param string_guid: A guid. (unique identifier of this schema)
    :type string_guid: str

    :param access_level_read: Access level to schema for read operations. Default is Public.
    :type access_level_read: Autodesk.Revit.DB.ExtensibleStorage.AccessLevel

    :access_level_write: Access level to schema for write operations. Default is Public
    :access_level_write: Autodesk.Revit.DB.ExtensibleStorage.AccessLevel

    :return: The newly created schema, or existing schema with same guid.
    :rtype: Autodesk.Revit.DB.ExtensibleStorage.Schema
    """

    # check if the schema name contains any spaces or not
    if " " in schema_name:
        raise ValueError("Schema name cannot contain spaces.")
    
    # Look for schema in memory
    schema = Schema.Lookup(Guid(string_guid))
    # Check if schema exists in the memory or not
    if schema == None:
        # Create a schema builder
        schema_guid = Guid(string_guid)
        builder = SchemaBuilder(schema_guid)
        # Set read and write access levels
        builder.SetReadAccessLevel(access_level_read)
        builder.SetWriteAccessLevel(access_level_write)
        # Set name to this schema builder
        builder.SetSchemaName(schema_name)
        builder.SetDocumentation(schema_documentation)
        
        # run the field builder
        if field_builder:
            field_builder(builder)
            
        schema = builder.Finish()
    return schema


def verify_schema_data_storage_based(
    doc, 
    schema_name,
    schema_docs, 
    schema_guid,
    access_level_read=AccessLevel.Public,
    access_level_write=AccessLevel.Public,
    vendor_id = VENDOR_ID, 
    field_builder=None):
    """
    Verify if the schema exists in the file. if not it will attempt to create it and add to data storage element.
    
   
    :return:
        Result class instance.

        - result.status. True if schema was verified or created successfully, otherwise False.
        - result.message will contain messages status messages.
        - result.result tuple (schema,data_storage)

        On exception:

        - result.status (bool) will be False.
        - result.message will contain generic exception message.
        - result.result will be empty

    :rtype: :class:`.Result`
    """

    return_value = Result()
    
    schema = None
    data_storage = None
    
    try:
        # check if extended storage is set up in the file
        if not does_schema_exist(schema_guid):
            return_value.append_message("Schema does not exists in the file.")
            # set up the schema in the file
            schema = create_schema  (
                schema_name=schema_name, 
                schema_documentation=schema_docs, 
                string_guid=schema_guid,
                vendor_id=vendor_id,
                access_level_read=access_level_read,
                access_level_write=access_level_write,
                field_builder=field_builder
            ) 
            
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
            schema = get_schema( schema_guid)
            # get the data storage element from the file
            data_storage = find_data_storage(doc,  schema_guid)
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