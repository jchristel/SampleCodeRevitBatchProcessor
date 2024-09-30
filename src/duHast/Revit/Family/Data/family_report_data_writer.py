"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Module containing functions to write report files from data previously read from file.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

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

import os

from duHast.Utilities.Objects.result import Result
from duHast.Utilities.files_csv import write_report_data_as_csv
from duHast.Utilities.directory_io import directory_exists


# import report names and identifiers
from duHast.Revit.Family.Data.Objects.family_base_data_processor_defaults import (
    DATA_TYPE_PROCESSOR as data_type_family_base_processor,
)
from duHast.Revit.Family.Data.Objects.family_base_data_processor_defaults import (
    DATA_REPORT_NAME as data_type_family_base_report_name,
)

from duHast.Revit.Categories.Data.Objects.category_data_processor_defaults import (
    DATA_TYPE_PROCESSOR as data_type_category_processor,
)
from duHast.Revit.Categories.Data.Objects.category_data_processor_defaults import (
    DATA_REPORT_NAME as data_type_category_report_name,
)

from duHast.Revit.LinePattern.Data.Objects.line_pattern_data_processor_defaults import (
    DATA_TYPE_PROCESSOR as data_type_line_pattern_processor,
)
from duHast.Revit.LinePattern.Data.Objects.line_pattern_data_processor_defaults import (
    DATA_REPORT_NAME as data_type_line_pattern_report_name,
)

from duHast.Revit.SharedParameters.Data.Objects.shared_parameter_data_processor_defaults import (
    DATA_TYPE_PROCESSOR as data_type_shared_parameter_processor,
)
from duHast.Revit.SharedParameters.Data.Objects.shared_parameter_data_processor_defaults import (
    DATA_REPORT_NAME as data_type_shared_parameter_report_name,
)

from duHast.Revit.Warnings.Data.Objects.warnings_data_processor_defaults import (
    DATA_TYPE_PROCESSOR as data_type_warnings_processor,
)
from duHast.Revit.Warnings.Data.Objects.warnings_data_processor_defaults import (
    DATA_REPORT_NAME as data_type_warnings_report_name,
)


# contains the report name depending on data type
REPORT_NAME_BY_DATA_TYPE = {
    data_type_family_base_processor: data_type_family_base_report_name,
    data_type_category_processor: data_type_category_report_name,
    data_type_line_pattern_processor: data_type_line_pattern_report_name,
    data_type_shared_parameter_processor: data_type_shared_parameter_report_name,
    data_type_warnings_processor: data_type_warnings_report_name,
}


def get_storage_data(family_data):
    """
    Retrieves the storage data as list of strings sorted by storage type.

    :param family_data: List of family instances.
    :type family_data: [:class:`.FamilyDataFamily`]

    :return: A dictionary where the key is the storage data type, and value is a nested list of lists of strings representing the storage data.
    :rtype: {str:[[str]]}
    """

    # loop over all family instances and get the storage data and combine into single dictionary
    # where key is the data type and values is a list of all storage instances of that data type

    return_value = {}
    for family_instance in family_data:
        data_dic = family_instance.get_all_storage_data_as_strings
        for key, item in data_dic.items():
            if key in return_value:
                return_value[key].extend(item)
            else:
                return_value[key] = item
    return return_value


def get_storage_headers(family_data):
    """
    Gets the storage property (report) headers

    :param family_data: List of family instances.
    :type family_data: [:class:`.FamilyDataFamily`]

    :return: A dictionary where the key is the storage data type, and value is a nested list of lists of strings representing the storage data property names.
    :rtype: {str:[[str]]}
    """

    return_value = {}
    for family_instance in family_data:
        data_dic = family_instance.get_all_storage_headers_as_strings
        for key, item in data_dic.items():
            if key not in return_value:
                return_value[key] = item
    return return_value


def write_data_from_families_to_files(family_data, directory_path):
    """
    Writes family data retrieved from report files back to file.

    :param family_data: List of family instances
    :type family_data: [:class:`.FamilyDataFamily`]
    :param directory_path: Fully qualified directory path to write report files to.
    :type directory_path: str
    :raises TypeError: family_data needs to be a list.
    :raises TypeError: directory_path needs to be a string.
    :raises ValueError: Directory: xyz does not exist.
    :raises ValueError: Failed to get any storage data from family data past in.

    :return:
        Result class instance.

        - result.status: Write report files status returned in result.status. False if an exception occurred, otherwise True.
        - result.message: Will contain the fully qualified file path of each of report files written.
        - result.result: Will be a fully qualified file path of each file written.

        On exception

        - Reload.status (bool) will be False
        - Reload.message will contain the exception message

    :rtype: :class:`.Result`
    """

    return_value = Result()

    try:
        # tests first
        if isinstance(family_data, list) == False:
            raise TypeError(
                "Family_data needs to be a list. Got {} instead.".format(
                    type(family_data)
                )
            )

        if isinstance(directory_path, str) == False:
            raise TypeError(
                "Directory_path needs to be a string. Got {} instead".format(
                    type(directory_path)
                )
            )

        if directory_exists(directory_path=directory_path) == False:
            raise ValueError("Directory: {} does not exist.".format(directory_path))

        # get storage data
        storage_data_dic = get_storage_data(family_data=family_data)

        # get storage file headers
        storage_headers_dic = get_storage_headers(family_data=family_data)

        # need to have at least one entry:
        if len(storage_data_dic) < 1:
            raise ValueError("Failed to get any storage data from family data past in.")

        for key, item in storage_data_dic.items():
            # write to file
            if key in REPORT_NAME_BY_DATA_TYPE:
                # build output file name
                full_file_name = os.path.join(
                    directory_path, REPORT_NAME_BY_DATA_TYPE[key], ".csv"
                )
                try:
                    # get file header
                    header_data = []
                    if key in storage_headers_dic:
                        header_data = storage_headers_dic[key]

                    write_report_data_as_csv(
                        file_name=full_file_name, header=header_data, data=item
                    )
                    return_value.append_message(
                        "Successfully wrote data type: {} report to: {}".format(
                            key, full_file_name
                        )
                    )
                    return_value.result.append(full_file_name)
                except Exception as e:
                    return_value.update_sep(
                        False,
                        "Failed to write report for data type: {} to file: {}".format(
                            key, full_file_name
                        ),
                    )
            else:
                return_value.update_sep(
                    False, "Data type: {} has no report file name assigned".format(key)
                )

    except Exception as e:
        return_value.update_sep(
            False,
            "Failed to write family storage data to file with exception: {}".format(e),
        )

    return return_value
