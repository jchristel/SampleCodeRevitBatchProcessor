"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Family Base data utility module containing functions to read the data from file.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Reads family base data into two list of named tuples.

root_family:

- name 
- category 
- filePath 
- parent 
- child

nested_family:

- name 
- category 
- filePath 
- rootPath  [str]
- categoryPath [str]

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

from collections import namedtuple

from duHast.Utilities import (
    files_csv as fileCSV,
    files_get as fileGet,
    files_io as fileIO,
    utility as util,
)

from duHast.Revit.Family.Data.Objects.family_base_data_processor_defaults import (
    NESTING_SEPARATOR,
)

# tuples containing base family data read from file
root_family = namedtuple(
    "root_family", "name category filePath parent child report_data"
)
nested_family = namedtuple(
    "nested_family",
    "name category filePath rootPath categoryPath hostFamily report_data",
)

# row structure of family base data file
BASE_DATA_LIST_INDEX_FAMILY_NAME = 2
BASE_DATA_LIST_INDEX_FAMILY_FILE_PATH = 3
BASE_DATA_LIST_INDEX_CATEGORY = 4
BASE_DATA_LIST_INDEX_ROOT_PATH = 0
BASE_DATA_LIST_INDEX_ROOT_CATEGORY_PATH = 1

# file name identifiers for family base data
FAMILY_BASE_DATA_FILE_NAME_PREFIX = "FamilyBase"
FAMILY_BASE_DATA_FILE_EXTENSION = ".csv"

# exceptions
EXCEPTION_NO_FAMILY_BASE_DATA_FILES = "Families base data list files do not exist."
EXCEPTION_EMPTY_FAMILY_BASE_DATA_FILES = "Empty Families base data list file!"


def _get_base_data_file_name(directory_path):
    """
    Gets the first family base data file in provided directory or any of it's sub directories.

    :param directory_path: Fully qualified directory path.
    :type directory_path: str
    :raises Exception: EXCEPTION_NO_FAMILY_BASE_DATA_FILES

    :return: Fully qualified file path to family base data file.
    :rtype: str
    """

    # get all base data files in folder
    files = fileGet.get_files_from_directory_walker_with_filters(
        directory_path,
        FAMILY_BASE_DATA_FILE_NAME_PREFIX,
        "",
        FAMILY_BASE_DATA_FILE_EXTENSION,
    )
    if len(files) > 0:
        return files[0]
    else:
        raise Exception(EXCEPTION_NO_FAMILY_BASE_DATA_FILES)


def read_overall_family_data_list(file_path):
    """
    Reads list of families from family base data report file into named tuples.

    :param file_path: Fully qualified file path to family base data report file.
    :type file_path: str
    :raises Exception: "Families base data list files does not exist."
    :raises Exception: "Empty Families base data list file!"
    :return: Two lists: first list of named tuples contain family root data, second list contains family nested data.
    :rtype: [root_family], [nested_family]
    """

    rows = []
    if fileIO.file_exist(file_path):
        rows = fileCSV.read_csv_file(file_path)
    else:
        raise Exception(EXCEPTION_NO_FAMILY_BASE_DATA_FILES)
    if len(rows) > 0:
        pass
    else:
        raise Exception(EXCEPTION_EMPTY_FAMILY_BASE_DATA_FILES)

    return_value_root_family = []
    return_value_nested_family = []
    for i in range(1, len(rows)):
        # check if root family
        if NESTING_SEPARATOR not in rows[i][BASE_DATA_LIST_INDEX_ROOT_PATH]:
            data = root_family(
                rows[i][BASE_DATA_LIST_INDEX_FAMILY_NAME],
                rows[i][BASE_DATA_LIST_INDEX_CATEGORY],
                rows[i][BASE_DATA_LIST_INDEX_FAMILY_FILE_PATH],
                [],  # set up an empty list for parent families
                [],  # set up an empty list for child families
                rows[i],  # set up report data
            )
            return_value_root_family.append(data)
        else:
            # found a child family
            data = nested_family(
                rows[i][BASE_DATA_LIST_INDEX_FAMILY_NAME],
                rows[i][BASE_DATA_LIST_INDEX_CATEGORY],
                rows[i][BASE_DATA_LIST_INDEX_FAMILY_FILE_PATH],
                rows[i][BASE_DATA_LIST_INDEX_ROOT_PATH].split(
                    NESTING_SEPARATOR
                ),  # split root path into list for ease of searching
                rows[i][BASE_DATA_LIST_INDEX_ROOT_CATEGORY_PATH].split(
                    NESTING_SEPARATOR
                ),  # split category path into list for ease of searching
                [],
                rows[i],  # set up report data
            )
            return_value_nested_family.append(data)
    return return_value_root_family, return_value_nested_family


