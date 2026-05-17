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


from duHast.pyRevit.UI.doc_selector import pick_document
from duHast.pyRevit.UI.ui_element_selection import get_element_selection_from_user


def get_model_selection(doc, forms):
    """
    Prompts the user to select a model (active or linked) containing push it rooms.

    :param doc: The Revit document
    :type doc: Autodesk.Revit.DB.Document
    :param forms: The pyRevit forms module
    :type forms: pyRevit.forms
    :return: The selected model, or None if cancelled.
    :rtype: Autodesk.Revit.DB.Document or None
    """
    return pick_document(doc, forms, button_name="Select model with push it rooms.")


def get_push_it_room_selection(doc, push_it_rooms, unique_id_parameter_guid, forms):

    def room_getter(doc):
        return push_it_rooms

    def ui_name_builder(element):
        return element.get_ui_name(unique_id_parameter_guid)

    rooms_selected_result = get_element_selection_from_user(
        doc=doc,
        forms=forms,
        element_getter=room_getter,
        element_selection_description="select push it rooms to convert",
        multiselect=True,
        ui_element_name_builder=ui_name_builder,
    )

    if rooms_selected_result is not None and len(rooms_selected_result) > 0:
        return rooms_selected_result
    return None

    