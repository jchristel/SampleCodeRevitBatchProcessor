"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Family Base data analysis module containing functions to find circular family referencing in extracted data.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A circular reference is when a family A has a family B nested but family B has also family A nested.

Algorithm description:

- read base data file processing list (created by RevitFamilyBaseDataProcessor module)
- extract all root families (no ' :: ' in root path)
- extract all nested families (' :: 'in root path)

- loop over root families
    - loop over nested families 
        - check if root family is in nested family root path
            - yes
            - get all families higher in root path and add to parents prop of root family (if not there already)
            - get all families lower in root path of nested family and add to child property of root family if not already
            -   TODO: Check this theory: families always have the same children...once children are identified there is no need to check over and over again!

- loop over root family 
    -   check whether any family exist in parent and child family
        - YES: found circular reference

"""

#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright © 2023, Jan Christel
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

import threading
import os

from duHast.Revit.Family.Data import family_base_data_utils as rFamBaseDataUtils
from duHast.Utilities.Objects.timer import Timer
from duHast.Utilities.Objects import result as res


def _extract_parent_families(current_parent, tree_path):
    """
    Find the index of the match in the root tree, any entries in the root tree list with a lower index are parents

    Note: Changes current_parent.parent property of the current_parent variable!

    :param current_parent: A tuple containing family root data
    :type current_parent: named tuple rootFamily
    :param tree_path: list of family names describing the nesting tree of a family
    :type tree_path: [str]
    :return: Nothing
    :rtype: None
    """

    index_match = tree_path.index(current_parent.name)
    # double check...it exists and it is not root itself
    if index_match > 0:
        # add all parents
        for i in range(index_match):
            if tree_path[i] not in current_parent.parent:
                current_parent.parent.append(tree_path[i])


def _extract_child_families(current_parent, tree_path):
    """
    Find the index of the match in the root tree, any entries in the root tree list with a lower index are children

    Note: Changes current_parent.child property of the current_parent variable!

    :param current_parent: A tuple containing family root data
    :type current_parent: named tuple rootFamily
    :param tree_path: list of family names describing the nesting tree of a family
    :type tree_path: [str]
    :return: Nothing
    :rtype: None
    """

    index_match = tree_path.index(current_parent.name)
    # double check...it exists and it is not root itself and its not the last item in tree path
    if index_match > 0 and index_match != len(tree_path):
        # add all children
        for i in range(index_match + 1, len(tree_path)):
            if tree_path[i] not in current_parent.child:
                current_parent.child.append(tree_path[i])


def _check_data_blocks_for_over_lap(block_one, block_two):
    """
    Checks whether the root path of families in the first block overlaps with the root path of any family in the second block.
    Overlap is checked from the start of the root path. Any families from block one which are not overlapping any family in\
        block two are returned.

    :param block_one: List of family tuples of type nestedFamily
    :type block_one: [nestedFamily]
    :param block_two: List of family tuples of type nestedFamily
    :type block_two: [nestedFamily]
    :return: List of family tuples of type nestedFamily
    :rtype: [nestedFamily]
    """

    unique_tree_nodes = []
    for fam in block_one:
        match = False
        for fam_up in block_two:
            if " :: ".join(fam_up.rootPath).startswith(" :: ".join(fam.rootPath)):
                match = True
                break
        if match == False:
            unique_tree_nodes.append(fam)
    return unique_tree_nodes


def _cull_data_block(family_base_nested_data_block):
    """
    Sorts family data blocks into a dictionary where key, from 1 onwards, is the level of nesting indicated by number of '::' in root path string.

    After sorting it compares adjacent blocks in the dictionary (key and key + 1) for overlaps in the root path string. Only unique families will be returned.

    :param family_base_nested_data_block: A list containing all nested families belonging to a single root host family.
    :type family_base_nested_data_block: [nestedFamily]
    :return: A list of unique families in terms of root path.
    :rtype: [nestedFamily]
    """

    culled_family_base_nested_data_blocks = []
    data_blocks_by_length = {}
    # build dic by root path length
    # start at 1 because for nesting level ( 1 based rather then 0 based )
    for family in family_base_nested_data_block:
        if len(family.rootPath) - 1 in data_blocks_by_length:
            data_blocks_by_length[len(family.rootPath) - 1].append(family)
        else:
            data_blocks_by_length[len(family.rootPath) - 1] = [family]

    # loop over dictionary and check block entries against next entry up blocks
    for i in range(1, len(data_blocks_by_length) + 1):
        # last block get automatically added
        if i == len(data_blocks_by_length):
            culled_family_base_nested_data_blocks = (
                culled_family_base_nested_data_blocks + data_blocks_by_length[i]
            )
        else:
            # check for matches in next one up
            unique_nodes = _check_data_blocks_for_over_lap(
                data_blocks_by_length[i], data_blocks_by_length[i + 1]
            )
            # only add non overlapping blocks
            culled_family_base_nested_data_blocks = (
                culled_family_base_nested_data_blocks + unique_nodes
            )
    return culled_family_base_nested_data_blocks


def _cull_nested_base_data_blocks(overall_family_base_nested_data):
    """
    Reduce base data families for parent / child finding purposes. Keep the nodes with the root path longest branch only.

    Sample:

    famA :: famB :: famC
    famA :: famB

    The second of the above examples can be culled since the first contains the same information.

    :param overall_family_base_nested_data: A list containing all nested families with the longest nesting levels per branch per host family.
    :type overall_family_base_nested_data: [nestedFamily]
    """

    current_root_fam_name = ""
    family_blocks = []
    block = []
    # read families into blocks
    for nested in overall_family_base_nested_data:
        if nested.rootPath[0] != current_root_fam_name:
            # read family block
            if len(block) > 0:
                family_blocks.append(block)
                # reset block
                block = []
                block.append(nested)
                current_root_fam_name = nested.rootPath[0]
            else:
                block.append(nested)
                current_root_fam_name = nested.rootPath[0]
        else:
            block.append(nested)

    retained_family_base_nested_data = []
    # cull data per block
    for family_block in family_blocks:
        d = _cull_data_block(family_block)
        retained_family_base_nested_data = retained_family_base_nested_data + d

    return retained_family_base_nested_data


def find_parents_and_children(
    overall_family_base_root_data, overall_family_base_nested_data
):
    """
    Loop over all root families and check if they exist in root path of any nested families.
    if so extract families higher up the root path tree as parents and families further down the root path tree as children

    :param overall_family_base_root_data: List of tuples containing root family data.
    :type overall_family_base_root_data: [rootFamily]
    :param overall_family_base_nested_data: List of tuples containing nested family data.
    :type overall_family_base_nested_data: [nestedFamily]

    :return: List of tuples containing root family data.
    :rtype: [rootFamily]
    """

    for i in range(len(overall_family_base_root_data)):
        # print ('checking family :' , i, ' ', overall_family_base_root_data[i].name)
        for nested_fam in overall_family_base_nested_data:
            try:
                # get the index of the match
                index_match = nested_fam.rootPath.index(
                    overall_family_base_root_data[i].name
                )
                if index_match > 0:

                    # print('found ', overall_family_base_root_data[i].name ,' in ', nested_fam.rootPath)
                    _extract_parent_families(
                        overall_family_base_root_data[i], nested_fam.rootPath
                    )

                    _extract_child_families(
                        overall_family_base_root_data[i], nested_fam.rootPath
                    )

                    # print('after: ', overall_family_base_root_data[i].child)
            except:
                pass
    return overall_family_base_root_data


def find_circular_references(overall_family_base_root_data):
    """
    Loops over family data and returns any families which appear in circular references.
    (A family appears in their parent and child collection)

    :param overall_family_base_root_data: List of tuples containing root family data.
    :type overall_family_base_root_data: [rootFamily]

    :return: List of tuples containing root family data.
    :rtype: [rootFamily]
    """

    circular_references = []
    # loop over all families and check whether there are any families in both the parent as well as child collection
    for family in overall_family_base_root_data:
        for parent_family in family.parent:
            if parent_family in family.child:
                circular_references.append(family)
    return circular_references


def check_families_have_circular_references(family_base_data_report_file_path):
    """
    Processes a family base data report and identifies any families which contain circular reference.

    Makes use of multithreading when more then 2 cores are present.

    :param family_base_data_report_file_path: Fully qualified file path to family base data report file.
    :type family_base_data_report_file_path: str

    :return:
        Result class instance.

        - result.status. True if circular referencing file was written successfully, otherwise False.
        - result.message will contain the summary messages of the process including time stamps.
        - result.result empty list

        On exception:

        - result.status (bool) will be False.
        - result.message will contain generic exception message.
        - result.result will be empty

    :rtype: :class:`.Result`
    """

    # set up a timer
    t_process = Timer()
    t_process.start()

    return_value = res.Result()
    # read overall family base data and nested data from file
    (
        overall_family_base_root_data,
        overall_family_base_nested_data,
    ) = rFamBaseDataUtils.read_overall_family_data_list(
        family_base_data_report_file_path
    )
    return_value.append_message(
        "{} Read overall family base data report. {} root entries found and {} nested entries found.".format(
            t_process.stop(),
            len(overall_family_base_root_data, len(overall_family_base_nested_data)),
        )
    )
    t_process.start()

    before = len(overall_family_base_nested_data)
    # reduce workload by culling not needed nested family data
    overall_family_base_nested_data = _cull_nested_base_data_blocks(
        overall_family_base_nested_data
    )
    return_value.append_message(
        " {} culled nested family base data from : {} to: {} families.".format(
            t_process.stop(), before
        ),
        len(overall_family_base_nested_data),
    )
    t_process.start()

    # set up some multithreading
    core_count = int(os.environ["NUMBER_OF_PROCESSORS"])
    if core_count > 2:
        return_value.append_message("cores: ".format(core_count))
        # leave some room for other processes
        core_count = core_count - 1
        chunk_size = len(overall_family_base_root_data) / core_count
        threads = []
        # set up threads
        for i in range(core_count):
            t = threading.Thread(
                target=find_parents_and_children,
                args=(
                    overall_family_base_root_data[
                        i * chunk_size : (i + 1) * chunk_size
                    ],
                    overall_family_base_nested_data,
                ),
            )
            threads.append(t)
        # start up threads
        for t in threads:
            t.start()
        # wait for results
        for t in threads:
            t.join()
    else:
        # find parents and children
        overall_family_base_root_data = find_parents_and_children(
            overall_family_base_root_data, overall_family_base_nested_data
        )

    return_value.append_message(
        "{} Populated parents and children properties of: {} root families".format(
            t_process.stop(), len(overall_family_base_root_data)
        )
    )
    t_process.start()

    # identify circular references
    circular_references = find_circular_references(overall_family_base_root_data)
    return_value.append_message(
        "{} Found: {} circular references in families.".format(
            t_process.stop(), len(circular_references)
        )
    )
    if len(circular_references) > 0:
        return_value.result = circular_references
    return return_value