def read_overall_family_data_list_from_directory(directory_path):
    """
    Reads the first family base data file it finds in a folder.
    Note: This method calls ReadOverallFamilyDataList(filePath) which will raise exceptions if files are empty or dont exist in specified folder.

    :param directory_path: A fully qualified directory path containing family base data file(s)
    :type directory_path: _str

    :return: Two lists: first list of named tuples contain family root data, second list contains family nested data.
    :rtype: [root_family], [nested_family]
    """

    file_name = _get_base_data_file_name(directory_path)
    return read_overall_family_data_list(file_name)


def read_overall_family_data_list_into_nested(file_path):
    """
    Reads list of families from family base data report file into named tuples.

    :param file_path: Fully qualified file path to family base data report file.
    :type file_path: str
    :raises Exception: "Families base data list files does not exist."
    :raises Exception: "Empty Families base data list file!"
    :return: A list contains family nested data.
    :rtype: [nested_family]
    """

    rows = []
    if fileIO.file_exist(file_path):
        rows = fileCSV.read_csv_file(file_path)
    else:
        raise Exception(EXCEPTION_NO_FAMILY_BASE_DATA_FILES)
    if len(rows) > 0:
        pass
    else:
        raise Exception(EXCEPTION_EMPTY_FAMILY_BASE_DATA_FILES)

    return_value_nested_family = []
    for i in range(1, len(rows)):
        # found a child family
        data = nested_family(
            rows[i][BASE_DATA_LIST_INDEX_FAMILY_NAME],
            rows[i][BASE_DATA_LIST_INDEX_CATEGORY],
            rows[i][BASE_DATA_LIST_INDEX_FAMILY_FILE_PATH],
            rows[i][BASE_DATA_LIST_INDEX_ROOT_PATH].split(
                NESTING_SEPARATOR
            ),  # split root path into list for ease of searching
            rows[i][BASE_DATA_LIST_INDEX_ROOT_CATEGORY_PATH].split(
                NESTING_SEPARATOR
            ),  # split category path into list for ease of searching
            [],
        )
        return_value_nested_family.append(data)
    return return_value_nested_family


def read_overall_family_data_list_into_nested_from_directory(directory_path):
    """
    Reads the first family base data file it finds in a folder.
    Note: This method calls ReadOverallFamilyIntoNestedDataList(filePath) which will raise exceptions if files are empty or dont exist in specified folder.

    :param directory_path: A fully qualified directory path containing family base data file(s)
    :type directory_path: _str

    :return: A list contains family nested data.
    :rtype: [nested_family]
    """

    file_name = _get_base_data_file_name(directory_path)
    return read_overall_family_data_list_into_nested(file_name)


# -------------------------------- simplify data set ----------------------------------------------------------------


def _check_data_blocks_for_overlap(block_one, block_two):
    """
    Checks whether the root path of families in the first block overlaps with the root path of any family in the second block.
    Overlap is checked from the start of the root path. Any families from block one which are not overlapping any family in\
        block two are returned.

    :param block_one: List of family tuples of type nested_family
    :type block_one: [nested_family]
    :param block_two: List of family tuples of type nested_family
    :type block_two: [nested_family]
    
    :return: List of family tuples of type nested_family
    :rtype: [nested_family]
    """

    unique_tree_nodes = []
    for fam in block_one:
        match = False
        for fam_up in block_two:
            if NESTING_SEPARATOR.join(fam_up.rootPath).startswith(
                NESTING_SEPARATOR.join(fam.rootPath)
            ):
                match = True
                break
        if match == False:
            unique_tree_nodes.append(fam)
    return unique_tree_nodes


