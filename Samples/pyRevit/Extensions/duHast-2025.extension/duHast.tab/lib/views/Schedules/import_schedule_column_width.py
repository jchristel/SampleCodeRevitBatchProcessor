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
from duHast.Revit.Views.Import.schedules_width_read_from_file import read_column_width_data_file

from schedules_ui import get_schedules_from_user_to_import


from pyrevit.framework import Forms

DEBUG = True


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
        print_header("Importing schedule column widths...")

        # let the user select the csf file to import schedules column width from
        # let the user select the schedules to which to import the column widths
        # update the column widths of the selected schedules based on the csv file

        # get the file path of the csv file to import from the user
        file_path = get_file_path_from_user(
            forms=forms, title="Select schedule width file", file_extension="csv"
        )
        if file_path is None:
            print("No file selected. Exiting.")
            return_value.update_sep(False, "No file selected. Exiting.")
            return return_value
    
        # read data from the csv file
        read_result = read_column_width_data_file(file_path)
        schedule_data_from_file = read_result.result[0]

        if not read_result.status:
            raise Exception(read_result.message)
        
        # get the user to select the schedules to update the column widths for, based on the schedules available in the file
        schedules_to_update = get_schedules_from_user_to_import(
            doc, 
            forms, 
            button_name="Select Schedules To Import Column Widths For",
            schedule_data=schedule_data_from_file)

        if len(schedules_to_update) == 0:
            return_value.update_sep(
                status=False,
                message="No schedules selected for import."
            )
            print_error("No schedules selected for import. Exiting...")
            return return_value

        if DEBUG:
            print("Schedules selected for import: {}".format(schedules_to_update))
            
        # set up a pyrevit progress bar
        with forms.ProgressBar(
            title="Importing schedules: {value} of {max_value}", cancellable=True
        ) as pb:
            pass
    
    except Exception as e:
        return_value.update_sep(
            status=False,
            message="Failed to import schedules column widths: {}".format(e)
        )
        

        print("Error: {}".format(e))

        return return_value