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

from duHast.Utilities.Objects.result import Result
from duHast.Utilities.files_io import file_move, get_file_name_without_ext

from duHast.Revit.Family.Utility.family_copy_directive_utils import get_copy_directives

from duHast.Revit.Family.Data.Objects.family_directive_copy import FamilyDirectiveCopy
from duHast.Utilities.files_get import get_files_single_directory
from duHast.Utilities.files_io import file_exist

# post process tasks
# - move original families into back up directory
# - copy updated families into library directory


def move_files(files, destination_directory, output):
    """
    Moves files to the specified destination directory.

    :param files: List of file paths to be moved.
    :type files: list[str]
    :param destination_directory: Directory where the files will be moved.
    :type destination_directory: str
    :param output: Output function to log messages.
    :type output: function
    
    :return: True if all files were moved successfully, False otherwise.
    :rtype: bool
    """
    overall_move_flag = True
    for file in files:
        file_name =  get_file_name_without_ext(file)
        destination_file = os.path.join(destination_directory, file_name + file[-4:])  # keep the original file extension
        move_flag = file_move(file, destination_file)

        output("Moving file: {} to {} with result: {}".format(file, destination_file,  move_flag))
        overall_move_flag = overall_move_flag and move_flag
    
    return overall_move_flag


def get_part_atom_files_from_families(file_path):
    """
    Gets part atom files from the specified family file path.

    :param file_path: list of Path to the family files.
    :return: List of part atom files.
    """
    part_atom_files = []

    for family_path in file_path:
        part_atom_file_path = family_path.replace(".rfa", ".xml")
        if file_exist(part_atom_file_path):
            part_atom_files.append(part_atom_file_path)
    
    return part_atom_files


def move_original_families_to_backup_directory(family_copy_directive_directory, backupPath, output):
    """
    Moves original families from the library path to the backup path.

    :param family_copy_directive_directory: Directory containing family copy directives.
    :type family_copy_directive_directory: str
    :param backupPath: Path to the backup directory where families will be moved.
    :type backupPath: str
    :param output: Output function to log messages.
    :type output: function

    :return: Result object indicating success or failure of the operation.
    :rtype: Result
    """

    return_value = Result()

    try:
        if not os.path.exists(backupPath):
            os.makedirs(backupPath)
            return_value.append_message("Backup directory created: {}".format(backupPath))
    except Exception as e:
        return_value.update_sep(False, "Failed to create backup directory: {}".format(str(e)))
        return return_value
    
    output("Backup directory: {}".format(backupPath))

    # read copy directives
    files = get_files_single_directory(
        family_copy_directive_directory,  
        FamilyDirectiveCopy.COPY_DIRECTIVE_FILE_NAME_PREFIX, 
        "", 
        FamilyDirectiveCopy.COPY_DIRECTIVE_FILE_EXTENSION
    )
        
    if len(files) == 0:
        return_value.update_sep(False, "No copy directives found in directory: {}".format(family_copy_directive_directory))
        return return_value
    
    output("Found copy directives files: {}".format(len(files)))

    # get copy directives
    copy_directives = get_copy_directives(files)
    if copy_directives is None or len(copy_directives) == 0:
        return_value.update_sep(False, "Failed to get copy directives from files: {}".format(files))
        return return_value
    
    output("Copy directives: {}".format(len(copy_directives)))

    # build list of unique source files
    files_to_copy = []

    for copy_directive in copy_directives:
        if copy_directive.source_file_path not in files_to_copy:
            files_to_copy.append(copy_directive.source_file_path)
    
    # add part atom files if they exists
    part_atom_path = get_part_atom_files_from_families(files_to_copy)
    if part_atom_path is not None and len(part_atom_path) > 0:
        files_to_copy += part_atom_path

    # attempt to move files to backup directory
    try:

        move_flag_rfa = move_files(files_to_copy, backupPath, output)
        if not move_flag_rfa:
            return_value.update_sep(False, "Failed to move original families to backup directory: {}".format(backupPath))
        else:
            return_value.update_sep(True, "Moved original families to backup directory: {}".format(backupPath))

    except Exception as e:
        return_value.update_sep(False, "Failed to move original families to backup directory: {}".format(e))
        return return_value
    
    return return_value


def copy_new_families_to_library(output_path, library_path, output):
    """
    Copies new families from the output path to the library path.
    :param output_path: Path where new families are located.
    :type output_path: str
    :param library_path: Path to the library where families will be copied.
    :type library_path: str
    :param output: Output function to log messages.
    :type output: function

    :return: Result object indicating success or failure of the operation.
    :rtype: Result
    """

    return_value = Result()

    try:
        # get all rfa and text files
        files = get_files_single_directory(output_path, "", "",".rfa")
        files += get_files_single_directory(output_path, "", "",".txt")
        if len(files) == 0:
            return_value.update_sep(False, "No new families found in output directory: {}".format(output_path))
            return return_value

        # copy files to library path
        move_flag = move_files(files, library_path, output)
        
        if not move_flag:
            return_value.update_sep(False, "Failed to copy new families to library: {}".format(library_path))
            return return_value
        else:
            return_value.update_sep(True, "Copied new families to library: {}".format(library_path))
        return return_value
    except Exception as e:
        return_value.update_sep(False, "Failed to copy new families to library: {}".format(str(e)))
        return return_value
    

def post_process_family(output_path, library_path, backup_directory_path, output):
    """
    Post-process function to handle the final steps after family processing.

    This function copies new families to the library and moves original families to a backup directory.

    :param output_path: Path where new families are located.
    :type output_path: str
    :param library_path: Path to the library where new families will be copied to.
    :type library_path: str
    :param backup_directory_path: Path to the backup directory where original families will be moved.
    :type backup_directory_path: str

    :return: Result object indicating the success or failure of the post-processing step.
    :rtype: Result
    """

    return_value = Result()
    try:
        copy_result = copy_new_families_to_library(output_path, library_path, output)
        if copy_result.status is False:
            return_value.update_sep(
                False,
                "Failed to copy new families to library: {}".format(copy_result.message),
            )
            output("Failed to copy new families to library: {}".format(copy_result.message))
        else:
            return_value.append_message(
                "Successfully copied new families to library: {}".format(library_path)
            )
            output("Successfully copied new families to library: {}".format(library_path))
        
        backup_result = move_original_families_to_backup_directory(
            output_path, backup_directory_path, output
        )

        if backup_result.status is False:
            return_value.update_sep(
                False,
                "Failed to move original families to backup directory: {}".format(backup_result.message),
            )
            output("Failed to move original families to backup directory: {}".format(backup_result.message))
        else:
            return_value.append_message(
                "Successfully moved original families to backup directory: {}".format(backup_directory_path)
            )
            output("Successfully moved original families to backup directory: {}".format(backup_directory_path))

    except Exception as e:
        return_value.update_sep(
            False,
            "Failed to complete post process: {}".format(e),
        )
        output("Failed to complete post process: {}".format(e))
    
    output("Finished!")
    return return_value