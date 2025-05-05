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


from Autodesk.Revit.DB.ExtensibleStorage import  Schema
from System import Guid


def does_schema_exist(schema_guid):
    """
    Check if a schema exists in the memory.

    :param schema_guid: The guid of the schema to check
    :type schema_guid: str

    :return: True if the schema exists, False otherwise
    :rtype: bool
    """
    # Look for schema in memory
    schema = Schema.Lookup(Guid(schema_guid))
    # Check if schema exists in the memory or not
    return schema != None


def get_schema(schema_guid):
    """
    Get a schema by its guid.

    :param schema_guid: The guid of the schema to get
    :type schema_guid: str

    :return: The schema if it exists, None otherwise
    :rtype: Autodesk.Revit.DB.ExtensibleStorage.Schema
    """
    
    # Look for schema in memory
    schema = Schema.Lookup(Guid(schema_guid))
    return schema

