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
from duHast.Utilities.files_csv import read_csv_file
from duHast.Utilities.directory_io import create_directory
from duHast.Revit.Views.sheets import get_sheet_rev_by_sheet_name
from duHast.Utilities.utility import pad_single_digit_numeric_string
from duHast.Utilities.Objects import result as res


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
    :param file_extensions: The file extension. i.e 'sample[12].ifc'
    :type file_extensions: [str]
    :param revision_prefix: the character proceeding the revision information
    :type revision_prefix: str
    :param revision_suffix: the character following the revision information
    :type revision_suffix: str

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


def copy_exports(
    export_status, target_folder, file_extension, revision_prefix, revision_suffix
):
    """
    Copies files into a give folder.

    Copies new Exports into specified folder and strips away the revision information
    Used to maintain a current NWC and IFC file set

    :param export_status: Result class instance containing file path information.
    :type export_status:  :class:`.Result`
    :param target_folder: Fully qualified directory path to where files get copied to.
    :type target_folder: str
    :param file_extension: The file extension of files to be copied in format '.extension'
    :type file_extension: str
    :param revision_prefix: the character proceeding the revision information
    :type revision_prefix: str
    :param revision_suffix: the character following the revision information
    :type revision_suffix: str

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
                    new_name = get_export_file_name_without_revision(
                        file_name=export_name[1],
                        file_extensions=[file_extension],
                        revision_prefix=revision_prefix,
                        revision_suffix=revision_suffix,
                    )
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


def build_default_file_list(
    doc,
    revision_data_file_path,
    revit_file_name,
    splash_screen_name,
    revit_file_extension,
):
    """
    Reads file data from file and stores it in a global list.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param revision_data_file_path: _description_
    :type revision_data_file_path: _type_
    :param revit_file_name: _description_
    :type revit_file_name: _type_
    :param splash_screen_name: _description_
    :type splash_screen_name: _type_
    :param revit_file_extension: _description_
    :type revit_file_extension: _type_

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

    # will contain the old file name and the new file name (with revision data)
    matched_file_data = []
    marker_file_data = None
    # get the revision from title sheet
    rev = get_sheet_rev_by_sheet_name(doc, splash_screen_name)
    match = False
    # read current files
    file_list = read_current_file(revision_data_file_path)
    if file_list is not None and len(file_list) > 0:
        # loop over file data objects and search for match
        return_value.append_message("looking for match:".format(revit_file_name))
        for file_data in file_list:
            return_value.append_message(
                "starts with {}".format(file_data.existing_file_name)
            )
            if (
                revit_file_name.startswith(file_data.existing_file_name)
                and file_data.file_extension == revit_file_extension
            ):
                return_value.append_message("Found match!")
                match = True
                file_data.revision = rev  # update with latest revision from sheet
                # pad revision out to two digits if required
                file_data.revision = pad_single_digit_numeric_string(file_data.revision)
                # store updated file data to be written to marker file
                marker_file_data = file_data.get_data()

                # get new file name for saving as
                new_file_name = file_data.get_new_file_name()

                # build revision file name
                row_default_new = []
                row_default_new.append(file_data.existing_file_name)
                row_default_new.append(new_file_name)
                matched_file_data.append(row_default_new)

        if match == False:
            # check whether we found a match
            return_value.update_sep(False, "No file name match found in file list.")
    else:
        return_value.update_sep(False, "File data list is empty!")
    return return_value, matched_file_data, marker_file_data
