#!/usr/bin/python
# -*- coding: utf-8 -*-
# License:
#
#
# Revit Batch Processor Sample Code
#
# Copyright (c) 2020  Jan Christel
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#


import docFile as df

# import from library
from duHast.Utilities.files_io import get_file_extension, copy_file, file_exist
from duHast.Utilities.files_get import get_files
from duHast.Utilities.files_csv import read_csv_file, write_report_data_as_csv
from duHast.Utilities.directory_io import create_directory
from duHast.Utilities.Objects import result as res


def read_marker_files_from_revit_processed(marker_dir_path, marker_file_extension):
    """
    Reads marker files into docfile objects.

    :param marker_dir_path: Fully qualified directory path containing marker files.
    :type marker_dir_path: str
    :param marker_file_extension: marker file extension in format ".ext"
    :type marker_file_extension: str

    :return:
        Result class instance.

        - Read status returned in result.status. False if an exception occurred, otherwise True.
        - result.message will contain 'Read marker file(s)'.
        - result.result will contain list of docFile objects

        On exception:

        - result.status (bool) will be False.
        - result.message will contain the exception message.
        - result.result will be an empty list.

    :rtype: :class:`.Result`
    """

    return_value = res.Result()
    marker_file_data = []
    # get all text files in location
    marker_files = get_files(marker_dir_path, marker_file_extension)
    if len(marker_files) > 0:
        try:
            for mf in marker_files:
                rows = read_csv_file(mf)
                for row in rows:  # each row is a list
                    # read information into class
                    marker_file_data.append(df.docFile(row))
        except Exception as e:
            return_value.update_sep(
                False,
                "Failed to read marker file from Revit export with exception: {}".format(
                    e
                ),
            )
    return_value.update_sep(True, "Read marker file(s)")
    return_value.result = marker_file_data
    return return_value


def create_bim360_out_folder(target_directory, new_subdirectory_name):
    """
    Sets up the directory for files to be uploaded to bim360 or acc

    :param target_directory: The fully qualified directory path in which the new sub directory is to be created.
    :type target_directory: str
    :param new_subdirectory_name: The new sub directory name
    :type new_subdirectory_name: str
    :return: True if folder was created successfully or already existed, Otherwise False
    :rtype: bool
    """

    flag = create_directory(target_directory, new_subdirectory_name)
    return flag


def get_export_file_name_without_revision(
    file_name, file_extensions, revision_prefix, revision_suffix
):
    """
    Strips the revision and extension of a file name (used for current exports folders of IFC and NWC and Revit)

    :param file_name: The file name including extension. i.e 'sample[12].ifc'
    :type file_name: str

    :return: The file name without the revision and extension. i.e. 'sample'
    :rtype: str
    """

    # strip file extension (in all 3 cases 4 characters long)
    # if not an ifc, nwc or revit file, return name unchanged.
    file_extension = get_file_extension(file_extensions)

    if file_extension in file_extensions:
        file_name = file_name[0:-4]
        # check if file name contains revision (format is: [xx])
        if revision_prefix in file_name and revision_suffix in file_name:
            index_rev_start = file_name.find(revision_prefix)
            index_rev_end = file_name.find(revision_suffix)
            file_name = file_name[0:index_rev_start] + file_name[index_rev_end + 1 :]
        else:
            # just remove extension
            file_name = file_name[0:-4]
    return file_name


# copies new Exports into specified folder and strips away the revision information
# used to maintain a current NWC and IFC file set
def copy_exports(export_status, target_folder, file_extension):
    """
    Copies files into a give folder.

    :param export_status: Result class instance containing file path information.
    :type export_status:  :class:`.Result`
    :param target_folder: Fully qualified directory path to where files get copied to.
    :type target_folder: str
    :param file_extension: The file extension of files to be copied in format '.extension'
    :type file_extension: str

    :return:
        Result class instance.

        - Read status returned in result.status. False if an exception occurred, otherwise True.
        - result.message will contain message(s) in format: 'Copied: currentFullFileName to newFileName'
        - result.result will be an empty list.

        On exception:

        - result.status (bool) will be False.
        - result.message will contain the exception message.
        - result.status will be an empty list.

    :rtype: :class:`.Result`
    """

    return_value = res.Result()
    if export_status.status == True:
        if export_status.result is not None and len(export_status.result) > 0:
            for export_name in export_status.result:
                # check if file exists...some files will not be exported if the view is empty!
                current_full_file_name = export_name[0] + "\\" + export_name[1]
                # Output('current file name from status: ' + currentFullFileName)
                if file_exist(current_full_file_name):
                    new_name = get_export_file_name_without_revision(export_name[1])
                    new_file_name = target_folder + "\\" + new_name + file_extension
                    flagCopy = copy_file(current_full_file_name, new_file_name)
                    if flagCopy:
                        return_value.append_message(
                            "Copied: {} to {}".format(
                                current_full_file_name, new_file_name
                            )
                        )
                    else:
                        return_value.status = False
                        return_value.append_message(
                            "Failed to Copy: {} to {}".format(
                                current_full_file_name, new_file_name
                            )
                        )

                else:
                    return_value.append_message(
                        "File not found: {}".format(current_full_file_name)
                    )
        else:
            return_value.update_sep(True, "No files copied since nothing was exported")
    else:
        return_value.update_sep(True, "No files copied since nothing was exported")
    return return_value


# common stuff


def read_current_file(revision_data_path):
    """
    Read the current revision data file located in script location

    :param revision_data_path: fully qualified file path to revision data file
    :type revision_data_path: str
    :return: a list containing current file data
    :rtype: [docFile]
    """

    reference_list = []
    try:
        rows = read_csv_file(revision_data_path)
        for row in rows:
            reference_list.append(df.docFile(row))
    except Exception as e:
        print(str(e))
        reference_list = []
    return reference_list


def write_rev_marker_file(fully_qualified_path, file_data):
    """
    Writes out revision marker file

    :param fully_qualified_path: Fully qualified file path of revision marker file.
    :type fully_qualified_path: str
    :param file_data: File data to be written to file.
    :type file_data: [str]

    :return:
        Result class instance.

        - Write status returned in result.status. False if an exception occurred, otherwise True.
        - result.message will contain message(s) in format: 'Successfully wrote marker file: marker file name'
        - result.result will be an empty list.

        On exception:

        - result.status (bool) will be False.
        - result.message will contain the exception message.
        - result.status will be an empty list.

    :rtype: :class:`.Result`
    """

    return_value = res.Result()
    if len(file_data) > 0:
        try:
            write_report_data_as_csv(fully_qualified_path, [], [file_data])
            return_value.append_message = "Successfully wrote marker file: {}".format(
                fully_qualified_path
            )
        except Exception as e:
            return_value.update_sep(
                False,
                "Failed to write data file! {} with exception: {}".format(
                    fully_qualified_path, e
                ),
            )
    return return_value
