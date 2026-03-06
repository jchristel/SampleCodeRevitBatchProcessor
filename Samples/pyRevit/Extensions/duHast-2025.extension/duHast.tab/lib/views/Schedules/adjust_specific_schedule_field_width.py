# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2026, Jan Christel
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


from duHast.pyRevit.Objects.ProgressPyRevit import ProgressPyRevit
from duHast.pyRevit.console_output import print_error, print_header
from duHast.pyRevit.file_picker import get_file_path_from_user

from duHast.Utilities.Objects.result import Result
from duHast.Revit.Views.schedules_modify import adjust_column_width
from duHast.Revit.Common.element_id import get_el_id_int

from schedules_ui import (
    get_schedules_from_user,  
    determine_single_field_to_export,  
    get_column_width_dialogue
)


from pyrevit.framework import Forms

DEBUG = True



def _build_field_data_dict(schedules_to_modify, name_of_field_to_modify, column_width_in_mm):
    """
    Builds a dictionary in the format {schedule_id: {field_name: column_width_in_mm}} which is then used to modify the column widths of the selected schedules.

    :param schedules_to_modify: List of schedules to modify the column widths for.
    :type schedules_to_modify: list of Autodesk.Revit.DB.ViewSchedule
    :param name_of_field_to_modify: Name of the field to modify the column width for.
    :type name_of_field_to_modify: str
    :param column_width_in_mm: Column width in mm to set for the specified field in the selected schedules.
    :type column_width_in_mm: float

    :return: Dictionary in the format {schedule_id_int: {field_name: column_width_in_mm}}
    :rtype: dict
    """

    field_data_dict = {}

    for schedule in schedules_to_modify:
        schedule_id_int = int(get_el_id_int(schedule.Id))
        if schedule_id_int not in field_data_dict:
            field_data_dict[schedule_id_int] = {}
        
        field_data_dict[schedule_id_int][name_of_field_to_modify] = column_width_in_mm
    
    return field_data_dict


def import_schedules_column_width_entry(doc, output, forms, debug=DEBUG):
    """
    Allows the user to set the column width of schedules based on a csv file which contains the schedule names, field names and column widths to set. The user can select which schedules to import the column widths for.
    
    :return:
        Result class instance.

        - result.status: Export status will be in result.status. False if an exception occurred, otherwise True.
        - result.message will contain the file path of the .json file created.
        - result.result will be an empty list

        On exception

        - result.status (bool) will be False
        - result.message will contain the exception message

    :rtype: :class:`.Result`
    """

    # set up a status tracker
    return_value = Result()

    try:
        print_header("Adjusting specific schedule column widths...")

        # let the user select the schedules to update
        # let the user select the field of which to update the width
        # get the width in mm from the user
        # update the column widths of the selected schedules based on provided data

        # get the user to select which schedules to export
        schedules_to_update = get_schedules_from_user(doc, forms, button_name="Select Schedules To Modify A Specific Column Widths")
        if len(schedules_to_update) == 0:
            return_value.update_sep(
                status=False,
                message="No schedules selected for modification."
            )
            print_error("No schedules selected for modification. Exiting...")
            return return_value


        # get the field name from the user
        result_determine_single_field_to_export = determine_single_field_to_export(forms, schedules_to_update)

        if not result_determine_single_field_to_export.status:
            print_error("Field and column width selection failed with message: {}".format(result_determine_single_field_to_export.message))
            return_value.update_sep(
                status=False,
                message=result_determine_single_field_to_export.message
            )
            return return_value
        
        if result_determine_single_field_to_export.result is None or len(result_determine_single_field_to_export.result) == 0:
            print_error("No field and column width selected for modification.")
            return_value.update_sep(
                status=False,
                message="No field and column width selected for modification."
            )
            return return_value
        
        # store the name of the field to modify
        name_of_field_to_modify = result_determine_single_field_to_export.result[0]

        # get the field width in mm from the user
        column_width_in_mm =  get_column_width_dialogue()
        if column_width_in_mm is None:
            print_error("No column width provided for modification.")
            return_value.update_sep(
                status=False,
                message="No column width provided for modification."
            )
            return return_value
        
        # build the field data dictionary and get to it
        field_data_dict = _build_field_data_dict(schedules_to_update, name_of_field_to_modify, column_width_in_mm)

        # set up a pyrevit progress bar
        with forms.ProgressBar(
            title="Importing schedules: {value} of {max_value}", cancellable=True
        ) as pb:
            
            progress_bar = ProgressPyRevit(pb)

            adjust_result = adjust_column_width(
                doc, 
                schedules_to_update, 
                field_data_dict, 
                callback_progress=progress_bar
            )
    
            return_value.update(adjust_result)

            # list schedules that were skipped because they did not contain the specified field
            if len(adjust_result.result) > 0:
                print("The following schedules were skipped because they did not contain the specified field: {}".format(adjust_result.result))
            else:
                print("All schedules were updated successfully.")

    except Exception as e:
        return_value.update_sep(
            status=False,
            message="Failed to modify specific column widths: {}".format(e)
        )
        

        print("Error: {}".format(e))

        return return_value
    
    return return_value