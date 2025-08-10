"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to Revit view schedules of category sheet export to file. 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
#
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

import os

from duHast.Revit.Views.schedules import  get_all_sheet_schedules
from duHast.Revit.Views.schedules_export import export_schedule_to_file
from duHast.Utilities.Objects.result import Result
from duHast.Utilities.directory_io import directory_exists


def export_all_sheet_schedules_to_file( directory_path, export_if_number_is_hidden = False):
    """
    Exports all schedules that are placed on sheets to file.
    
    :param directory_path: The directory path to export the schedules to.
    :type directory_path: str
    :param export_if_number_is_hidden: Whether to export schedules even if the number is hidden.
    :type export_if_number_is_hidden: bool, optional
    
    :return: Result object containing success status and messages.
    :rtype: duHast.Utilities.Objects.result.Result
    """
    
    return_value = Result()

    try:

        # check if the directory exists
        if directory_exists(directory_path) is False:
            return_value.update_sep(False, "Directory does not exist: {directory_path}".format(directory_path=directory_path))
            return return_value

        # get all sheet schedules in doc
        all_schedules = get_all_sheet_schedules(doc)

        # check if there are any schedules to export
        if len(all_schedules) == 0:
            return_value.update_sep(False, "No sheet schedules in document.")
            return return_value
        
        # check if schedules need to be filtered ( export only if sheet number field is not hidden)
        if export_if_number_is_hidden is False:
            # filter schedules to only those that have the sheet number field visible
            pass

        # iterate through all schedules and export them to file
        for schedule in all_schedules:
            # get the file name from the schedule name
            file_name = schedule.Name.replace(" ", "_") + ".csv"
            file_path = os.path.join(directory_path, file_name)
            
            # export the schedule to file
            export_result = export_schedule_to_file(schedule, file_path)
            
            return_value.update(export_result)

        return return_value
    
    except Exception as e:
        return_value.update_sep(False, "Failed to export schedules to file: {e}".format(e=e))
        return return_value