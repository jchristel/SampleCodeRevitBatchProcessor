"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Module containing functions relating to family type xml file creation.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Reports:

- all family located in library folder(s)

"""

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
import datetime
import tempfile

from duHast.UI.file_list import get_revit_files
from duHast.Utilities.files_io import get_file_name_without_ext, file_exist
from duHast.Utilities.files_xml import read_xml_file
from duHast.Utilities.directory_io import directory_exists
from duHast.Utilities.Objects.timer import Timer
from duHast.Utilities.Objects.result import Result
from duHast.UI.Objects.ProgressBase import ProgressBase


def get_families_from_directory(directory):
    """
    Get all family files from a directory. (ignores subdirectories)

    :param directory: directory to search for family files
    :type directory: str

    :return: list of family files
    :rtype: [FileItem]
    """

    family_files = get_revit_files(directory, "*.rfa")
    return family_files


def get_xml_files_from_directory(directory):
    """
    Get all xml files from a directory. (ignores subdirectories)

    :param directory: directory to search for xml files
    :type directory: str

    :return: list of xml files
    :rtype: [FileItem]
    """

    xml_files = get_revit_files(directory, "*.xml")
    return xml_files


def check_file_item_exists(instances, name_to_check):
    """
    Check if a file item exists in a list of file items based on the name property.

    :param instances: list of file items
    :type instances: [FileItem]
    :param name_to_check: name to check
    :type name_to_check: str

    :return: True if a file item with the name exists, False otherwise
    :rtype: bool
    """

    return any(instance.name == name_to_check for instance in instances)


def get_families_requiring_update(family_files, xml_files):
    """
    Check if any family files require an xml file update

    :param family_files: the family files to check
    :type family_files: [:class:`FileItem`]
    :param xml_files: the xml files to check against
    :type xml_files: [:class:`FileItem`]

    :return: a list of family files that require updating
    :rtype: list
    """

    return_value = Result()
    family_files_to_update = []
    try:
        # loop over family files
        for fam_file in family_files:

            # and find a matching xml file
            xml_file = os.path.splitext(fam_file.name)[0] + ".xml"

            # get the catalogue file too
            catalogue_file = os.path.splitext(fam_file.name)[0] + ".txt"

            # check if the xml file does exist
            if check_file_item_exists(xml_files, xml_file):

                # get time stamp of files for varies file types (.rfa, .xml, .txt) relating to families
                # .txt catalogue file
                # .xml part atom export file
                # .rfa family file
                xml_file_time_stamp = os.path.getmtime(xml_file)
                rfa_file_time_stamp = os.path.getmtime(fam_file.name)
                txt_file_time_stamp = (
                    None
                    if not (file_exist(catalogue_file))
                    else os.path.getmtime(catalogue_file)
                )

                # convert to something human readable
                xml_formatted_time = datetime.datetime.fromtimestamp(
                    xml_file_time_stamp
                )
                rfa_formatted_time = datetime.datetime.fromtimestamp(
                    rfa_file_time_stamp
                )
                txt_formatted_time = (
                    None
                    if txt_file_time_stamp is None
                    else datetime.datetime.fromtimestamp(txt_file_time_stamp)
                )

                # if the xml file is older than the family file
                if xml_file_time_stamp < rfa_file_time_stamp:

                    return_value.append_message(
                        "...xml file is older than family file, needs updating. [xml: {} vs rfa: {}]".format(
                            xml_formatted_time, rfa_formatted_time
                        )
                    )
                    # family xml file is older than family file, needs updating
                    family_files_to_update.append(fam_file.name)
                elif (
                    txt_file_time_stamp is not None
                    and xml_file_time_stamp < txt_file_time_stamp
                ):
                    return_value.append_message(
                        "...xml file is older than catalogue file, needs updating. [xml: {} vs txt: {}]".format(
                            xml_formatted_time, txt_formatted_time
                        )
                    )
                    # family xml file is older than family file, needs updating
                    family_files_to_update.append(fam_file.name)
                else:
                    # family xml file is up to date
                    pass

            else:
                # no matching xml file found
                family_files_to_update.append(fam_file.name)

        # save data to be returned
        return_value.result = family_files_to_update
    except Exception as e:
        return_value.update_sep(
            False,
            "Failed to check families requiring update with exception: {}".format(e),
        )

    return return_value


def write_data_to_xml_file(application, family_path, xml_path):
    """
    Write the family type data to an XML file.

    :param application: The Revit application object.
    :type application: Autodesk.Revit.ApplicationServices.Application
    :param family_path: The path of the family file.
    :type family_path: str
    :param xml_path: The path of the XML file.
    :type xml_path: str

    :return: A result object with .status True if successful.
    :rtype: Result
    """

    return_value = Result()
    try:

        # Save XML file to temporary location
        # this is a method of the application object and does not require the family to be open...
        application.ExtractPartAtomFromFamilyFile(family_path, xml_path)
        return_value.update_sep(True, "Wrote data to XML file.")
    except Exception as e:
        return_value.update_sep(False, "Failed to write XML data: {}".format(e))

    return return_value


def create_xml_file(revit_application, family_file):
    """
    Create an xml file for a given family file.

    :param revit_application: revit application object
    :type revit_application: Application
    :param family_file: family file to create xml file for
    :type family_file: str
    """

    return_value = Result()
    try:
        xml_file = os.path.splitext(family_file)[0] + ".xml"
        result_write = write_data_to_xml_file(revit_application, family_file, xml_file)
        return_value.update_sep(result_write)
    except Exception as e:
        return_value.update_sep(
            False,
            "Failed to create xml file for family: {} with exception: {}".format(
                family_file, e
            ),
        )
    return return_value


def write_data_to_temp_xml_file_and_read_it_back(an_action_to_write_xml_data):
    """
    Write the data to a temp XML file and read it back.

    :param an_action_to_write_xml_data: The action to write the XML data.
    :type an_action_to_write_xml_data: function returning a Result object

    :return:
        Result class instance.

        - result.status: True if data was written and read back successfully, False otherwise.
        - result.message will contain the log data.
        - result.result will be a XML document object.

        On exception

        - Reload.status (bool) will be False
        - Reload.message will contain the exception message
        - Reload.result will be an empty list.

    :rtype: :class:`.Result`
    """

    return_value = Result()

    # Create a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".xml") as temp_file:
        temp_path_xml = temp_file.name

    try:

        # Write the data to the file
        write_result = an_action_to_write_xml_data(temp_path_xml)
        # update the return value
        return_value.update(write_result)

        # Check if the write was successful
        if return_value.status is False:
            return return_value

        # Read the data back from the file
        read_result = read_xml_file(temp_path_xml)

        # update the return value message and status
        # for some reasons this adds a XMLDeclaration object to the result field...not sure why
        return_value.update(read_result)

        # overwrite result field with the actual XML document
        return_value.result = read_result.result

    finally:
        # Delete the temporary file
        if os.path.exists(temp_path_xml):
            os.remove(temp_path_xml)

    return return_value


def write_data_to_xml_file_and_read_it_back(an_action_to_write_xml_data, xml_file_path):
    """
    Write the data to an XML file and read it back.

    :param an_action_to_write_xml_data: The action to write the XML data.
    :type an_action_to_write_xml_data: function
    :param xml_file_path: The path of the XML file.
    :type xml_file_path: str

    :return:
        Result class instance.

        - result.status: True if data was written and read back successfully, False otherwise.
        - result.message will contain log data
        - result.result will be a XML document object.

        On exception

        - Reload.status (bool) will be False
        - Reload.message will contain the exception message
        - Reload.result will be an empty list.

    :rtype: :class:`.Result`
    """

    return_value = Result()

    try:

        # Write the data to the file
        write_result = an_action_to_write_xml_data(xml_file_path)

        # update the return value
        return_value.update(write_result)

        # Check if the write was successful
        if return_value.status is False:
            return return_value

        # Read the data back from the file
        read_result = read_xml_file(xml_file_path)

        # update the return value message and status
        # for some reasons this adds a XMLDeclaration object to the result field...not sure why
        return_value.update(read_result)
        # overwrite result field with the actual XML document
        return_value.result = read_result.result

    except Exception as e:
        return_value.update_sep(False, "{}".format(e))
    return return_value


def create_family_xml_files(
    revit_application, process_directories, progress_callback=None
):
    """
    Create xml files for all families in a list of directories using Revit API PartAtomExport function.

    :param revit_application: revit application object
    :type revit_application: Application
    :param process_directories: list of directories to process
    :type process_directories: [str]
    :param progress_callback: progress callback object
    :type progress_callback: ProgressBase

    :return: Result object
    :rtype: Result
    """

    return_value = Result()

    # check callback class
    if progress_callback and isinstance(progress_callback, ProgressBase) == False:
        raise TypeError(
            "progress_callback needs to be inherited from ProgressBase. Got : {} instead.".format(
                type(progress_callback)
            )
        )

    # check if directories are valid
    if isinstance(process_directories, list) == False:
        raise TypeError(
            "progress_directories needs to be a list. Got: {} instead.".format(
                type(process_directories)
            )
        )

    # set up a timer
    t = Timer()
    t.start()

    try:

        # loop through directories
        for directory in process_directories:

            # check if directory exists
            if directory_exists(directory) == False:
                return_value.update_sep(
                    False, "Directory does not exist: {} Skipping it.".format(directory)
                )
                continue

            # get any revit families from the directory
            return_value.append_message("Processing directory: {}".format(directory))

            families = get_families_from_directory(directory=directory)
            return_value.append_message("Families found: {}".format(len(families)))

            if len(families) == 0:
                return_value.append_message(
                    "No families found in directory: {}".format(directory)
                )
                continue

            # get any xml files from the directory
            xml_files = get_xml_files_from_directory(directory=directory)
            return_value.append_message("XML files found: {}".format(len(xml_files)))

            # check if any families require updating ( a new xml file is required or an existing one is out of date)
            families_to_update_result = get_families_requiring_update(
                families, xml_files
            )
            if families_to_update_result.status == False:
                return_value.update_sep(False, families_to_update_result.message)
                return_value.append_message(t.stop())
                return return_value

            families_to_update = families_to_update_result.result
            return_value.append_message(
                "Families requiring update: {}".format(len(families_to_update))
            )

            # check if any families require updating
            if families_to_update:

                # set up progress
                fam_counter = 1
                max_fam = len(families_to_update)

                # iterate through families
                for family in families_to_update:

                    # get the family name
                    fam_name = get_file_name_without_ext(family)

                    # update progress
                    if progress_callback:
                        progress_callback.update(fam_counter, max_fam, fam_name)

                    create_xml_file(revit_application, family)
                    return_value.append_message(
                        "Created xml file for family: {}".format(fam_name)
                    )

                    # update counter
                    fam_counter += 1

                    # check for user cancel
                    if progress_callback != None:
                        if progress_callback.is_cancelled():
                            return_value.append_message("User cancelled!")
                            break

        # stop the timer
        return_value.append_message(
            "Successfully created family atom exports: {}".format(t.stop())
        )

    except Exception as e:
        return_value.update_sep(
            False, "Failed to create family atom exports with exception: {}".format(e)
        )
        if t.is_running():
            return_value.append_message(t.stop())

    return return_value
