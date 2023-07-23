"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Finds host families of nested families requiring to be renamed.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- read file rename change list:
-   text file (tab separated) with columns: currentFamilyName   currentFamilyFilePath	categoryName newFamilyName
-   note: current family file path could be blank in situations where just a rename of a nested family is required...
- read base data file processing list (created by RevitFamilyBaseDataProcessor module)
- extract all root families (no :: in root path)
- extract all nested families ( :: in root path)
- loop over nested families and find any family where:
    - family at first nesting level is in rename list by name and category
    - extract root family name and add to identified host family list

- loop over root families
-   find match in identified host families
- write out root family date: family file path, family name, category

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

# import clr
# import System
from duHast.Utilities.Objects.timer import Timer

from duHast.Utilities.Objects import result as res

# from duHast.Utilities import Utility as util
from duHast.Revit.Family.Data import family_base_data_utils as rFamBaseDataUtils
from duHast.Revit.Family import family_rename_files_utils as rFamRenameUtils

# ---------------------------------------------------------------------------------------------------------------
#                      find families containing nested families needing to be renamed
# ---------------------------------------------------------------------------------------------------------------


def _find_host_families(overall_family_base_nested_data, file_rename_list):
    """
    Finds all root family names and categories where the first level nested family is one which needs to be renamed.

    :param overall_family_base_nested_data: A list containing all root families.
    :type overall_family_base_nested_data: [rootFamily]
    :param file_rename_list: A list containing all families needing to be renamed.
    :type file_rename_list: [renameFamily]

    :return: A dictionary where:

        - key is the family name and category concatenated and
        - value is a tuple in format 0: family name, 1: family category

    :rtype: {str: (str,str)}
    """

    host_families = {}
    for file_rename_family in file_rename_list:
        hosts = rFamBaseDataUtils.find_direct_host_families(
            file_rename_family, overall_family_base_nested_data
        )
        # update dictionary with new hosts only
        for h in hosts:
            if h not in host_families:
                host_families[h] = hosts[h]
    return host_families


def find_host_families_with_nested_families_requiring_rename(input_directory_path):
    """
    Finds all host families in data set containing nested families needing to be renamed.

    :param input_directory_path: Fully qualified directory path containing rename directives and family base data report.
    :type input_directory_path: str

    :return:
        Result class instance.

        - result.status: True if any host families are found with nested families needing renaming, otherwise False.
        - result.message: processing steps with time stamps
        - result.result: [rootFamily]

        On exception:

        - result.status (bool) will be False.
        - result.message will contain an exception message
        - result.result will be empty

    :rtype: :class:`.Result`
    """

    # set up a timer
    t_process = Timer()
    t_process.start()

    return_value = res.Result()
    # read overall family base data from file
    try:
        (
            overall_family_base_root_data,
            overall_family_base_nested_data,
        ) = rFamBaseDataUtils.read_overall_family_data_list_from_directory(
            input_directory_path
        )
        return_value.append_message(
            "{} Read overall family base data report. {} root entries found and {} nested entries found.".format(
                t_process.stop(),
                len(overall_family_base_root_data),
                len(overall_family_base_nested_data),
            )
        )
        # check if input file existed and contained data
        if len(overall_family_base_root_data) > 0:
            t_process.start()
            file_rename_list_status = rFamRenameUtils.get_rename_directives(
                input_directory_path
            )
            return_value.append_message(
                "{} Read data from file! Rename family entries [{} ] found.".format(
                    t_process.stop(), len(file_rename_list_status.result)
                )
            )
            # check if any rename directives
            if len(file_rename_list_status.result) > 0:
                before = len(overall_family_base_nested_data)
                t_process.start()
                # reduce workload by culling not needed nested family data
                overall_family_base_nested_data = (
                    rFamBaseDataUtils.cull_nested_base_data_blocks(
                        overall_family_base_nested_data
                    )
                )
                return_value.append_message(
                    "{} Culled nested family base data from : {} to: {} families.".format(
                        t_process.stop(), before
                    ),
                    len(overall_family_base_nested_data),
                )

                t_process.start()
                # get a list of simplified root data families extracted from nested family path data
                root_fam_simple = rFamBaseDataUtils.find_all_direct_host_families(
                    file_rename_list_status.result, overall_family_base_nested_data
                )
                return_value.append_message(
                    "{} Found simplified root families: {}".format(
                        t_process.stop(), len(root_fam_simple)
                    )
                )

                t_process.start()
                # identify actual root families with nested families at top level which require renaming.
                root_families = rFamBaseDataUtils.find_root_families_from_hosts(
                    root_fam_simple, overall_family_base_root_data
                )
                return_value.append_message(
                    "{} Found {} root families.".format(
                        t_process.stop(), len(root_families)
                    )
                )
                return_value.result = root_families
            else:
                return_value.update_sep(
                    False, "No rename directives found. Aborted operation!"
                )
        else:
            return_value.update_sep(
                False, "No base family data found. Aborted operation!"
            )
    except Exception as e:
        return_value.update_sep(
            False, "Failed to find host families with exception: ".format(e)
        )
    return return_value
