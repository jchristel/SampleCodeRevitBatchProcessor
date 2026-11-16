"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Family Base data analysis module containing functions to build a reload tree.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- read change list: csv file with a header row and columns: family name, family file path, category name
- read the family base data report into family instances
- find the direct hosts of the changed families, then the hosts of those hosts and so on, and write one task list per nesting level,
  so families are reloaded bottom up in their nesting hierarchy

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

from duHast.Utilities.Objects.timer import Timer
from duHast.Utilities.Objects import result as res
from duHast.Revit.Family.Data.family_reload_advanced_utils import (
    read_change_list,
    write_out_empty_task_list,
    write_reload_list_to_file,
)
from duHast.Revit.Family.Data.family_data_family_utils import (
    read_root_families_from_report,
    get_direct_host_root_families,
)

# reload levels written before giving up: a family nesting more levels deep than this indicates circular nesting
MAXIMUM_NUMBER_OF_TASK_LISTS = 20


def _remove_duplicates(list_one, list_two):
    """
    Splits the families in list one into those not in list two, and those in list two.

    :param list_one: Families
    :type list_one: [:class:`.FamilyDataFamily`]
    :param list_two: Families
    :type list_two: [:class:`.FamilyDataFamily`]
    :return: Two lists: families of list one not in list two, families of list one also in list two.
    :rtype: [:class:`.FamilyDataFamily`], [:class:`.FamilyDataFamily`]
    """

    new_list = []
    duplicates_list = []
    for l_one_item in list_one:
        if l_one_item not in list_two:
            new_list.append(l_one_item)
        else:
            duplicates_list.append(l_one_item)
    return new_list, duplicates_list


def build_work_lists(
    change_list_file_path,
    family_base_data_report_file_path,
    load_lists_output_directory_path,
):
    """
    Processes a file change list and a family base data report. From both reports it builds a lists for reloading families bottom up in their nesting hierarchy.

    A family hosting a changed family at more than one nesting level is reloaded at the highest level only (after everything it contains).

    :param change_list_file_path: Fully qualified file path to family change list report file.
    :type change_list_file_path: str
    :param family_base_data_report_file_path: Fully qualified file path to family base data report file.
    :type family_base_data_report_file_path: str
    :param load_lists_output_directory_path: Fully qualified directory path to which the task output files will be written
    :type load_lists_output_directory_path: str

    :return:
        Result class instance.

        - result.status. True if the task lists were written, otherwise False.
        - result.message will contain the processing steps with time stamps.
        - result.result will be empty.

        On exception (including more than 20 task lists, representing a family nesting level of 20 deep...unlikely):

        - result.status (bool) will be False.
        - result.message will contain the exception message.

    :rtype: :class:`.Result`
    """

    # set up a timer
    t_process = Timer()
    t_process.start()

    return_value = res.Result()
    try:
        change_list = read_change_list(change_list_file_path)
        return_value.append_message(
            "{} Change list of length [{}] loaded.".format(
                t_process.stop(), len(change_list)
            )
        )

        t_process.start()
        # read overall family base data from file
        read_result = read_root_families_from_report(family_base_data_report_file_path)
        if read_result.status is False:
            raise ValueError(read_result.message)
        root_families = read_result.result
        return_value.append_message(
            "{} Family base data of [{}] root families loaded.".format(
                t_process.stop(), len(root_families)
            )
        )

        if len(change_list) > 0:
            task_list_counter = 0
            # get the direct hosts of the changed families
            t_process.start()
            task_current_level = get_direct_host_root_families(root_families, change_list)
            return_value.append_message(
                "{} Direct hosts [{}] found.".format(
                    t_process.stop(), len(task_current_level)
                )
            )
            # get the hosts of the hosts
            t_process.start()
            task_next_level = get_direct_host_root_families(
                root_families, task_current_level
            )
            return_value.append_message(
                "{} Next level hosts [{}] found.".format(
                    t_process.stop(), len(task_next_level)
                )
            )
            while len(task_current_level) > 0:
                # a family which is also a host at the next level gets reloaded at that level
                cleaned_current_tasks, over_lap_tasks = _remove_duplicates(
                    task_current_level, task_next_level
                )
                if len(cleaned_current_tasks) > 0:
                    t_process.start()
                    result_write_to_disk = write_reload_list_to_file(
                        cleaned_current_tasks,
                        load_lists_output_directory_path,
                        task_list_counter,
                    )
                    return_value.update_sep(
                        result_write_to_disk,
                        "{} Wrote task list to file with status: {}".format(
                            t_process.stop(), result_write_to_disk
                        ),
                    )
                else:
                    empty_task_list_flag = write_out_empty_task_list(
                        load_lists_output_directory_path, task_list_counter
                    )
                    return_value.update_sep(
                        empty_task_list_flag,
                        "Wrote empty task list at counter [{}]".format(
                            task_list_counter
                        ),
                    )
                # move one level up
                task_current_level = list(task_next_level)
                return_value.append_message(
                    "Swapping next level hosts to direct hosts [{}]".format(
                        len(task_current_level)
                    )
                )
                t_process.start()
                task_next_level = get_direct_host_root_families(
                    root_families, task_current_level
                )
                return_value.append_message(
                    "{} Next level hosts [{}]".format(
                        t_process.stop(), len(task_next_level)
                    )
                )
                task_list_counter = task_list_counter + 1
                if task_list_counter > MAXIMUM_NUMBER_OF_TASK_LISTS:
                    raise ValueError(
                        "Exceeded maximum number of task list files ({}): circular family nesting?".format(
                            MAXIMUM_NUMBER_OF_TASK_LISTS
                        )
                    )
        else:
            return_value.update_sep(
                True, "Empty change list found. No families require processing."
            )
    except Exception as e:
        return_value.update_sep(
            False, "Failed to build reload task lists with exception: {}".format(e)
        )
    return return_value
