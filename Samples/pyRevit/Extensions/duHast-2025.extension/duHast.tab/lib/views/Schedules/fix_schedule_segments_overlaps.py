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
from schedules_ui import (
    get_split_schedules_from_user_dialogue, 
)

from duHast.Revit.Views.schedules_sheet_instances_move import  move_schedule_sheet_instances_in_x_until_no_overlap

from pyrevit.framework import Forms

DEBUG = True


def fix_schedule_segments_overlap_entry(doc, output, forms, debug=DEBUG):
    """
    Allows the user to select schedules which have segments with overlapping fields and fixes the overlaps by moving schedule segments horizontally until there are no more overlaps.
    
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
        print_header("Adjusting schedule overlaps...")

        # let the user select the schedules which may have split segments and are on sheets to update
        # update the segment locations of the selected schedules to fix the overlaps

        # get the user to select which schedules to fix the overlaps for
        schedules_to_update = get_split_schedules_from_user_dialogue(doc, forms, button_name="Select Split Schedules to Fix Possible Overlaps")
        if len(schedules_to_update) == 0:
            return_value.update_sep(
                status=False,
                message="No schedules selected for modification."
            )
            print_error("No schedules selected for modification. Exiting...")
            return return_value


        # set up a pyrevit progress bar
        with forms.ProgressBar(
            title="Adjusting schedules: {value} of {max_value}", cancellable=True
        ) as pb:
            
            progress_bar = ProgressPyRevit(pb)

            adjust_result =  move_schedule_sheet_instances_in_x_until_no_overlap(
                doc=doc,
                schedules=schedules_to_update,
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