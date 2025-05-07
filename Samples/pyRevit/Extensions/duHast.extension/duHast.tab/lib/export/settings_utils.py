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

from export.Objects.Settings import Settings


from export import settings

def get_name_settings_from_schema(doc):
    """
    Get the name settings from the schema associated with the document.
    
    :param doc: The Revit document to retrieve the output path from.
    :type doc: Autodesk.Revit.DB.Document
    :return: A Result object containing the settings object in result or an error message.
    :rtype: Result
    """
    # set up a status tracker
    return_value = Result()

    exporter_settings = Settings()
    try:
        schema = get_schema(settings.EXPORTER_ADD_IN_GUID)
        data_storage = find_data_storage(doc, settings.EXPORTER_ADD_IN_GUID)
        stored_entity = data_storage.GetEntity(schema)
        if stored_entity.IsValid():

            # get the pdf settings from the entity
            exporter_settings.pdf_settings = stored_entity.Get[str](settings.DU_HAST_EXPORTER_PDF_SETTING_FIELD_NAME)
            return_value.append_message("...pdf settings [{}]".format(exporter_settings.pdf_settings))

            # get the dwg settings from the entity
            exporter_settings.dwg_settings = stored_entity.Get[str](settings.DU_HAST_EXPORTER_DWG_SETTING_FIELD_NAME)
            return_value.append_message("...dwg settings [{}]".format(exporter_settings.dwg_settings))

            return_value.result.append(exporter_settings)
        else:
            return_value.update_sep(False, "...invalid Entity: [{}]".format(stored_entity))
    except Exception as e:
        return_value.update_sep(False, "Error retrieving settings from schema: {}".format(e))
    return return_value