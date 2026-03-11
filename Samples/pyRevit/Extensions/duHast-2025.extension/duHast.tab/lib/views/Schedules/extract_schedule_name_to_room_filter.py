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
from duHast.Revit.Common.transaction import in_transaction

from schedules_ui import get_schedules_from_user, get_schedule_name_prefix_dialogue

SCHEDULE_FILTER_FIELD_NAME = "Room: Number"

from Autodesk.Revit.DB import Element, Transaction

DEBUG = False

def get_room_number_from_schedule_name(schedule_name, prefix):

    """
    Extracts the room number from the schedule name based on the provided prefix.
    :param schedule_name: Name of the schedule.
    :type schedule_name: str
    :param prefix: Prefix after which the room number starts in the schedule name.
    :type prefix: str
    :return:
        Room number extracted from the schedule name based on the provided prefix. If no room number could be extracted, returns None.
    :rtype: str or None
    """
    try:
        # find the index of the prefix in the schedule name ,but ignore case sensitivity
        prefix_index = schedule_name.lower().find(prefix.lower())
        if prefix_index != -1:
            room_number_start_index = prefix_index + len(prefix)
            room_number = schedule_name[room_number_start_index:]
            return room_number.strip()  # remove any leading/trailing whitespace
        else:
            return None
    except Exception as e:
        print_error("Failed to extract room number from schedule name: {} with exception: {}".format(schedule_name, e))

    return None


def extract_room_filter_values_from_schedules_name_and_update_room_filter_entry(doc, output, forms):
    """
    Extracts the room filter value from schedules name and updates the room number filter value accordingly.
   
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param output: pyRevit output
    :type output: pyRevit output module
    :param forms: pyRevit forms
    :type forms: pyRevit forms module

    :return:
        Result class instance.

        - result.status (bool) True if room numbers where extracted successfully and applied to room number filter value successfully, otherwise False.
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

        schedule_of_interest = get_schedules_from_user(doc, forms, "Select schedules to extract room filter values from")
        if schedule_of_interest is None or len(schedule_of_interest) == 0:
            message = "No valid schedules selected"
            print(message)
            return_value.update_sep(False, message)
            return return_value
        
        # get the schedule name prefix after which the room number starts from the user
        schedule_prefix = get_schedule_name_prefix_dialogue()
        if schedule_prefix is None:
            message = "No valid schedule name prefix provided"
            print(message)
            return_value.update_sep(False, message)
            return return_value
        
        # what happens if the room number starts immediately at the start of the schedule name?

        #set up a pyRevit progress bar
        with forms.ProgressBar(
            title="Updating: {value} of {max_value}",
            cancellable=True,
        ) as pb:
            
            print_header("Extracting and updating schedule filter values:")

            max_count = len(schedule_of_interest)
            schedule_counter = 1
            # get room filter values from schedules
            for schedule in schedule_of_interest:

                # update the progress bar
                pb.update_progress(schedule_counter, max_count)
                schedule_name = Element.Name.GetValue(schedule)

                print_header("Processing schedule: {} ({} of {})".format(schedule_name, schedule_counter, max_count))

                # extract the room number from the schedule name based on the provided prefix
                room_number_from_schedule_name = get_room_number_from_schedule_name(schedule_name, schedule_prefix)
                if room_number_from_schedule_name is None or len(room_number_from_schedule_name) == 0:
                    message = ("No room number extracted from schedule name: {} based on provided prefix: {}. Skipping".format(schedule_name, schedule_prefix))
                    print(message)
                    return_value.append_message(message)
                    # skip schedules where no room number could be extracted from the name based on the provided prefix
                    continue

                if schedule.Definition.GetFilterCount() > 0:
                   
                    filters = schedule.Definition.GetFilters()

                    filter_counter = 0
                    for filter in filters:
                        schedule_field = schedule.Definition.GetField(filter.FieldId)
                        schedule_field_name = schedule_field.GetName()

                        # check if this is the room number filter by comparing the field name to the expected room number field name
                        if schedule_field_name == SCHEDULE_FILTER_FIELD_NAME:
                        
                            # update the filter value with the room number extracted from the schedule name
                            # set up an action to change the filter value
                            def action():
                                action_return_value = Result()
                                try:
                                    # set filter value
                                    filter.SetValue(room_number_from_schedule_name)
                                    # update the filter in the schedule
                                    schedule.Definition.SetFilter(filter_counter, filter)
                                    action_return_value.append_message("Set filter value {} for field {} in schedule: {}".format(room_number_from_schedule_name, schedule_field_name, schedule_name))
                                except Exception as e:
                                    action_return_value.update_sep(
                                        False, "Failed to write filter value with exception: {}".format(e)
                                    )
                                return action_return_value
                                
                            # set up a transaction to change the filter value
                            tranny = Transaction(doc, "Changing Schedule {} ".format(schedule_name))
                            action_result = in_transaction(tranny, action)

                            # give user feedback
                            if action_result.status:
                                print(action_result.message)
                            else:
                                print_error(action_result.message)

                            return_value.update(action_result)
                            break
                        filter_counter = filter_counter +1
                else:
                    message = ("Schedule {} has no filters".format(schedule.Name))
                    print_error(message)
                    return_value.append_message(message)
                
                # update schedule counter
                schedule_counter += 1

                # check if cancelled
                if pb.cancelled:
                    print("Export cancelled by user")
                    return_value.update_sep(False, "Export cancelled by user")
                    return return_value

    except Exception as e:
        message = "Failed to write filter values with exception: {}".format(e)
        print_error (message)
        return_value.update_sep(
            False, message
        )

    if DEBUG:
        print("\n{}".format(return_value.message))
    print("Finished")

    return return_value