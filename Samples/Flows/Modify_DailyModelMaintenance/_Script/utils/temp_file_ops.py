"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Module containing file operations related to temp folder.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- copying files to temp
- copying files from temp
- deleting files in temp
- old unused temp folders
"""

#!/usr/bin/python
# -*- coding: utf-8 -*-
#
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

from duHast.Utilities.files_io import (
    copy_file
)

from duHast.Utilities.files_get import get_files_with_filter


def copy_files_from_output_to_temp(file_extension, output_to_console, output_folder,temp_folder):
    """
    Copies files with given extension from output folder to temp folder for processing.

    :param file_extension: file extension to filter files in output folder
    :param output_to_console: function to output messages to console
    :param output_folder: folder where files are currently located
    :param temp_folder: folder where files should be copied to for processing
    :return: exit code (0 for success, 1 for failure)
    """
    
    exit_code = 0
    # copy temp files from output folder to temp folder for processing
    try:
        # get .temp files in output folder
        temp_files = get_files_with_filter(
            output_folder,file_extension, "*"
        )

        all_files_copied = True
        # copy files to temp folder
        for temp_file in temp_files:

            # new file name in temp folder is the same as in output folder, just different path
            new_file_name =  os.path.join(temp_folder, os.path.basename(temp_file))

            # copy file to temp folder
            copy_result = copy_file(temp_file, new_file_name)
            if copy_result:
                output_to_console("Copied file: {} to temp folder for processing.".format(temp_file))
            else:
                all_files_copied = False
                output_to_console(
                    "Failed to copy file: {} to temp folder for processing.".format(
                        temp_file
                    )
                )

        if not all_files_copied:
            raise ValueError("Not all files were copied to temp folder for processing.")
        
    except Exception as e:
        output_to_console("Failed to copy files to temp folder: {}".format(e))
        exit_code = 1
    

    return exit_code


def copy_files_from_temp_to_output(file_extension, output_to_console, temp_folder, output_folder):
    """
    Copies files with given extension from temp folder to output folder after processing.

    :param file_extension: file extension to filter files in temp folder
    :param output_to_console: function to output messages to console
    :param temp_folder: folder where files are currently located for processing
    :param output_folder: folder where files should be copied to after processing
    :return: exit code (0 for success, 1 for failure)
    """

    exit_code = 0
    # copy temp files from temp folder to output folder after processing
    try:
        # get .temp files in temp folder
        temp_files = get_files_with_filter(
            temp_folder,file_extension, "*"
        )

        all_files_copied = True
        # copy files to output folder
        for temp_file in temp_files:

            # new file name in output folder is the same as in temp folder, just different path
            new_file_name =  os.path.join(output_folder, os.path.basename(temp_file))

            # copy file to output folder
            copy_result = copy_file(temp_file, new_file_name)
            if copy_result:
                output_to_console("Copied file: {} to output folder after processing.".format(temp_file))
            else:
                all_files_copied = False
                output_to_console(
                    "Failed to copy file: {} to output folder after processing.".format(
                        temp_file
                    )
                )
        if not all_files_copied:
            raise ValueError("Not all files were copied to output folder after processing.")
    except Exception as e:
        output_to_console("Failed to copy files to output folder: {}".format(e))
        exit_code = 1
    return exit_code


def delete_files_in_temp_folder(file_extension, output_to_console, temp_folder):
    """
    Deletes files with given extension in temp folder.

    :param file_extension: file extension to filter files in temp folder
    :param output_to_console: function to output messages to console
    :param temp_folder: folder where files should be deleted
    :return: exit code (0 for success, 1 for failure)
    """
    
    exit_code = 0
    # delete temp files in temp folder after processing
    try:
        # get .temp files in temp folder
        temp_files = get_files_with_filter(
            temp_folder,file_extension, "*"
        )

        all_files_deleted = True
        # delete files in temp folder
        for temp_file in temp_files:

            try:
                os.remove(temp_file)
                output_to_console("Deleted file: {} from temp folder after processing.".format(temp_file))
            except Exception as e:
                all_files_deleted = False
                output_to_console(
                    "Failed to delete file: {} from temp folder after processing. Error: {}".format(
                        temp_file, e
                    )
                )

        if not all_files_deleted:
            raise ValueError("Not all files were deleted from temp folder after processing.")
        
    except Exception as e:
        output_to_console("Failed to delete files from temp folder: {}".format(e))
        exit_code = 1
    

    return exit_code


def copy_all_to_temp(output_to_console, temp_folder, output_folder, temp_file_extension, report_file_extension, log_file_extension):
    exit_code = 0

    # copy temp files from output folder to temp folder for processing
    status_code_copy_temp_files = copy_files_from_output_to_temp(
        temp_file_extension,
        output_to_console,
        output_folder,
        temp_folder
    )

    if status_code_copy_temp_files != 0:
        output_to_console("Failed to copy temp files from output folder to temp folder for processing.")
        return status_code_copy_temp_files


    # copy csv files from output folder to temp folder for processing
    status_code_copy_csv_files = copy_files_from_output_to_temp(
        report_file_extension,
        output_to_console,
        output_folder,
        temp_folder
    )

    if status_code_copy_csv_files != 0:
        output_to_console("Failed to copy csv files from output folder to temp folder for processing.")
        return status_code_copy_csv_files

    # copy overall log file to temp folder for processing
    status_code_copy_log_file = copy_files_from_output_to_temp(
        log_file_extension,
        output_to_console,
        output_folder,
        temp_folder
    )

    if status_code_copy_log_file != 0:
        output_to_console("Failed to copy log file from output folder to temp folder for processing.")
        return status_code_copy_log_file

    return exit_code


def copy_all_files_from_temp(output_to_console, temp_folder, output_folder, report_file_extension, log_file_extension):
    
    exit_code = 0

    # copy log file back to output folder
    status_log_file_back =  copy_files_from_temp_to_output(
        log_file_extension, 
        output_to_console, 
        temp_folder, 
        output_folder,
        )

    if status_log_file_back != 0:
        output_to_console("Failed to copy log file back to output folder.")
        exit_code = exit_code + status_log_file_back

    # copy csv files back to output folder
    status_csv_files_back = copy_files_from_temp_to_output(
        report_file_extension, 
        output_to_console, 
        temp_folder, 
        output_folder,
        )

    if status_csv_files_back != 0:
        output_to_console("Failed to copy csv files back to output folder.")
        exit_code =  exit_code + status_csv_files_back
    
    return exit_code


def clean_temp_folder(output_to_console, temp_folder,  temp_file_extension, report_file_extension, log_file_extension):
    
    # delete everything in temp including the temp folder if so far everything is ok
    exit_code = 0
    # delete temp files in temp folder
    status_delete_temp_files = delete_files_in_temp_folder(
        temp_file_extension, output_to_console, temp_folder
    )

    if status_delete_temp_files != 0:
        output_to_console("Failed to delete temp files in temp folder.")
        exit_code =  exit_code + status_delete_temp_files

    # delete log file
    status_delete_temp_log_file = delete_files_in_temp_folder(
        log_file_extension,output_to_console, temp_folder
    )

    if status_delete_temp_log_file != 0:
        output_to_console("Failed to delete log file in temp folder.")
        exit_code =  exit_code + status_delete_temp_log_file

    # delete csv files
    status_delete_temp_csv_files = delete_files_in_temp_folder(
        report_file_extension, output_to_console, temp_folder
    )

    if status_delete_temp_csv_files != 0:
        output_to_console("Failed to delete csv files in temp folder.")
        exit_code =  exit_code + status_delete_temp_csv_files

    # delete temp folder
    try:
        os.rmdir(temp_folder)
        output_to_console("Deleted temp folder: {}".format(temp_folder))
    except Exception as e:
        output_to_console("Failed to delete temp folder: {} with error: {}".format(temp_folder, e))
    
    return exit_code

