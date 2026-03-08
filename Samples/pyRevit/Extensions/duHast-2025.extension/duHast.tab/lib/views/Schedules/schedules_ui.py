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
from duHast.Revit.Views.schedules import get_schedules, filter_split_schedules , get_all_schedules_placed_on_sheets
from duHast.Revit.Views.schedules_fields import get_field_names_from_schedule
from duHast.Revit.Common.element_id import get_el_id_int

from Autodesk.Revit.DB import Element

# ui components
from rpw.ui.forms import FlexForm, Label, TextBox, Button

# ui functions around schedule selection by the user

# set up some options for the user to select in terms of which fields to export
EXPORT_ALL = "Export All Fields"
EXPORT_SPECIFIC = "Export Only Selected Fields"


# ------------------------------------------------------------------- all schedules in models specific functions -------------------------------------------------------------------

def get_schedules_for_ui(doc):
    """
    Returns all schedules in the model

    :param doc: The current model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: view_filter_names, view_filters_by_name
    :rtype: [str], {str: Autodesk.Revit.DB.View}
    """

    # set up return values
    schedule_names = []
    schedules_by_name = {}

    # get all view templates
    schedules = get_schedules(doc=doc)
    for schedule in schedules:
        key = Element.Name.GetValue(schedule)
        schedule_names.append(key)
        schedules_by_name[key] = schedule

    return schedule_names, schedules_by_name


def get_schedules_from_user(doc, forms, button_name="Select Schedules To Export"):
    """
    returns the schedules by user selection

    :param doc: The current model document.
    :type doc: Autodesk.Revit.DB.Document
    :param forms: pyRevit forms module
    :type forms: module
    :param button_name: The name of the button to show in the selection window
    :type button_name: str

    :return: target_view_templates
    :rtype: [Autodesk.Revit.DB.View]
    """

    schedules_selected = []

    # get view filter in the model
    schedule_names, schedules_by_name = get_schedules_for_ui(doc)

    # check if we got any?
    if len(schedule_names) == 0:
        return schedules_selected

    # get the user to select the source ( returns a string)
    selection = forms.SelectFromList.show(
        sorted(schedule_names),
        button_name=button_name,
        multiselect=True,
    )


    if selection is None or len(selection) == 0:
        return schedules_selected
    else:
        for source_view_filter_name in selection:
            schedules_selected.append(
                schedules_by_name[source_view_filter_name]
            )
        return schedules_selected
    

# ------------------------------------------------------------------- imported schedules from csv specific functions -------------------------------------------------------------------

def get_schedules_to_import_for_ui(doc, schedule_data):
    """
    Returns all schedules in the model

    :param doc: The current model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: view_filter_names, view_filters_by_name
    :rtype: [str], {str: Autodesk.Revit.DB.View}
    """

    # set up return values
    schedule_names = []
    schedules_by_name = {}

    # get the list of keys from the schedule data representing the schedule ids for which we have data in the csv file
    schedule_ids_to_import = schedule_data.keys()
    
    # get all view templates
    schedules = get_schedules(doc=doc)
    for schedule in schedules:
        
        # check if this schedule is in the list of schedules to import based on the schedule id, if not skip it and don't show it to the user for selection, 
        # as we only want to show schedules for which we have data in the csv file to import
        if get_el_id_int(schedule.Id) not in schedule_ids_to_import:
            continue

        key = Element.Name.GetValue(schedule)
        schedule_names.append(key)
        schedules_by_name[key] = schedule

    return schedule_names, schedules_by_name


def get_schedules_from_user_to_import(doc, forms, button_name="Select Schedules To Import Column Widths For", schedule_data = None):
    """
    returns the schedules by user selection

    :param doc: The current model document.
    :type doc: Autodesk.Revit.DB.Document
    :param forms: pyRevit forms module
    :type forms: module
    :param button_name: The name of the button to show in the selection window
    :type button_name: str
    :param schedule_data: the schedule data read from the csv file, used to filter the schedules that are shown to the user for selection
    :type schedule_data: dict[int, dict[str, int]]

    :return: target_view_templates
    :rtype: [Autodesk.Revit.DB.View]
    """

    schedules_selected = []

    # get view filter in the model
    schedule_names, schedules_by_name = get_schedules_to_import_for_ui(doc, schedule_data)

    if len(schedule_names) == 0:
        print("No schedules found in the model matching the schedule data read from the csv file. Exiting...")
        return schedules_selected

    # check if we got any?
    if len(schedule_names) == 0:
        return schedules_selected

    # get the user to select the source ( returns a string)
    selection = forms.SelectFromList.show(
        sorted(schedule_names),
        button_name=button_name,
        multiselect=True,
    )

    if selection is None or len(selection) == 0:
        return schedules_selected
    else:
        for source_view_filter_name in selection:
            schedules_selected.append(
                schedules_by_name[source_view_filter_name]
            )
        return schedules_selected

# ------------------------------------------------------------------- split schedules on sheets specific functions -------------------------------------------------------------------