def _cull_data_block(family_base_nested_data_block):
    """
    Sorts family data blocks into a dictionary where key, from 1 onwards, is the level of nesting indicated by number of ' :: ' in root path string.

    After sorting it compares adjacent blocks in the dictionary (key and key + 1) for overlaps in the root path string. Only unique families will be returned.

    :param family_base_nested_data_block: A list containing all nested families belonging to a single root host family.
    :type family_base_nested_data_block: [nested_family]

    :return: A list of unique families in terms of root path.
    :rtype: [nested_family]
    """

    culled_family_base_nested_data_blocks = []

    if isinstance(family_base_nested_data_block, list) == False:
        raise Exception(
            "Family base nested data block is not a list. It is of type: {}".format(
                type(family_base_nested_data_block)
            )
        )

    culled_family_base_nested_data_blocks = []
    data_blocks_by_length = {}

    # build dic by root path length
    # start at 1 because for nesting level ( 1 based rather then 0 based )
    for family in family_base_nested_data_block:

        # root path is a list of family names representing the nesting tree
        # subtract 1 to get the nesting level minus the root family itself
        split_root_path_length = len(family.rootPath) - 1

        # add family to dictionary
        if split_root_path_length in data_blocks_by_length:
            data_blocks_by_length[split_root_path_length].append(family)
        else:
            data_blocks_by_length[split_root_path_length] = [family]

    # loop over dictionary and check block entries against next entry up blocks
    # I need to extend range by 1 since the end value in the range is always exclusive in python for i in range loop
    # i.e. for i in range (1, 3) will only loop over 1 and 2...

    for i in range(1, len(data_blocks_by_length) + 1):

        # last block get automatically added
        # do not add + 1 here since the loop will stop at the last entry
        if i == len(data_blocks_by_length):
            culled_family_base_nested_data_blocks = (
                culled_family_base_nested_data_blocks + data_blocks_by_length[i]
            )
        else:
            # check for matches in next one up
            unique_nodes = _check_data_blocks_for_overlap(
                data_blocks_by_length[i], data_blocks_by_length[i + 1]
            )
            # only add non overlapping blocks
            culled_family_base_nested_data_blocks = (
                culled_family_base_nested_data_blocks + unique_nodes
            )

    return culled_family_base_nested_data_blocks


def cull_nested_base_data_blocks(root_families, nested_families):
    """
    Reduce base data families for parent / child finding purposes. Keep the nodes with the root path longes branch only.

    Sample ( within a single data block)

    famA :: famB :: famC
    FamA :: famB

    The second of the above examples can be culled since the path is contained within the first example.

    Sample ( across multiple data blocks)

    famA :: famB :: famC
    famB :: famC


    The second of the above examples can be culled since the first family (famB) in that sample is already in the first example.(nested Family)

    :param overall_family_base_nested_data: _description_
    :type overall_family_base_nested_data: _type_
    """

    # get root families not found in nested data since they contain the longest unique nesting path
    non_nested_root_families = find_root_families_not_in_nested_data(
        root_families, nested_families
    )

    # get nested family data blocks for each root family
    nested_data_blocks_per_root_family = get_nested_family_data_for_root_family(
        non_nested_root_families, nested_families
    )

    # storage for culled data
    retained_family_base_nested_data = []

    # cull data per block
    for (
        root_family_identifier,
        family_block,
    ) in nested_data_blocks_per_root_family.items():
        # if the data block only contains one item skip culling
        if len(family_block) == 1:
            # no need to do any culling
            retained_family_base_nested_data.append(family_block[0])
            continue
        else:
            # attempt to cull data block
            d = _cull_data_block(family_block)
            retained_family_base_nested_data = retained_family_base_nested_data + d

    return retained_family_base_nested_data


def get_nested_family_data_for_root_family(root_families, nested_families):
    """
    Returns a list of nested families for each root family.

    :param root_families: A list of tuples containing root family data.
    :type root_families: [root_family]
    :param nested_families: A list of tuples containing nested family data.
    :type nested_families: [nested_family]

    :return: A dictionary where:

        - key is the root family name and category concatenated and
        - value is a list of tuples containing nested family data.

    :rtype: {str: [nested_family]}
    """

    nested_families_for_root_families = {}
    for root_family in root_families:
        nested_families_for_root_families[root_family.name + root_family.category] = []
        for nested_family in nested_families:
            if (
                nested_family.rootPath[0] == root_family.name
                and nested_family.categoryPath[0] == root_family.category
            ):
                nested_families_for_root_families[
                    root_family.name + root_family.category
                ].append(nested_family)
    return nested_families_for_root_families


