"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Utility functions for family instances read from family reports: finding report files and host families.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""


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

from duHast.Utilities.Objects.result import Result
from duHast.Utilities.files_get import get_files_from_directory_walker_with_filters
from duHast.Revit.Family.Data.family_report_reader import read_data_into_families
from duHast.Revit.Family.Data.Objects.family_data_family import FamilyDataFamily


def get_report_file_path(directory_path, report_name_prefix, file_extension=".csv"):
    """
    Gets the first report file with the given file name prefix in the directory or any of its sub directories.

    :param directory_path: Fully qualified directory path.
    :type directory_path: str
    :param report_name_prefix: The report file name prefix, e.g. FamilyBaseDataCombinedReport
    :type report_name_prefix: str
    :param file_extension: The report file extension, defaults to ".csv"
    :type file_extension: str, optional

    :return: Fully qualified file path of the report file, or None if no file was found.
    :rtype: str or None
    """

    files = get_files_from_directory_walker_with_filters(
        directory_path, report_name_prefix, "", file_extension
    )
    if len(files) > 0:
        return files[0]
    return None


def read_root_families_from_report(file_path):
    """
    Reads a family report file into root family instances, with their nested families.

    :param file_path: Fully qualified file path of the report file.
    :type file_path: str

    :return:
        Result class instance.

        - result.status. True if the report was read without an exception, otherwise False.
        - result.message will contain the read messages.
        - result.result list of root families.

        On exception:

        - result.status (bool) will be False.
        - result.message will contain the exception message.
        - result.result will be empty

    :rtype: :class:`.Result`
    """

    return_value = Result()
    read_result = read_data_into_families(file_path)
    if read_result.status is False:
        return_value.update_sep(
            False,
            "Failed to read families from: {} with: {}".format(
                file_path, read_result.message
            ),
        )
        return return_value
    return_value.append_message(
        "Read {} root families from: {}".format(len(read_result.result), file_path)
    )
    return_value.result = read_result.result
    return return_value


def find_all_direct_host_families(root_families, families):
    """
    Finds the families which directly host (contain at the next nesting level up) any of the given families.

    :param root_families: Root families, with their nested families, to search.
    :type root_families: [:class:`.FamilyDataFamily`]
    :param families: Families to find the hosts of, as tuples in format 0 index family name, 1 index family category.
    :type families: [(str, str)]

    :return: List of unique tuples in format 0 index the host family name, 1 index the host family category
    :rtype: [(str, str)]
    """

    hosts = []
    for family_name, family_category in families:
        for root_family in root_families:
            for host in root_family.get_direct_hosts(family_name, family_category):
                if host not in hosts:
                    hosts.append(host)
    return hosts


def find_root_families_from_hosts(root_families, hosts):
    """
    Returns the root families matching the given host families by name and category.

    :param root_families: Root families to search.
    :type root_families: [:class:`.FamilyDataFamily`]
    :param hosts: Host families as tuples in format 0 index family name, 1 index family category.
    :type hosts: [(str, str)]

    :return: List of root families.
    :rtype: [:class:`.FamilyDataFamily`]
    """

    matches = []
    for host_name, host_category in hosts:
        for root_family in root_families:
            if (
                root_family.family_name == host_name
                and root_family.family_category == host_category
                and root_family not in matches
            ):
                matches.append(root_family)
    return matches


def get_direct_host_root_families(root_families, families):
    """
    Returns the root families which directly host any of the given families.

    :param root_families: Root families, with their nested families, to search.
    :type root_families: [:class:`.FamilyDataFamily`]
    :param families: Families to find the hosts of: family instances, or tuples in format 0 index family name, 1 index family category.
    :type families: [:class:`.FamilyDataFamily`] or [(str, str)]

    :return: List of root families.
    :rtype: [:class:`.FamilyDataFamily`]
    """

    names_and_categories = []
    for family in families:
        if isinstance(family, FamilyDataFamily):
            names_and_categories.append((family.family_name, family.family_category))
        else:
            names_and_categories.append((family[0], family[1]))
    hosts = find_all_direct_host_families(root_families, names_and_categories)
    return find_root_families_from_hosts(root_families, hosts)
