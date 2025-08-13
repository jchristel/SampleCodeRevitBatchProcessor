"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to Revit view schedules export to file. 
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

from duHast.Utilities.Objects.result import Result
from duHast.Utilities.files_io import get_directory_path_from_file_path, get_file_name_without_ext, get_file_extension
from duHast.Utilities.directory_io import directory_exists


from Autodesk.Revit.DB import ExportColumnHeaders, ExportTextQualifier, ViewSchedule, ViewScheduleExportOptions

def export_schedule_to_file(schedule, file_path, field_delimiter=",", export_title=False, export_column_headers = ExportColumnHeaders.None ,export_text_qualifier=ExportTextQualifier.DoubleQuote):

    """
    Exports a Revit schedule to a file.

    :param schedule: The schedule to export.
    :type schedule: Autodesk.Revit.DB.ViewSchedule
    :param file_path: The file path to export the schedule to.
    :type file_path: str
    :param field_delimiter: The delimiter to use between fields in the exported file.
    :type field_delimiter: str, optional
    :param export_title: Whether to include the schedule title in the exported file.
    :type export_title: bool, optional
    :param export_column_headers: The type of column headers to include in the exported file.
    :type export_column_headers: Autodesk.Revit.DB.ExportColumnHeaders, optional
    :param export_text_qualifier: The text qualifier to use in the exported file.
    :type export_text_qualifier: Autodesk.Revit.DB.ExportTextQualifier, optional
    
    :return: Result object containing success status and messages.
    :rtype: duHast.Utilities.Objects.result.Result
    """

    return_value = Result()

    try:

        # check if the schedule is a view schedule instance
        if not isinstance(schedule, ViewSchedule):
            return_value.update_sep(False, "Provided schedule is not a valid ViewSchedule instance. Got {} instead.".format(type(schedule).__name__))
            return return_value

        # check if a file path was provided
        if not file_path:
            return_value.update_sep(False, "No file path provided for schedule export.")
            return return_value
        
        # check if file_path is a string
        if not isinstance(file_path, str):
            return_value.update_sep(False, "File path must be a string. Got {} instead.".format(type(file_path).__name__))
            return return_value


        # set up an schedule export options object with default values
        export_options = ViewScheduleExportOptions()
        export_options.FieldDelimiter = field_delimiter
        export_options.Title = export_title
        export_options.TextQualifier = export_text_qualifier
        export_options.ColumnHeaders = export_column_headers

        # get directory from file_path
        directory_path = get_directory_path_from_file_path(file_path)

        # check if the directory exists
        if not directory_exists(directory_path):
            return_value.update_sep(False, "Directory does not exist: {directory}".format(directory=directory_path))
            return return_value

        # get the file name from the file_path
        file_name = get_file_name_without_ext(file_path)
        # add the extension back in
        file_extension = get_file_extension(file_path)
        file_name += file_extension

        # export the schedule to a file
        schedule.Export(directory_path, file_name, export_options)

        return_value.append_message( "Schedule exported successfully to: {file}".format(file=file_path))
        return return_value

    except Exception as e:
        return_value.update_sep(False, "Failed to export schedule to file: {e}".format(e=e))
        return return_value