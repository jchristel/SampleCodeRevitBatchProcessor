"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Module containing meta data file functions functions.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Some document exchange platforms may use meta data files to allow for fast processing of uploaded documents. This 
sample code uses aconex for that purpose.



"""

#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# License:
#
#
# Revit Batch Processor Sample Code
#
# Copyright (c) 2023  Jan Christel
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

# --------------------------
# Imports
# --------------------------

import os

# import settings
import settings as settings  # sets up all commonly used variables and path locations!

from duHast.Utilities.Objects import result as res
from duHast.Utilities.files_get import get_files
from duHast.Utilities.files_io import get_file_name_without_ext
from duHast.Utilities.date_stamps import get_date_stamp
from duHast.Utilities.files_csv import write_report_data_as_csv


def write_meta_data(meta_data_header, doc_files, root_path):
    """
    Function building meta data of files exported and writing data to file.

    :param meta_data_header: First (header) row in meta data file.
    :type meta_data_header: [str]
    :param doc_files: List of meta data information for all files in project.
    :type doc_files: [:class:`.docFile`]
    :param root_path: Fully qualified directory path to where exported files are located.
    :type root_path: str

    :return:
        Result class instance.

        - Write meta data status returned in result.status. False if an exception occurred, otherwise True.
        - result.message will contain messages for each file match found.
        - result.result will be a nested list containing meta data : [[[str,str,..],[str,str,..],..]]

        On exception:

        - result.status (bool) will be False.
        - result.message will contain the exception message.
        - result.result will be an empty list.

    :rtype: :class:`.Result`
    """

    return_value = res.Result()
    # build meta data
    result_meta_data_build = build_meta_data(
        meta_data_header=meta_data_header, doc_files=doc_files, root_path=root_path
    )
    return_value.update(result_meta_data_build)
    if result_meta_data_build.status:
        # attempt to write data to file
        try:
            meta_data_file_path = os.path.join(
                root_path, settings.ACONEX_METADATA_FILE_NAME
            )
            write_report_data_as_csv(
                meta_data_file_path, [], result_meta_data_build.result[0]
            )
            return_value.append_message(
                "Successfully wrote meta data file to: {}".format(meta_data_file_path)
            )
        except Exception as e:
            return_value.update_sep(
                False,
                "Failed to write data file: {} with exception: {}".format(
                    meta_data_file_path, e
                ),
            )
    else:
        # no action
        pass

    return return_value


def build_meta_data(meta_data_header, doc_files, root_path):
    """
    Builds meta data based on doc file data past in and files fpound in root path location.

    :param meta_data_header: First (header) row in meta data file.
    :type meta_data_header: [str]
    :param doc_files: List of meta data information for all files in project.
    :type doc_files: [:class:`.docFile`]
    :param root_path: Fully qualified directory path to where exported files are located.
    :type root_path: str

    :return:
        Result class instance.

        - Build meta data list status returned in result.status. False if an exception occurred, otherwise True.
        - result.message will contain messages for each file match found.
        - result.result will be a nested list containing meta data : [[[str,str,..],[str,str,..],..]]

        On exception:

        - result.status (bool) will be False.
        - result.message will contain the exception message.
        - result.result will be an empty list.

    :rtype: :class:`.Result`
    """

    return_value = res.Result()
    meta_data = []
    meta_data.append(meta_data_header)
    flag = True
    # get files in todays output folder
    files = get_files(root_path, file_extension=".*")
    # loop over files found and build aconex list
    if len(files) > 0:
        for file in files:
            file_name, file_extension = os.path.splitext(file)
            file_name = get_file_name_without_ext(file)
            for docs in doc_files:
                if (
                    file_name.startswith(docs.aconex_doc_number)
                    and file_extension == docs.file_extension
                ):
                    return_value.append_message(
                        "Found match: {} {}".format(file_name, file_extension)
                    )
                    row = []
                    row.append(docs.aconex_doc_number)
                    row.append(str(docs.revision))
                    row.append(docs.aconex_doc_name)
                    row.append(settings.ACONEX_METADATA_DOC_TYPE)
                    row.append(settings.ACONEX_METADATA_DOC_STATUS)
                    row.append(settings.ACONEX_METADATA_DISCIPLINE)
                    row.append(settings.ACONEX_METADATA_PROJECT_PHASE)
                    row.append(str(file_name) + str(file_extension))
                    row.append(settings.ACONEX_METADATA_NOT_APPLICABLE)
                    row.append("")
                    row.append(get_date_stamp(settings.ACONEX_METADATA_DATE_FORMAT))
                    row.append(settings.ACONEX_METADATA_COMPANY)
                    row.append("")
                    row.append("")
                    row.append("")
                    row.append("")
                    meta_data.append(row)
                    # update revision for file where we found a match only??
                    # in cases where we issue .rvt only but .rvt and .ifc revision need to stay the same....
                    docs.new_revision = True
                elif (
                    file_name.startswith(docs.existing_file_name)
                    and not (file_name.startswith(docs.aconex_doc_number))
                    and file_extension == docs.file_extension
                ):
                    # this condition applies to NWC's only on this job...
                    return_value.append_message(
                        "Found match: {} {}".format(file_name, file_extension)
                    )
                    row = []
                    row.append(docs.aconex_doc_number)
                    row.append(str(docs.revision))
                    row.append(docs.aconex_doc_name)
                    row.append(settings.ACONEX_METADATA_DOC_TYPE)
                    row.append(settings.ACONEX_METADATA_DOC_STATUS)
                    row.append(settings.ACONEX_METADATA_DISCIPLINE)
                    row.append(settings.ACONEX_METADATA_PROJECT_PHASE)
                    row.append(str(file_name) + str(file_extension))
                    row.append(settings.ACONEX_METADATA_NOT_APPLICABLE)
                    row.append("")
                    row.append(get_date_stamp(settings.ACONEX_METADATA_DATE_FORMAT))
                    row.append(settings.ACONEX_METADATA_COMPANY)
                    row.append("")
                    row.append("")
                    row.append("")
                    row.append("")
                    meta_data.append(row)
                    docs.new_revision = True
        # return meta data to caller
        return_value.result.append(meta_data)
    else:
        return_value.update_sep(
            False, "No files to add to meta data found in {}".format(root_path)
        )
    return return_value
