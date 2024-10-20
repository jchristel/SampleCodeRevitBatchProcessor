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

from Autodesk.Revit.DB.ExtensibleStorage import AccessLevel, Schema, SchemaBuilder
from System import Guid


def create_schema(
    schema_name,
    schema_documentation,
    string_guid,
    access_level_read=AccessLevel.Public,
    access_level_write=AccessLevel.Public,
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
        # TODO: Create fields
        schema = builder.Finish()
    return schema
