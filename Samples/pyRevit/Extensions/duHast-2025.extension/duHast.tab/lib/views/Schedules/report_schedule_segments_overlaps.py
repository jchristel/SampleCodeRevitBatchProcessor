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
import os
import csv

from duHast.pyRevit.Objects.ProgressPyRevit import ProgressPyRevit
from duHast.pyRevit.console_output import print_error, print_header
from duHast.Utilities.Objects.result import Result
from duHast.Revit.Views.schedules_sheet_instances import (
    get_sheets_with_overlapping_schedules,
    get_sheets_with_schedules_outside_titleblock,
    get_sheets_with_schedules_overlapping_viewports
)
from duHast.Utilities.files_csv import write_report_data_as_csv

from sheets_ui import get_sheets_from_user_dialogue



from Autodesk.Revit.DB import Element

from pyrevit.framework import Forms

DEBUG = False

def _convert_data_to_csv_string(document_title, data):
    """
    Converts the data on sheets with overlapping schedule segments to a list of lists that can be easily written to a csv file.
    """

    report_data = []
    for sheet, overlaps in data:
        row_data = ["{}".format(document_title),"{} {}:".format(sheet.SheetNumber, Element.Name.GetValue(sheet)), str(len(overlaps))]
        report_data.append(row_data)
    return report_data

def report_schedule_segments_overlap_entry(doc, output, forms, debug=DEBUG):
    """
    Allows the user to select schedules and reports on whether any of the segments in the selected schedules are either overlapping with the title block or other view ports on the sheet.
    
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
        print_header("Reporting sheets with overlapping schedule segments...")

        # let the user select the schedules to check
        # select an output folder to save the reports to
        # gather overlap data
        # write reports to the selected output folder

        selected_sheets = get_sheets_from_user_dialogue(doc, forms)

        if len(selected_sheets) == 0:
            return_value.update_sep(
                status=False,
                message="No sheets selected for overlap checking."
            )
            print_error("No sheets selected for overlap checking. Exiting...")
            return return_value
        
        # get a folder to save the reports to
        report_out_folder_path = None
        report_out_folder_path = forms.pick_folder("Select the reports export folder")
        if report_out_folder_path is None:
            message = "No folder selected. Exiting."
            print(message)
            return_value.update_sep(False, message=message)
            return return_value


        # set up a pyrevit progress bar
        with forms.ProgressBar(
            title="Checking sheets: {value} of {max_value}", cancellable=True
        ) as pb:
            
            progress_bar = ProgressPyRevit(pb)

            check_schedules_overlap_result = get_sheets_with_overlapping_schedules(doc, selected_sheets, callback_progress=progress_bar)
            check_schedules_outside_titleblock_result = get_sheets_with_schedules_outside_titleblock(doc, selected_sheets, callback_progress=progress_bar)
            check_schedules_overlap_viewports_result = get_sheets_with_schedules_overlapping_viewports(doc, selected_sheets, callback_progress=progress_bar)
            
            # check what needs to be written to file
            if len(check_schedules_overlap_result) == 0:
                print("No overlapping schedule segments found on the selected sheets.")
                return_value.append_message("No overlapping schedule segments found on the selected sheets.")
            else:
                # give user feedback
                message = "{} sheets with overlapping schedule segments found.".format(len(check_schedules_overlap_result))
                return_value.append_message(message)
                print(message)

                if DEBUG:
                    print(check_schedules_overlap_result)

                # write results to file
                output_file_path_segment = os.path.join(report_out_folder_path, "{}_schedule_segments_overlap.csv".format(doc.Title))
                write_segment_overlap_result = write_report_data_as_csv(
                    file_name=output_file_path_segment,
                    header=[],
                    data=_convert_data_to_csv_string(doc.Title, check_schedules_overlap_result),
                    quoting=csv.QUOTE_MINIMAL
                )
                return_value.update(write_segment_overlap_result)
            
            if len(check_schedules_outside_titleblock_result) == 0:
                print("No schedule segments found outside the title block on the selected sheets.")
                return_value.append_message("No schedule segments found outside the title block on the selected sheets.")
            else:
                # give user feedback
                message = "{} sheets with schedule segments outside the title block found.".format(len(check_schedules_outside_titleblock_result))
                return_value.append_message(message)
                print(message)

                if DEBUG:
                    print(check_schedules_outside_titleblock_result)

                #  write results to file
                output_file_titleblock_overlaps=os.path.join(report_out_folder_path, "{}_schedule_overlaps_title_block.csv".format(doc.Title))
                write_titleblock_overlap_result = write_report_data_as_csv(
                    file_name=output_file_titleblock_overlaps,
                    header=[],
                    data=_convert_data_to_csv_string(doc.Title, check_schedules_outside_titleblock_result),
                    quoting=csv.QUOTE_MINIMAL
                )
                return_value.update(write_titleblock_overlap_result)
            
            if len(check_schedules_overlap_viewports_result) == 0:
                print("No schedule segments found overlapping viewports on the selected sheets.")
                return_value.append_message("No schedule segments found overlapping viewports on the selected sheets.")
            else:
                # give user feedback
                message = "{} sheets with schedule segments overlapping viewports found.".format(len(check_schedules_overlap_viewports_result))
                return_value.append_message(message)
                print(message)

                if DEBUG:
                    print(check_schedules_overlap_viewports_result)

                # write results to file
                output_file_viewport_overlaps=os.path.join(report_out_folder_path, "{}_schedule_overlaps_viewports.csv".format(doc.Title))
                write_viewport_overlap_result = write_report_data_as_csv(
                    file_name=output_file_viewport_overlaps,
                    header=[],
                    data=_convert_data_to_csv_string(doc.Title, check_schedules_overlap_viewports_result),
                    quoting=csv.QUOTE_MINIMAL
                )
                return_value.update(write_viewport_overlap_result)
                
    except Exception as e:
        return_value.update_sep(
            status=False,
            message="Failed to modify specific column widths: {}".format(e)
        )
        

        print("Error: {}".format(e))

        return return_value
    
    print("Finished checking for overlapping schedule segments.")
    return return_value