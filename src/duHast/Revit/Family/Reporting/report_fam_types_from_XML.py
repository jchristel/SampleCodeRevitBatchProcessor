"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Module containing reporting family type reporting functions.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Reports:

- all family types in the library folder ( based on xml files located in the library folder)

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

from duHast.Revit.Family.family_types_get_data_from_xml import (
    get_family_type_data_from_library,
)
from duHast.Utilities.files_xml import get_all_xml_files_from_directories
from duHast.Utilities.Objects.timer import Timer
from duHast.Utilities.Objects.result import Result
from duHast.UI.Objects.ProgressBase import ProgressBase


def build_report(type_data_storage_manager_instances):
    """
    Build a report of the family type data retrieved from the library.

    :param type_data_storage_manager_instances: list of matched family type data
    :type type_data_storage_manager_instances: [:class:`FamilyTypeDataStorageManager`]

    :return:
        Result class instance.

        - result.status: Comparison status will be returned in result.status. False if an exception occurred, otherwise True.
        - result.message: will be empty.
        - result.result will be [[str]] where each entry is a list of family name, category etc and difference.

        On exception

        - Reload.status (bool) will be False
        - Reload.message will contain the exception message
        - Reload.result will be an empty list

    :rtype: :class:`.Result`
    """

    report_data = []
    return_value = Result()
    try:
        # loop over the data and built the report
        for type_data_storage_manager_instance in type_data_storage_manager_instances:
            fam_data = type_data_storage_manager_instance.get_report_data()
            for fam in fam_data:
                report_data.append(fam)
        # store the report data
        return_value.result = report_data
    except Exception as e:
        return_value.update_sep(
            False, "Failed to gather family data with exception: {}".format(e)
        )

    return return_value


def get_family_type_data_from_library_xml(process_directories, progress_callback=None):
    """
    Reads family xml atom files from library directories and saves them out to a combined csv report.

    :param process_directories: list of directories to search for xml files
    :type process_directories: list
    :param progress_callback: progress callback object
    :type progress_callback: :class:`ProgressBase`

    :return:
        Result class instance.

        - result.status: Report status will be returned in result.status. False if an exception occurred, otherwise True.
        - result.message: Log entries.
        - result.result will be [[str]] where each entry is a list of family name, category etc and difference.

        On exception

        - Reload.status (bool) will be False
        - Reload.message will contain the exception message
        - Reload.result will be an empty list

    :rtype: :class:`.Result`
    """

    return_value = Result()

    # check callback class
    if progress_callback and isinstance(progress_callback, ProgressBase) == False:
        raise TypeError(
            "progress_callback needs to be inherited from ProgressBase. Got : {} instead.".format(
                type(progress_callback)
            )
        )

    # set up a timer
    t = Timer()
    t.start()

    try:

        # get all xml files from the directory representing families in the library (point of truth)
        xml_files_in_libraries = get_all_xml_files_from_directories(process_directories)

        # check if any xml files were found
        if len(xml_files_in_libraries) == 0:
            return_value.update_sep(
                False,
                "No XML files found in the directories: {}".format(process_directories),
            )
            return_value.append_message(t.stop())
            return return_value
        else:
            return_value.append_message(
                "Found {} XML files in the directories: {}".format(
                    len(xml_files_in_libraries), process_directories
                )
            )

        # get the type data from the library
        type_data_from_library_result = get_family_type_data_from_library(
            xml_files_in_libraries, progress_callback
        )

        # check if the type data from the library was successfully gathered
        if (
            type_data_from_library_result.status == False
            or len(type_data_from_library_result.result) == 0
        ):
            return_value.update_sep(False, type_data_from_library_result.message)
            return_value.append_message(t.stop())
            return return_value
        else:
            return_value.append_message(
                "Successfully gathered family type data from the library."
            )

        # build the report
        report_result = build_report(type_data_from_library_result.result)

        # check if the report was successfully built
        if report_result.status == False:
            return_value.update_sep(False, report_result.message)
            return_value.append_message(t.stop())
            return return_value
        else:
            return_value.append_message(
                "Successfully built the report. {}".format(t.stop())
            )

        # store the report data
        return_value.result = report_result.result

    except Exception as e:
        return_value.update_sep(
            False, "Failed to gather family data with exception: {}".format(e)
        )
        return_value.append_message(t.stop())

    return return_value
