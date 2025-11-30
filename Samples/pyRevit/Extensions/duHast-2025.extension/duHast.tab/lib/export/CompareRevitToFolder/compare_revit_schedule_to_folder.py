#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2024, Jan Christel
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

from duHast.Utilities.Objects.result import Result
from duHast.pyRevit.console_output import print_header, print_error
from duHast.Utilities.files_get import get_files_from_directory_walker_with_filters_simple
from duHast.Revit.Views.schedules_sheets_export import export_all_sheet_schedules_and_read_data_back

from export.CompareRevitToFolder.ui_data_get import get_schedule_name_from_user, get_docs_folder_path_from_user


DEBUG = False

# parameter names which combined can be used to identify sheet number
DOC_NUMBER_PARAMETER_NAMES = ["Sheet Number", "SHEET NUMBER", "SHEET_NO", "SHEET NO.", "SHEETNO"]


def get_file_name_to_full_path_dict(files):
    """
    Gets a dictionary mapping file names to full paths.

    :param files: List of full file paths.
    :type files: list str
    :return: Dictionary mapping file names to full paths.
    :rtype: dict
    """

    file_name_to_full_path_dict = {}

    for file_path in files:
        # extract file name from full path
        file_name = os.path.basename(file_path)
        file_name_to_full_path_dict[file_name] = file_path

    return file_name_to_full_path_dict

def get_full_sheet_number_from_data(schedule_data):

    """
    Gets full sheet number from schedule data.
    Assume for now the full sheet number is in the first two columns. do fancy logic later.

    :param schedule_data: Schedule data extracted from Revit.
    :type schedule_data: list of strings
    :return: list of Full sheet numbers.
    :rtype: list of str
    """

    sheet_numbers = []

    # loop over all rows in schedule data
    for row in schedule_data:

        # skip any dodgy rows
        if len(row) < 2:
            continue

        # get the first column value as sheet number
        sheet_number = row[0] + row[1]
        sheet_numbers.append(sheet_number)

    return sheet_numbers


def compare_schedule_data_to_files(schedule_data, files):
    """
    Compares schedule data to files.

    :param schedule_data: Schedule data extracted from Revit.
    :type schedule_data: dict
    :param files: List of files to compare against.
    :type files: list str
    :return: Result object with status and message.
    :rtype: Result
    """

    # set up a status tracker
    return_value = Result()

    try:
        
        #extract the file name from the full path
        files_dic =  get_file_name_to_full_path_dict(files)

        # build sheet numbers from schedule data
        sheet_numbers_from_schedule = get_full_sheet_number_from_data(schedule_data)

        # sort sheet numbers
        sheet_numbers_from_schedule = sorted(sheet_numbers_from_schedule)

        # st up a dictionary containing the matches
        matched_sheets_dict = {}

        # loop over sheet numbers and check if corresponding file exists
        for sheet_number in sheet_numbers_from_schedule:

            # initialize list in dict for sheet number, any empty list means no match found
            matched_sheets_dict[sheet_number] = []

            # loop over all files to find match
            for incoming_file_name, incoming_file_path in  files_dic.items():
                # check if the file name starts with the sheet number
                if incoming_file_name.startswith(sheet_number):
                    # match found
                    if DEBUG:
                        print_header("Match found for sheet number: {}".format(sheet_number))
                        print(incoming_file_name)
                    
                    # add to matched sheets dict
                    matched_sheets_dict[sheet_number].append(incoming_file_path)
                    
        no_matches_found =[]
        # process the matched sheets dict to determine overall status
        for sheet_number, matched_files in matched_sheets_dict.items():
            if len(matched_files) == 0:
                # no match found for this sheet number
                message = "No matching file found for sheet number"
                no_matches_found.append("{} {}".format(sheet_number, message))
                if DEBUG:
                    print_error(message)
            elif len(matched_files) > 1:
                # multiple matches found for this sheet number
                message = "Multiple matching files found for sheet number: {}".format(matched_files)
                no_matches_found.append("{} {}".format(sheet_number, message))
                if DEBUG:
                    print_error(message)
            else:
                # exactly one match found, all good
                print("Matched sheet number: {} to file: {}".format(sheet_number, matched_files[0]))
        
        if len(no_matches_found) > 0:
            # sort the issues
            no_matches_found = sorted(no_matches_found)
            message = "Comparison completed with issues:\n" + "\n".join(no_matches_found)
            return_value.update_sep(False, message)
        
    except Exception as e:
        # handle any exceptions that occur during the export process
        message = "An error occurred while comparing schedule data to files: {}".format(e)
        return_value.update_sep(
            False, message
        )
        print_error(message)
    
    print("\nFinished comparing schedule data to files.")
    return return_value


def compare_entry(doc, output, forms):
    """
    Exports sheets to pdf and dwg files.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param output: pyRevit output.
    :type output: pyRevit.output
    :param forms: pyRevit forms.
    :type forms: pyRevit.forms
    :return: Result object with status and message.
    :rtype: Result
    """

    # set up a status tracker
    return_value = Result()

    try:
       
        # get user input for schedule name
        schedule_name_result = get_schedule_name_from_user(doc, forms)

        if not schedule_name_result.status:
            return_value.update_sep(False, schedule_name_result.message)
            if DEBUG:
                print_error(schedule_name_result.message)   
            return return_value

        # get the selected schedule name
        schedule_name = schedule_name_result.result[0]

        if DEBUG:
            print_header("Selected schedule name")
            print(schedule_name)

        # get folder path from usr containing pdfs to compare to
        docs_folder_result = get_docs_folder_path_from_user(forms)
        if not docs_folder_result.status:
            return_value.update_sep(False, docs_folder_result.message)
            if DEBUG:
                print_error(docs_folder_result.message)   
            return return_value
        
        # get the selected folder path
        docs_folder_path = docs_folder_result.result[0]

        if DEBUG:
            print_header("Selected folder path")
            print(docs_folder_path)

        # export and read the schedule content
        schedules_content_result = export_all_sheet_schedules_and_read_data_back(doc)
        if not schedules_content_result.status:
            return_value.update_sep(False, schedules_content_result.message)
            if DEBUG:
                print_error("exporting schedules: {}".format(schedules_content_result.message))
            return return_value
        
        # get the actual schedule data
        schedule_data = schedules_content_result.result[0][schedule_name]

        if DEBUG:
            print_header("Schedule data extracted")
            print(schedule_data)
        else:
            print("\nExtracted schedule data for schedule: {} found {} rows.".format(schedule_name, len(schedule_data)))

        # get the pdf files in folder
        files = get_files_from_directory_walker_with_filters_simple(docs_folder_path, ".pdf")

        if len(files) == 0:
            message = "No pdf files found in folder: {}".format(docs_folder_path)
            return_value.update_sep(False, message)
            if DEBUG:
                print_error(message)   
            return return_value
        
        if DEBUG:
            print_header("PDF files found")
            for f in files:
                print(f)
        else:
            print("\nFound {} pdf files in folder: {}".format(len(files), docs_folder_path))
        
        print_header("Comparing files to schedule data...")

        # compare each file to schedule data
        compare_result = compare_schedule_data_to_files(schedule_data, files)
        if not compare_result.status:
            return_value.update_sep(False, compare_result.message)
            print_error(compare_result.message)   
            return return_value
        else:
            print("\nAll files matched successfully to schedule data.")
            print(compare_result.message)
        
    except Exception as e:
        # handle any exceptions that occur during the export process
        message = "An error occurred while comparing: {}".format(e)
        return_value.update_sep(
            False, message
        )
        print_error(message)


    print("\nFinished comparing files to schedule.")

    return return_value