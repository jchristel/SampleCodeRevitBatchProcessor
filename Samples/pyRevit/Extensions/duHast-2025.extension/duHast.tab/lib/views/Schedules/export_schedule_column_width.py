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
from duHast.Utilities.Objects.result import Result
from duHast.Revit.Views.Reporting.schedules_report import export_schedules_column_widths

from schedules_ui import get_schedules_from_user, determine_fields_to_export


from pyrevit.framework import Forms

DEBUG = True


def export_schedules_column_width_entry(doc, output, forms, debug=DEBUG):
    """
    Allows the user to select schedules of which to export either all column widths or just the ones which get selected in the UI. The column widths get exported to a csv file.
    
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
        print_header("Exporting schedule column widths...")

        # get the user to select which schedules to export
        schedules_to_export = get_schedules_from_user(doc, forms, button_name="Select Schedules To Export Column Widths For")
        if len(schedules_to_export) == 0:
            return_value.update_sep(
                status=False,
                message="No schedules selected for export."
            )
            print_error("No schedules selected for export. Exiting...")
            return return_value
        
        # get the user to select whether all column or only specific column widths should be exported
        determine_fields_to_export_result =  determine_fields_to_export(forms, schedules_to_export)

        # check what the result of the field selection was
        if not determine_fields_to_export_result.status:
            if DEBUG:
                print_error("Field selection failed with message: {}".format(determine_fields_to_export_result.message))
            return_value.update_sep(
                status=False,
                message=determine_fields_to_export_result.message
            )
            return return_value
        
        # get the fields to export from the result of the field selection
        # this can be an empty list if the user selected to export all fields, or a list of fields if the user selected to export specific fields
        specific_fields_to_export = determine_fields_to_export_result.result

        if DEBUG:
            if specific_fields_to_export is None or len(specific_fields_to_export) == 0:
                print("User selected to export all fields of the schedules.")
            else:
                print("User selected to export the following fields: {}".format(specific_fields_to_export))

        # get the user to specify an output file path
        file_path = forms.save_file(file_ext="csv", title="Save report to csv file")

        if file_path and len(file_path) > 0:
            # collate data and write data to file
            export_result = export_schedules_column_widths(
                doc=doc, 
                file_name=file_path, 
                schedules=schedules_to_export, 
                field_names_of_interest=specific_fields_to_export
            )

            if DEBUG:
                print("Export result status: {}, message: {}".format(export_result.status, export_result.message))
            
            if export_result.status:
                message = "Successfully exported schedule column widths to: {} ".format(file_path)
                return_value.append_message(
                    message
                )
                print(message)
            else:
                return_value.update_sep(
                    False,
                    "Failed to export schedule column widths to: {} with error: {}".format(
                        file_path, export_result.message
                    ),
                )
            return return_value
        else:
            return_value.append_message("No file path selected")
            print_error("No file path selected. Exiting...")
            return return_value
    
    except Exception as e:
        return_value.update_sep(
            status=False,
            message="Failed to export schedules column widths: {}".format(e)
        )
        

        print("Error: {}".format(e))

        return return_value