def find_root_families_not_in_nested_data(root_families, nested_families):
    """
    Returns a list of root families not found in the nested family data set.

    In order to reduce the number of families to be processed, this function can be used to find the root families which are not nested into any other family and therefore do contain the
    longest nesting path.

    This is based on two assumptions:

    - The provided data set contains all families in the project (no missing families are reported)
    - As soon as a family is nested into another family, its nesting path will appear in the nested family data set and the root family data set.

    :param root_families: A list of tuples containing root family data.
    :type root_families: [root_family]
    :param nested_families: A list of tuples containing nested family data.
    :type nested_families: [nested_family]

    :return: A list of tuples containing root family data.
    :rtype: [root_family]

    """

    # storage for root families not found in nested data
    root_families_not_in_nested_data = []

    # check each root family
    for root_family in root_families:
        found = False
        for nested_family in nested_families:
            # check if the root family name is in the nested family root path on first position
            # only interested in matches which are not the first entry in the list since that indicates nesting
            index_match_root = util.index_of(nested_family.rootPath, root_family.name)
            if index_match_root > 0:
                # check if the categories are also a match!
                if nested_family.categoryPath[index_match_root] == root_family.category:
                    # found a match
                    found = True
                    break
        if found == False:
            root_families_not_in_nested_data.append(root_family)
    return root_families_not_in_nested_data


# --------------------------------------------  find families in nesting tree data ------------------------------------


def find_direct_host_families(nested_fam, overall_family_base_nested_data):
    """
    Finds the direct hosts of the past in family in the base nested family data set.

    :param nested_fam: A tuple containing nested family data.
    :type nested_fam: nested_family
    :param overall_family_base_nested_data: List of tuples containing nested family data.
    :type overall_family_base_nested_data: [nested_family]

    :return: A dictionary where:

        - key is the family name and category concatenated and
        - value is a tuple in format 0: family name, 1: family category

    :rtype: {str: (str,str)}
    """

    host_families = {}
    # check each base family data whether it contains the missing family in its nesting tree
    for base_nested_fam in overall_family_base_nested_data:
        if nested_fam.name in base_nested_fam.rootPath:
            index_match = util.index_of(base_nested_fam.rootPath, nested_fam.name)
            # make sure we have a match and it is not the first entry in list (does not have a parent...)
            if index_match > 0:
                # confirm category is the same
                if base_nested_fam.categoryPath[index_match] == nested_fam.category:
                    # got a direct parent! (index - 1)
                    key_new = (
                        base_nested_fam.rootPath[index_match - 1]
                        + base_nested_fam.categoryPath[index_match - 1]
                    )
                    if key_new not in host_families:
                        host_families[key_new] = (
                            base_nested_fam.rootPath[index_match - 1],
                            base_nested_fam.categoryPath[index_match - 1],
                        )
    return host_families


def find_all_direct_host_families(families, overall_family_base_nested_data):
    """
    Returns a dictionary of all direct host families of families past in.

    :param families: A list of tuples containing nested family data.
    :type families: [nested_family]
    :param overall_family_base_nested_data: List of tuples containing nested family data.
    :type overall_family_base_nested_data: [nested_family]

    :return: A dictionary.
    :rtype: {str: (str,str)}
    """

    host_families = {}
    for fam in families:
        hosts = find_direct_host_families(fam, overall_family_base_nested_data)
        # update dictionary with new hosts only
        for h in hosts:
            if h not in host_families:
                host_families[h] = hosts[h]
    return host_families


def find_root_families_from_hosts(host_families, overall_family_base_root_data):
    """
    Returns a list of tuples of type root_family matching the past in host families.

    :param host_families: A dictionary where:

        - key is the family name and category concatenated and
        - value is a tuple in format 0: family name, 1: family category

    :type host_families: {str: (str,str)}
    :param overall_family_base_root_data: List of tuples containing root family data.
    :type overall_family_base_root_data: [root_family]

    :return: List of root family tuples.
    :rtype: [root_family]
    """

    base_host_families = []
    for nested_id, nestedFam in host_families.items():
        for base_root_fam in overall_family_base_root_data:
            if (
                nestedFam[0] == base_root_fam.name
                and nestedFam[1] == base_root_fam.category
            ):
                base_host_families.append(base_root_fam)
    return base_host_families
