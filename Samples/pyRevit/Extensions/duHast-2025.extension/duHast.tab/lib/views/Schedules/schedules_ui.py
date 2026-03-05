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
from duHast.Revit.Views.schedules import get_schedules
from duHast.Revit.Views.schedules_fields import get_field_names_from_schedule

from Autodesk.Revit.DB import Element

# ui functions around schedule selection by the user

# set up some options for the user to select in terms of which fields to export
EXPORT_ALL = "Export All Fields"
EXPORT_SPECIFIC = "Export Only Selected Fields"


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
    :param source_view_template_name: The name of the source view template to exclude from the list of target view templates.
    :type source_view_template_name: str

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


def get_schedule_fields_from_user(forms, field_list, button_name="Select Schedules Fields To Export"):
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

    :return: fields_to_export_by_schedule_name
    :rtype: {str: [str]}
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
    
    selected_fields = get_schedule_fields_from_user(forms, unique_fields, button_name="Select Schedules Fields To Export")
    if len(selected_fields) == 0:
        return_value.update_sep(False, "No fields selected for export.")
        print("No fields selected for export. Exiting...")
        return return_value
    
    # update what get returned
    return_value.update_sep(True, "User selected to export the following fields: {}".format(selected_fields))
    return_value.result = selected_fields

    return return_value