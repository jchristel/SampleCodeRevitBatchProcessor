"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Family Base data analysis module containing functions to find circular family referencing in extracted data.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A circular reference is when a family A has a family B nested but family B has also family A nested.

Algorithm description:


- read families into data family objects
- process them ( to get the internal nesting set up)
- get the shortest path from each family
- check for duplicates in those paths ( may need to get unique path for name and category!)

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

from duHast.Utilities.Objects.timer import Timer
from duHast.Utilities.Objects import result as res
from duHast.Revit.Family.Data.family_data_family_processor_utils import process_data


def find_circular_reference(family_data, result_list):
    """
    Function to find circular references in families.

    :param family_data: list of family data objects
    :type family_data: list
    :param result_list: list to store families with circular references
    :type result_list: list of tuples with two entries (
        0 index the family_data_family object,
        1 index list of tuples with two entries in format
            0 index the nesting level as integer at which the circular nesting occurs
            1 index a string in format  family name :: family category
            )

    :return: list of tuples containing family with circular references at 0 and circular family data at 1
    """

    # loop over all family data
    for family in family_data:
        # process each family and check for circular references
        circular_families = family.has_circular_nesting()
        if len(circular_families) > 0:
            result_list.append((family, circular_families))
    return result_list


def check_families_have_circular_references(family_base_data_report_file_path):
    """
    Function to check if families have circular references.

    :param family_base_data_report_file_path: path to family base data report file
    :type family_base_data_report_file_path: str

    :return: A result object with the success status and the circular reference check result

        . result is a list of tuples with two entries (
            0 index the family_data_family object,
            1 index list of tuples with two entries in format
                0 index the nesting level as integer at which the circular nesting occurs
                1 index a string in format  family name :: family category
                )

    :rtype: :class:`.Result`

    """

    # read families into data family objects
    # check for duplicate family names in nesting tree

    return_value = res.Result()

    # set up a timer
    t_process = Timer()
    t_process.start()

    try:

        # load and process families
        families_processed_result = process_data(
            family_base_data_report_file_path=family_base_data_report_file_path,
            do_this=find_circular_reference,
        )

        # check if processing was successful, otherwise get out
        if families_processed_result.status == False:
            raise ValueError(families_processed_result.message)

        # get results
        families = []
        families_with_circular_nesting = []
        for nested_tuple in families_processed_result.result:
            families.append(nested_tuple[0])
            families_with_circular_nesting.extend(nested_tuple[1])

        # append messages debug
        return_value.append_message(families_processed_result.message)

        return_value.append_message(
            "{} Found: {} circular references in families.".format(
                t_process.stop(), len(families_with_circular_nesting)
            )
        )

        # return families which have circular references
        if len(families_with_circular_nesting) > 0:
            return_value.result = families_with_circular_nesting

    except Exception as e:
        return_value.update_sep(
            False,
            "An error occurred while reading the families into data objects.{}".format(
                e
            ),
        )

    return return_value
