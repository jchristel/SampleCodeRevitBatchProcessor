"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Family Base data analysis module containing functions to build a reload tree.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- read change list:
-   text file (tab separated) with columns:familyName	familyFilePath	categoryName
- read overall family base data list
- get direct parents of change list families
- get next level parents of direct parents

- loop direct parent list until empty:
-   - remove any direct parents which also exist in next level parents
-   - write direct parents to file
-   - set next level parents as direct parents
-   - find all direct parents of changed families in base data list

- those reload lists will then be separated into work chunks by file list writer...

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


from duHast.Utilities.Objects.timer import Timer
from duHast.Utilities.Objects import result as res
from duHast.Utilities import (
    files_get as fileGet,
    files_io as fileIO,
    files_tab as fileTab,
)
from duHast.Revit.Family.Data import family_base_data_utils as rFamBaseDataUtils
from duHast.Revit.Family.Data import family_reload_advanced_utils as rFamReloadAdvUtils

_TASK_COUNTER_FILE_PREFIX = "TaskOutput"


def _write_reload_list_to_file(reload_families, directory_path, counter=0):
    """
    Writes task list file to disk. File contains single column of fully qualified file path.

    :param reload_families: List of tuples representing families requiring their nested families to be re-loaded.
    :type reload_families: [rootFamily]
    :param directory_path: Fully qualified directory path to which the task files will be written.
    :type directory_path: str
    :param counter: Task file name suffix, defaults to 0
    :type counter: int, optional

    :return: True if file was written successfully, otherwise False.
    :rtype: bool
    """

    # write out file list without header
    header = []
    # data to be written to file
    overall_data = []
    file_name = (
        directory_path + "\\" + _TASK_COUNTER_FILE_PREFIX + str(counter) + ".txt"
    )
    # loop over families to get file path
    for r in reload_families:
        # row data
        data = []
        data.append(r.filePath)
        overall_data.append(data)
    try:
        # write data
        fileTab.write_report_data(file_name, header, overall_data, writeType="w")
        return True
    except Exception:
        return False


def _delete_old_task_lists(directory_path):
    """
    Deletes all overall task files in given directory.

    :param directory_path: Fully qualified directory path containing the task files to be deleted.
    :type directory_path: str
    :return: True if all files got deleted successfully, otherwise False.
    :rtype: bool
    """

    flag = True
    # find all files in folder starting with and delete them
    files = fileGet.get_files(directory_path, ".txt")
    if len(files) > 0:
        for f in files:
            if fileIO.get_file_name_without_ext(f).startswith(
                _TASK_COUNTER_FILE_PREFIX
            ):
                flag = flag & fileIO.file_delete(f)
    return flag


def _write_out_empty_task_list(directory_path, counter=0):
    """
    Writes out an empty task list in case nothing is to be reloaded.

    :param directory_path: Fully qualified directory path to which the task files will be written.
    :type directory_path: str
    :param counter: Task file name suffix, defaults to 0
    :type counter: int, optional

    :return: True if file was written successfully, otherwise False.
    :rtype: bool
    """

    file_name = directory_path + "\\" + "TaskOutput" + str(counter) + ".txt"
    # write out file list without header
    header = []
    # write out empty data
    overall_data = []
    try:
        # write data
        fileTab.write_report_data(file_name, header, overall_data, writeType="w")
        return True
    except Exception:
        return False


def _remove_duplicates(list_one, list_two):
    """
    Removes any item from list one which is present in list two.

    :param list_one: List of tuples containing root family data.
    :type list_one: [rFamBaseDataUtils.rootFamily]
    :param list_two: List of tuples containing root family data.
    :type list_two: [rFamBaseDataUtils.rootFamily]

    :return: _description_
    :rtype: _type_
    """

    new_list = []
    duplicates_list = []
    for l_one_item in list_one:
        if l_one_item not in list_two:
            new_list.append(l_one_item)
        else:
            duplicates_list.append(l_one_item)
    return new_list, duplicates_list


def _get_hosts(
    current_families, overall_family_base_nested_data, overall_family_base_root_data
):
    """
    Returns the direct ( one level up) host families of the current families.

    :param current_families: A list of current families represented as tuples (tuple need to have properties 'name' and 'category').
    :type current_families: [rFamBaseDataUtils.rootFamily] or [rFamBaseDataUtils.nestedFamily] or [rFamReloadAdvUtils.changedFamily]
    :param overall_family_base_nested_data: List of tuples containing nested family data.
    :type overall_family_base_nested_data: [rFamBaseDataUtils.nestedFamily]
    :param overall_family_base_root_data: List of tuples containing root family data.
    :type overall_family_base_root_data: [rFamBaseDataUtils.rootFamily]

    :return: A list of root families.
    :rtype: [rFamBaseDataUtils.rootFamily]
    """

    # get current change list host files
    direct_hosts = rFamBaseDataUtils.find_root_families_from_hosts(
        rFamBaseDataUtils.find_all_direct_host_families(
            current_families, overall_family_base_nested_data
        ),
        overall_family_base_root_data,
    )
    return direct_hosts


