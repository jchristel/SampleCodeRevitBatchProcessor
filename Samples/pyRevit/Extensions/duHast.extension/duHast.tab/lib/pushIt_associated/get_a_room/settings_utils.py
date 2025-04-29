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
from duHast.Revit.ExtensibleSchemas.extensible_schemas import get_schema
from duHast.Revit.ExtensibleSchemas.data_storage import find_data_storage

from pushIt_associated.get_a_room import settings

def get_output_path_from_schema(doc):
    """
    Get the output path from the schema in the document.
    
    This function retrieves the output path from the schema associated with the document.
    
    :param doc: The Revit document to retrieve the output path from.
    :type doc: Autodesk.Revit.DB.Document
    :return: A Result object containing the output path or an error message.
    :rtype: Result
    """
    # set up a status tracker
    return_value = Result()
    try:
        schema = get_schema(settings.GET_A_ROOM_ADD_IN_GUID)
        data_storage = find_data_storage(doc, settings.GET_A_ROOM_ADD_IN_GUID)
        stored_entity = data_storage.GetEntity(schema)
        if stored_entity.IsValid():
            # get the output directory from the entity
            family_output_directory = stored_entity.Get[str](settings.DU_HAST_GET_A_ROOM_FAMILY_OUT_DIRECTORY_FIELD_NAME)
            return_value.append_message("...Family output directory: [{}]".format(family_output_directory))
            return_value.result.append(family_output_directory)
        else:
            return_value.update_sep(False, "...invalid Entity: [{}]".format(stored_entity))
    except Exception as e:
        return_value.update_sep(False, "Error retrieving family output directory from schema: {}".format(e))
    return return_value