def get_split_schedules_for_ui(doc):
    """
    Returns all schedules in the model

    :param doc: The current model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: view_filter_names, view_filters_by_name
    :rtype: [str], {str: Autodesk.Revit.DB.View}
    """

    # set up return values
    schedule_names = []
    schedules_by_name = {}

    # get all view templates
    schedules = get_all_schedules_placed_on_sheets(doc=doc)
    split_schedules = filter_split_schedules(schedules)

    for schedule in split_schedules:
        key = Element.Name.GetValue(schedule)
        schedule_names.append(key)
        schedules_by_name[key] = schedule

    return schedule_names, schedules_by_name


def get_split_schedules_from_user_dialogue(doc, forms, button_name="Select Schedules To Fix Overlaps For"):
    """
    returns the schedules by user selection

    :param doc: The current model document.
    :type doc: Autodesk.Revit.DB.Document
    :param forms: pyRevit forms module
    :type forms: module
    :param button_name: The name of the button to show in the selection window
    :type button_name: str

    :return: target_view_templates
    :rtype: [Autodesk.Revit.DB.View]
    """

    schedules_selected = []

    # get view filter in the model
    schedule_names, schedules_by_name = get_split_schedules_for_ui(doc)

    # check if we got any?
    if len(schedule_names) == 0:
        raise Exception("No split schedules found in the model. Exiting...")

    # get the user to select the source ( returns a string)
    selection = forms.SelectFromList.show(
        sorted(schedule_names),
        button_name=button_name,
        multiselect=True,
    )

    if selection is None or len(selection) == 0:
        return schedules_selected
    else:
        for source_view_filter_name in selection:
            schedules_selected.append(
                schedules_by_name[source_view_filter_name]
            )
        return schedules_selected


# ------------------------------------------------------------------- all schedules on sheets specific functions -------------------------------------------------------------------

def get_all_schedules_on_sheets_for_ui(doc):
    """
    Returns all schedules on sheets in the model

    :param doc: The current model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: view_filter_names, view_filters_by_name
    :rtype: [str], {str: Autodesk.Revit.DB.View}
    """

    # set up return values
    schedule_names = []
    schedules_by_name = {}

    # get all view templates
    schedules = get_all_schedules_placed_on_sheets(doc=doc)

    for schedule in schedules:
        key = Element.Name.GetValue(schedule)
        schedule_names.append(key)
        schedules_by_name[key] = schedule

    return schedule_names, schedules_by_name


def get_all_schedules_on_sheets_from_user_dialogue(doc, forms, button_name="Select Schedules To Report Overlaps For"):
    """
    returns the schedules by user selection

    :param doc: The current model document.
    :type doc: Autodesk.Revit.DB.Document
    :param forms: pyRevit forms module
    :type forms: module
    :param button_name: The name of the button to show in the selection window
    :type button_name: str

    :return: target_view_templates
    :rtype: [Autodesk.Revit.DB.View]
    """

    schedules_selected = []

    # get view filter in the model
    schedule_names, schedules_by_name = get_all_schedules_on_sheets_for_ui(doc)

    # check if we got any?
    if len(schedule_names) == 0:
        raise Exception("No schedules on sheets found in the model. Exiting...")

    # get the user to select the source ( returns a string)
    selection = forms.SelectFromList.show(
        sorted(schedule_names),
        button_name=button_name,
        multiselect=True,
    )

    if selection is None or len(selection) == 0:
        return schedules_selected
    else:
        for source_view_filter_name in selection:
            schedules_selected.append(
                schedules_by_name[source_view_filter_name]
            )
        return schedules_selected



# ------------------------------------------------------------------- schedule fields export specific functions -------------------------------------------------------------------

def get_user_fields_export_options(forms):
    """
    Gets the user options for exporting all fields or only specific fields of the schedule.

    Options are: EXPORT_ALL, EXPORT_SPECIFIC

    :param forms: the forms object
    :type forms: Forms
    :return: the user options
    :rtype: dict
    """

    # ask user for export all or specific fields
    ops = [EXPORT_ALL,EXPORT_SPECIFIC]
    configs = {
        EXPORT_ALL: {"background": "#FF0000"},
        EXPORT_SPECIFIC : {"background": "#FF0000"},
    }
    ui_options = forms.CommandSwitchWindow.show(
        ops,  message="Select Export Scope", config=configs
    )

    return ui_options


def get_unique_fields_from_schedules(schedules):
    """
    Gets a unique list of all fields across the schedules

    :param schedules: list of schedules to select fields from
    :type schedules: list of Autodesk.Revit.DB.ViewSchedule

    :return: unique_fields
    :rtype: [str]
    """

    unique_fields = set()

    for schedule in schedules:
        field_names = get_field_names_from_schedule(schedule)
        for field_name in field_names:
            unique_fields.add(field_name)

    return sorted(list(unique_fields))


