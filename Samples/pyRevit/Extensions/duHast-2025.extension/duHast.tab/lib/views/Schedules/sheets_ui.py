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
from duHast.Revit.Views.sheets import get_all_sheets, get_sheet_number

from Autodesk.Revit.DB import Element

def get_sheets_for_ui(doc):
    """
    Returns all schedules in the model

    :param doc: The current model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: view_filter_names, view_filters_by_name
    :rtype: [str], {str: Autodesk.Revit.DB.View}
    """

    # set up return values
    sheet_names = []
    sheets_by_name = {}

    # get all view templates
    sheets = get_all_sheets(doc=doc)
    for sheet in sheets:
        key = "{} {}".format(get_sheet_number(sheet), Element.Name.GetValue(sheet))
        sheet_names.append(key)
        sheets_by_name[key] = sheet

    return sheet_names, sheets_by_name


def get_sheets_from_user_dialogue(doc, forms, button_name="Select Sheets to check for Schedule Overlaps"):
    """
    returns the sheets by user selection

    :param doc: The current model document.
    :type doc: Autodesk.Revit.DB.Document
    :param forms: pyRevit forms module
    :type forms: module
    :param button_name: The name of the button to show in the selection window
    :type button_name: str

    :return: target_view_templates
    :rtype: [Autodesk.Revit.DB.View]
    """

    sheets_selected = []

    # get sheets in the model
    sheet_names, sheets_by_name = get_sheets_for_ui(doc)

    # check if we got any?
    if len(sheet_names) == 0:
        return sheets_selected

    # get the user to select the source ( returns a string)
    selection = forms.SelectFromList.show(
        sorted(sheet_names),
        button_name=button_name,
        multiselect=True,
    )


    if selection is None or len(selection) == 0:
        return sheets_selected
    else:
        for sheet_name in selection:
            sheets_selected.append(
                sheets_by_name[sheet_name]
            )
        return sheets_selected
    