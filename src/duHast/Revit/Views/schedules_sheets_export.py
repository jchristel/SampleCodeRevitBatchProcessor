"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to Revit view schedules of category sheet export to file. 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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
from duHast.Revit.Views.schedules_fields import schedule_contains_sheet_number_field, get_field_column_index_from_schedule_by_parameter_id, SHEET_NUMBER_PARAMETER_ID 
from duHast.Revit.Views.schedules_export import export_schedule_to_file

from duHast.Utilities.Objects.result import Result
from duHast.Utilities.directory_io import directory_exists, create_temp_directory, directory_delete_with_fallback
from duHast.Utilities.files_get import get_files_single_directory
from duHast.Utilities.files_io import get_file_name_without_ext
from duHast.Utilities.file_base_read_net import read_from_delimited_text_file


def filter_schedules_by_sheet_number_field(schedules):
    """
    Filters the given schedules to only those that contain a visible sheet number field.
    
    :param schedules: The list of schedules to filter.
    :type schedules: list[Autodesk.Revit.DB.ViewSchedule]

    :return: A list of schedules that contain the sheet number field.
    :rtype: list[Autodesk.Revit.DB.ViewSchedule]
    """

    filtered_schedules = []

    for schedule in schedules:
        # check if the schedule contains the sheet number field
        if schedule_contains_sheet_number_field(schedule = schedule, ignore_hidden_field=True):
            filtered_schedules.append(schedule)
    
    return filtered_schedules


def export_all_sheet_schedules_to_file( doc, directory_path, export_if_number_is_hidden = False):
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
            all_schedules = filter_schedules_by_sheet_number_field(all_schedules)

        # iterate through all schedules and export them to file
        for schedule in all_schedules:
            # get the file name from the schedule name
            file_name = schedule.Name + ".csv"
            file_path = os.path.join(directory_path, file_name)
            
            # export the schedule to file
            export_result = export_schedule_to_file(schedule, file_path)
            
            return_value.update(export_result)

        return return_value
    
    except Exception as e:
        return_value.update_sep(False, "Failed to export schedules to file: {e}".format(e=e))
        return return_value


def export_all_sheet_schedules_and_read_data_back(doc, export_if_number_is_hidden=False):
    """
    Exports all sheet schedules to file and reads the data back into a dictionary.

    :param export_if_number_is_hidden: Whether to export schedules even if the number is hidden.
    :type export_if_number_is_hidden: bool, optional

    :return: Result object containing success status, messages, and data.
    :rtype: duHast.Utilities.Objects.result.Result
    """

    return_value = Result()

    try:
        # set up a temporary directory to export the schedules to
        directory_path = create_temp_directory()
        
        # export all sheet schedules to file
        export_result = export_all_sheet_schedules_to_file(doc=doc, directory_path=directory_path, export_if_number_is_hidden=export_if_number_is_hidden)
        
        return_value.update(export_result)

        if return_value.status is False:
            return return_value

        # get all files in temp directory
        if directory_exists(directory_path) is False:
            return_value.update_sep(False, "Temporary directory does not exist: {directory_path}".format(directory_path=directory_path))
            return return_value
        
        # get all files in the directory with the specified filters
        files_found = get_files_single_directory(directory_path, file_prefix="", file_suffix="", file_extension=".csv")

        # check if any files were found
        if len(files_found) == 0:
            return_value.update_sep(False, "No files found in temporary directory: {directory_path}".format(directory_path=directory_path))
            
            # delete the temp directory
            delete_flag = directory_delete_with_fallback(directory_path)
            return_value.append_message("Deleted temporary directory: {directory_path} with status {flag}".format(directory_path=directory_path, flag=delete_flag))

            return return_value
        
        # read the data back into a dictionary
        data = {}

        for file_path in files_found:
            # attempt to read the file
            file_data_result = read_from_delimited_text_file(file_path)

            # check if the file was read successfully
            if file_data_result.status is False:
                return_value.update_sep(False, "Failed to read data from file: {file_path}".format(file_path=file_path))
                continue

            else:
                # log the success message
                return_value.append_message("Successfully read data from file: {file_path}".format(file_path=file_path))
                # store the data in the dictionary with the file name as the key
                file_name = get_file_name_without_ext(file_path)
                data[file_name] = file_data_result.result

        # delete the temporary directory
        delete_flag = directory_delete_with_fallback(directory_path)
        return_value.append_message("Deleted temporary directory: {directory_path} with status {flag}".format(directory_path=directory_path, flag=delete_flag))

        # return the data read
        return_value.result.append(data)
        return return_value
    
    except Exception as e:
        return_value.update_sep(False, "Failed to export and read data back: {e}".format(e=e))
        return return_value


def get_sheet_number_index_to_schedule_mapper(doc):
    """
    Creates a mapping of sheet number column index to their corresponding schedules in the document.

    :param doc: The Revit document containing the schedules.
    :type doc: Autodesk.Revit.DB.Document

    :return: A dictionary mapping sheet numbers to their corresponding schedules.
    :rtype: dict[str, Autodesk.Revit.DB.ViewSchedule]
    """

    return_value = Result()

    try:
        # get all sheet schedules in doc
        all_schedules = get_all_sheet_schedules(doc)

        # filter schedules to only those that have the sheet number field visible
        all_schedules = filter_schedules_by_sheet_number_field(all_schedules)

        # create a mapping of sheet numbers to schedules
        sheet_number_to_schedule_map = {}

        for schedule in all_schedules:
           column_index = get_field_column_index_from_schedule_by_parameter_id(schedule, SHEET_NUMBER_PARAMETER_ID )
           sheet_number_to_schedule_map[schedule.Name] = column_index
        
        return_value.result.append(sheet_number_to_schedule_map)
        return return_value
    
    except Exception as e:
        return_value.update_sep(False, "Failed to create sheet number column index to schedule mapper: {e}".format(e=e))
        return return_value