def build_work_lists(
    change_list_file_path,
    family_base_data_report_file_path,
    load_lists_output_directory_path,
):
    """
    Processes a file change list and a family base data report. From both reports it builds a lists for reloading families bottom up in their nesting hierarchy.

    :param change_list_file_path: Fully qualified file path to family change list report file.
    :type change_list_file_path: str
    :param family_base_data_report_file_path: Fully qualified file path to family base data report file.
    :type family_base_data_report_file_path: str
    :param load_lists_output_directory_path: Fully qualified directory path to which the task output files will be written
    :type load_lists_output_directory_path: str
    :raises Exception: "Infinite loop." Will be raised if more then 20 task output files are written (representing a family nesting level of 20 deep...unlikely)
    """

    # set up a timer
    t_process = Timer()
    t_process.start()

    return_value = res.Result()
    change_list = rFamReloadAdvUtils.read_change_list(change_list_file_path)
    return_value.append_message(
        t_process.stop()
        + " Change list of length ["
        + str(len(change_list))
        + "] loaded."
    )

    t_process.start()
    # read overall family base data from file
    (
        overall_family_base_root_data,
        overall_family_base_nested_data,
    ) = rFamBaseDataUtils.read_overall_family_data_list(
        family_base_data_report_file_path
    )
    return_value.append_message(
        t_process.stop()
        + " Nested base data list of length ["
        + str(len(overall_family_base_nested_data))
        + "] loaded."
    )

    if len(change_list) > 0:
        # list containing the hosts of the host families
        task_next_level = []
        # safety switch in case of infinite loop
        task_list_counter = 0

        t_process.start()
        task_current_level = _get_hosts(
            change_list, overall_family_base_nested_data, overall_family_base_root_data
        )
        return_value.append_message(
            t_process.stop()
            + " Direct hosts ["
            + str(len(task_current_level))
            + "] found."
        )

        t_process.start()
        task_next_level = _get_hosts(
            task_current_level,
            overall_family_base_nested_data,
            overall_family_base_root_data,
        )
        return_value.append_message(
            t_process.stop()
            + " Next level hosts ["
            + str(len(task_next_level))
            + "] found."
        )

        # loop until no more entries in current level tasks
        while len(task_current_level) > 0:

            # remove next level hosts from direct hosts list to avoid overlap in reload process
            cleaned_current_tasks, over_lap_tasks = _remove_duplicates(
                task_current_level, task_next_level
            )

            # write out cleaned up list:
            if len(cleaned_current_tasks) > 0:
                t_process.start()
                result_write_to_disk = _write_reload_list_to_file(
                    cleaned_current_tasks,
                    load_lists_output_directory_path,
                    task_list_counter,
                )
                return_value.update_sep(
                    result_write_to_disk,
                    t_process.stop()
                    + " Wrote task list to file with status: "
                    + str(result_write_to_disk),
                )
            else:
                # write out an empty task list!
                empty_task_list_flag = _write_out_empty_task_list(
                    load_lists_output_directory_path, task_list_counter
                )
                return_value.update_sep(
                    empty_task_list_flag,
                    "Wrote empty task list at counter [" + str(task_list_counter),
                )

            # swap lists to get to next level of loading
            task_current_level = list(task_next_level)
            return_value.append_message(
                "Swapping next level hosts to direct hosts ["
                + str(len(task_current_level))
                + "]"
            )

            t_process.start()
            # get next level host families (task)
            task_next_level = _get_hosts(
                task_current_level,
                overall_family_base_nested_data,
                overall_family_base_root_data,
            )
            return_value.append_message(
                t_process.stop()
                + " Next level hosts ["
                + str(len(task_next_level))
                + "] found."
            )

            # increase task list counter to be used in file name
            task_list_counter = task_list_counter + 1
            if task_list_counter > 20:
                # trigger fail save
                return_value.update_sep(
                    False, " Exceeded maximum number of task list files! (20)"
                )
                raise Exception("Infinite loop.")
    else:
        return_value.update_sep(
            True, "Empty change list found. No families require processing."
        )
    return return_value
