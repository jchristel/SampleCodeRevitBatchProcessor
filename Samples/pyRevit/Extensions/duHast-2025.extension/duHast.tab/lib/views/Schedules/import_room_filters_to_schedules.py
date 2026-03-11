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
from duHast.pyRevit.console_output import print_error, print_header
from duHast.Revit.Common.transaction import in_transaction
from duHast.Revit.Views.schedules_element_filters import get_schedule_filters_by_field_name
from duHast.Utilities.files_csv import read_csv_file
from duHast.pyRevit.file_picker import get_file_path_from_user

from Autodesk.Revit.DB import ElementId, Transaction

from System import Int64

SCHEDULE_FILTER_FIELD_NAME = "Room: Number"


def import_room_filter_values_to_schedules_entry(doc, output, forms):
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
        print("importing schedules filter values:")

        file_path = get_file_path_from_user(forms, "Select csv import", "csv", multi_file=False)

        if not file_path:
            return_value.update_sep(False, "No file path selected.")
            return return_value
    
        # read csv file
        csv_data_result = read_csv_file(file_path)
        
        # check csv data
        if not csv_data_result.status or len(csv_data_result.result) == 0:
            return_value.update_sep(False, "Failed to read csv file: {}".format(csv_data_result.message))
            return return_value

        csv_data = csv_data_result.result
        print("Found {} rows in csv file".format(len(csv_data)))

        # progress tracking
        counter = 1
        max_count = len(csv_data)-1 # skipping header row

        # set up a pyRevit progress bar
        with forms.ProgressBar(
            title="Importing: {value} of {max_value}",
            cancellable=True,
        ) as pb:
            
            # skip the header row
            for schedule_data in csv_data [1:]:

                # format csv data into variables
                field_index = int(schedule_data[2])
                new_value = schedule_data[3]
                schedule_id = ElementId(Int64(schedule_data[1]))
                
                # update progress
                pb.update_progress(counter,  max_count)

                # get the schedule from revit
                schedule = doc.GetElement(schedule_id)

                print_header("Processing schedule with id: {} ({} of {})".format(schedule.Name, counter, max_count))
                
                # make sure schedule exists
                if not schedule:
                    print_error("Failed to get schedule with id: {} from revit".format(schedule_data[1]))
                    continue
                
                # get schedule name
                schedule_name = schedule.Name
                
                # get schedule filter
                schedule_filters = get_schedule_filters_by_field_name(schedule, SCHEDULE_FILTER_FIELD_NAME)
                if len(schedule_filters) == 0:
                    print_error("Schedule {} has no filters for field: {}".format(schedule_name, SCHEDULE_FILTER_FIELD_NAME))
                    continue

                schedule_filter = schedule_filters[0]
                if not schedule_filter:
                    print_error("Failed to get filter at index {} for schedule: {}".format(field_index ,schedule_name))
                    continue

                
                all_filters = schedule.Definition.GetFilters()
                filter_index = 0
                for filter in all_filters:
                    if filter.Equals(schedule_filter):
                        break
                    filter_index = filter_index + 1
                print("Found filter at index {} for schedule: {}".format(filter_index, schedule_name))

                # get schedule field
                #schedule_field = schedule.Definition.GetField(schedule_filter.FieldId)
                #schedule_field_name = schedule_field.GetName()
                
                # set up an action to change the filter value
                def action():
                    action_return_value = Result()
                    try:
                        action_return_value.append_message("Attempting filter to value {} at filter index {} for schedule: {}".format(new_value, field_index, schedule_name))
                        # set filter value
                        schedule_filter.SetValue(new_value)
                        # update the filter in the schedule
                        schedule.Definition.SetFilter(field_index,schedule_filter)
                        action_return_value.append_message("Set filter value {} at index {} for field {} in schedule: {}".format(schedule_data[3], field_index, SCHEDULE_FILTER_FIELD_NAME, schedule_name))
                    except Exception as e:
                        action_return_value.update_sep(
                            False, "Failed to write filter value with exception: {}".format(e)
                        )
                    return action_return_value
                    
               
                tranny = Transaction(doc, "Changing Schedule {} ".format(schedule_name))
                action_result = in_transaction(tranny, action)
                
                print(action_result.message)
                
                return_value.update(action_result)

                # update progress
                counter = counter + 1
                
                # cancelled?
                if pb.cancelled:
                    message = "User cancelled."
                    print(message)
                    return_value.update_sep(False, message=message)
                    # leave loop
                    break

    except Exception as e:
        message =  "Failed to write filter values with exception: {}".format(e)
        print_error(message)
        return_value.update_sep(
            False, message
        )

    #print("\n{}".format(return_value.message))
    print("Finished")

    return return_value