def get_schedule_fields_from_user_dialogue(forms, field_list, button_name="Select Schedules Fields To Export"):
    """
    returns the schedules fields by user selection

    :param forms: pyRevit forms module
    :type forms: module
    :param source_view_template_name: The name of the source view template to exclude from the list of target view templates.
    :type source_view_template_name: str

    :return: target_view_templates
    :rtype: [Autodesk.Revit.DB.View]
    """

    # get the user to select the source ( returns a string)
    selection = forms.SelectFromList.show(
        sorted(field_list),
        button_name=button_name,
        multiselect=True,
    )

    if selection is None or len(selection) == 0:
        return []
    else:
        return selection


def determine_fields_to_export(forms, schedules):
    """
    Gets the user to select which fields of the schedule to export

    :param forms: pyRevit forms module
    :type forms: module
    :param schedules: list of schedules to select fields from
    :type schedules: list of Autodesk.Revit.DB.ViewSchedule

    :return: result object with the selected fields to export in result.result, and a message in result.message about the user selection
    :rtype: Result.result list contains dictionary {str: [str]}
    """

    # set up a status tracker
    return_value = Result()


    # check with user whether all schedule fields should be exported or only specific ones
    # get user options
    user_selection = get_user_fields_export_options(forms)

    if user_selection == None:
        return_value.update_sep(False, "User cancelled operation")
        print("User cancelled operation")
        return return_value
    
    if user_selection == EXPORT_ALL:
        return_value.append_message("User selected to export all fields of all schedules.")
        print ("Exporting all fields of all schedules...")
        # i can just return the return value with an empty result list and a message that all fields will be exported, and then handle the export of all fields in the calling function
        return return_value
    
    # get a unique list of all fields across the schedules and the get the user to select which ones to export
    unique_fields = get_unique_fields_from_schedules(schedules)
    if len(unique_fields) == 0:
        return_value.update_sep(False, "No fields found in the selected schedules.")
        print("No fields found in the selected schedules. Exiting...")
        return return_value
    
    selected_fields = get_schedule_fields_from_user_dialogue(forms, unique_fields, button_name="Select Schedules Fields To Export")
    if len(selected_fields) == 0:
        return_value.update_sep(False, "No fields selected for export.")
        print("No fields selected for export. Exiting...")
        return return_value
    
    # update what get returned
    return_value.update_sep(True, "User selected to export the following fields: {}".format(selected_fields))
    return_value.result = selected_fields

    return return_value


# ------------------------------------------------------------------- single schedule field selection specific functions -------------------------------------------------------------------

def get_single_schedule_field_from_user_dialogue(forms, field_list, button_name="Select Schedule Fields To Modify Column Width For"):
    """
    returns the schedules fields by user selection

    :param forms: pyRevit forms module
    :type forms: module
    :param source_view_template_name: The name of the source view template to exclude from the list of target view templates.
    :type source_view_template_name: str

    :return: target_view_templates
    :rtype: [Autodesk.Revit.DB.View]
    """

    # get the user to select the source ( returns a string)
    selection = forms.SelectFromList.show(
        sorted(field_list),
        button_name=button_name,
        multiselect=False,
    )

    return selection
    

def determine_single_field_to_export(forms, schedules):
    """
    Get the user to select a single field of the schedule to export, this is used for the adjust specific column width functionality where the user needs to select a single field of which to adjust the column width for
    
    :param forms: pyRevit forms module
    :type forms: module
    :param schedules: list of schedules to select fields from
    :type schedules: list of Autodesk.Revit.DB.ViewSchedule

    :return: result object with the selected field to in result.result, and a message in result.message about the user selection
    :rtype: Result.result list contains single entry or is empty if no field was selected
    """

    # set up a status tracker
    return_value = Result()

    # get a unique list of all fields across the schedules and the get the user to select which ones to export
    unique_fields = get_unique_fields_from_schedules(schedules)
    if len(unique_fields) == 0:
        return_value.update_sep(False, "No fields found in the selected schedules.")
        print("No fields found in the selected schedules. Exiting...")
        return return_value
    
    selected_field = get_single_schedule_field_from_user_dialogue(forms, unique_fields)
    if selected_field is None == 0:
        return_value.update_sep(False, "No field selected for modification.")
        print("No fields selected for modification. Exiting...")
        return return_value
    
    # update what get returned
    return_value.update_sep(True, "User selected to export the following field: {}".format(selected_field))
    return_value.result.append(selected_field)
    return return_value



# ------------------------------------------------------------------- columns width specific functions -------------------------------------------------------------------


def get_column_width_dialogue():
    """
    Get the user to input a column width in mm for the adjust specific column width functionality, this is used to get the column width to set for the selected field in the selected schedules

    :return: the column width input by the user in mm, or None if the user input is invalid
    :rtype: float or None
    """

    text_box_column_width_key = "width_input"
    # Define the form layout
    components = [
        Label("Enter width in mm:"),
        TextBox(text_box_column_width_key),  # TextBox with a key to retrieve the input
        Button("Submit")
    ]

    # Create and show the form
    form = FlexForm("Text Input Form", components)
    form.show()

    # Retrieve the user input
    item_width_input = form.values.get(text_box_column_width_key)

    try:
        float_width_input = float(item_width_input)
        return float_width_input
    except:
        return None