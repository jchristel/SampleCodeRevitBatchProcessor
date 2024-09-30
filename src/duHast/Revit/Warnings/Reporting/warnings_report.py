"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a Revit warnings properties report function. 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2023, Jan Christel
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

from duHast.Revit.Warnings.warnings import get_warnings
from duHast.Revit.Warnings.Objects.warnings_storage import RevitWarning
from duHast.Utilities.Objects import result as res
from duHast.Revit.Warnings.Reporting.warnings_report_header import (
    REPORT_WARNINGS_HEADER,
)
from duHast.Utilities.files_csv import write_report_data_as_csv


def get_warnings_report_data(doc, revit_file_name):
    """
    Gets warnings data to be written to report file.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param revit_file_path: The file hostname, which is added to data returned.
    :type revit_file_path: str
    :return: list of list of sheet properties.
    :rtype: list of list of str
    """

    # get all warnings
    data = {}
    warnings = get_warnings(doc)
    for warning in warnings:
        try:
            failure_id_guid = warning.GetFailureDefinitionId().Guid
            failure_description = warning.GetDescriptionText()
            failing_ids = warning.GetFailingElements()
            failing_ids_as_integer = []
            for fail_id in failing_ids:
                failing_ids_as_integer.append(fail_id.IntegerValue)

            warning_stored = RevitWarning(
                file_name=revit_file_name,
                id=failure_id_guid,
                description=failure_description,
                element_ids=failing_ids_as_integer,
            )
            if warning_stored.id in data:
                data[warning_stored.id].append(warning_stored)
            else:
                data[warning_stored.id] = [warning_stored]

        except Exception as e:
            # store the exception
            warning_exception = ResourceWarning(
                file_name=revit_file_name,
                id=-1,
                description="failed to retrieve warning with exception: {}".format(e),
                element_ids=[],
            )
            if warning_stored.id in data:
                data[warning_stored.id].append(warning_exception)
            else:
                data[warning_stored.id] = [warning_exception]

    return data


def convert_warnings_data_to_list(warnings_data):
    """
    Converts a list of dictionaries of view properties names and values to a list of properties only.

    :param view_data: List of dictionaries representing view properties
    :type view_data: [{}]
    :return: A list of lists of view property values.
    :rtype: [[str]]
    """

    data = []
    for key, value in warnings_data.items():
        number_elements_affected = 0
        dummy = None
        for warning_data_instance in value:
            number_elements_affected = number_elements_affected + len(
                warning_data_instance.element_ids
            )
            dummy = warning_data_instance
        # build a list with entries:
        # file name, warning GUID, number of warnings belonging to warnings GUID, warnings description, number of elements involved overall
        data.append(
            [
                dummy.file_name,
                dummy.date,
                dummy.time,
                dummy.id,
                len(warnings_data[key]),
                dummy.description,
                number_elements_affected,
            ]
        )
    return data


def write_warnings_data(file_name, data):
    """
    Writes to file all warnings properties.

    file type: csv

    :param file_name: The fully qualified file path of the report file.
    :type file_name: str
    :param current_file_name: The current revit file name which will be appended to data in the report.
    :type current_file_name: str
    :return:
        Result class instance.
        - .status True if data was written successfully. Otherwise False.
        - .message will contain write status.
    :rtype: :class:`.Result`
    """

    return_value = res.Result()
    try:
        data_converted = convert_warnings_data_to_list(warnings_data=data)
        write_report_data_as_csv(
            file_name=file_name,
            header=REPORT_WARNINGS_HEADER,
            data=data_converted,
            enforce_ascci=True,
        )
        return_value.update_sep(
            True, "Successfully wrote data file at {}".format(file_name)
        )
    except Exception as e:
        return_value.update_sep(False, str(e))
    return return_value
