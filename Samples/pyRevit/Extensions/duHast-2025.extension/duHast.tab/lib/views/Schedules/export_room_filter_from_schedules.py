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


import csv

from duHast.Utilities.Objects.result import Result
from duHast.Utilities.files_csv import write_report_data_as_csv
from duHast.Revit.Views.schedules_element_filters import get_schedule_filters_by_field_name
from schedules_ui import get_schedules_from_user
from families.util.print_table import print_result_table
from duHast.pyRevit.console_output import print_error, print_header

from Autodesk.Revit.DB import ElementId

SCHEDULE_FILTER_FIELD_NAME = "Room: Number"

def export_room_filter_values_from_schedules_entry(doc, output, forms):
    """
    exports room filter values from schedules to a csv file.
   
    Export contains the following columns:

    - Schedule Name
    - Schedule Id
    - Filter index
    - Room Filter Value

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param output: pyRevit output
    :type output: pyRevit output module
    :param forms: pyRevit forms
    :type forms: pyRevit forms module

    :return:
        Result class instance.

        - result.status (bool) True if families where reported without an exception, otherwise False.
        - result.message contains log messages.
        - result.result will be an empty list.

        On exception:

        - result.status (bool) will be False.
        - result.message will contain exception message.
    :rtype: :class:`.Result`
    """

    # set up a status tracker
    return_value = Result()

    try:

        # get user selected library reports
        print("Select schedules:")

        schedule_of_interest = get_schedules_from_user(doc, forms, "Select schedules to export room filter values from")
        if schedule_of_interest is None or len(schedule_of_interest) == 0:
            message = "No valid schedules selected"
            print(message)
            return_value.update_sep(False, message)
            return return_value
        
        #set up a pyRevit progress bar
        with forms.ProgressBar(
            title="Exporting: {value} of {max_value}",
            cancellable=True,
        ) as pb:
            
            print_header("Gathering schedule values:")

            data = []

            max_count = len(schedule_of_interest)
            schedule_counter = 1
            # get room filter values from schedules
            for schedule in schedule_of_interest:

                print_header("Processing schedule: {} ({} of {})".format(schedule.Name, schedule_counter, max_count))
                pb.update_progress(schedule_counter, max_count)

                # get all filters for the schedule for the field name "Room: Number"
                filters_for_room_number = get_schedule_filters_by_field_name(schedule, SCHEDULE_FILTER_FIELD_NAME)
                
                if len(filters_for_room_number) > 0:
                    for filter in filters_for_room_number:
                        if filter.IsStringValue:
                            print("Found filter for field {} with value: {}".format(SCHEDULE_FILTER_FIELD_NAME, filter.GetStringValue()))
                            data.append([schedule.Name, str(int(schedule.Id.Value)), str(schedule.Definition.GetField(filter.FieldId).FieldIndex), filter.GetStringValue()])
                            
                            # only export one filter value per schedule, if there are multiple filters for the same field, only the first one will be exported. 
                            # This is to avoid confusion and to keep the export simple. 
                            break
                        else:
                            print("filter is not a string value")
                else:
                    print_error("Schedule {} has no filters".format(schedule.Name))
                
                # update schedule counter
                schedule_counter += 1

                # check if cancelled
                if pb.cancelled:
                    print("Export cancelled by user")
                    return_value.update_sep(False, "Export cancelled by user")
                    return return_value
                        

            header = ["Schedule Name", "Schedule Id", "Filter index", "Room Filter Value"]

            print_result_table(output, data, header, "Schedule Filter Values")

            # get a file path to save the comparison result
            file_path = forms.save_file(file_ext='csv', title="Save filter export to csv file")

            if (file_path and len(file_path) > 0):
                write_result = write_report_data_as_csv(file_name=file_path, header= header,  data=data , quoting=csv.QUOTE_MINIMAL)
                if(write_result.status):
                    print("Successfully wrote filter report to: {} ".format(file_path ))
                else:
                    print("Failed to write filter report to: {} ".format(file_path ))
                    print("Error: {}".format(write_result.message))
            else:
                print("No file path selected")

    except Exception as e:
        message = "An exception occurred while exporting filter values from schedules: {}".format(e)
        print_error(message)
        return_value.update_sep(
            False, message
        )

    print("\n{}".format(return_value.message))
    print("Finished")

    return return_value