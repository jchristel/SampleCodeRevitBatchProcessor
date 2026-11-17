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
from duHast.Revit.Family.Data.family_data_family_utils import (
    get_report_file_path,
    read_root_families_from_report,
    get_direct_host_root_families,
)
from duHast.Revit.Family.Data.Objects.family_base_data_processor_defaults import (
    DATA_REPORT_NAME as FAMILY_BASE_DATA_REPORT_NAME,
)
from duHast.Revit.Family import family_rename_files_utils as rFamRenameUtils
from duHast.Revit.Family.Data.Objects.family_data_family import FamilyDataFamily

# ---------------------------------------------------------------------------------------------------------------
#                      find families containing nested families needing to be renamed
# ---------------------------------------------------------------------------------------------------------------


def find_host_families_with_nested_families_requiring_rename(input_directory_path):
    """
    Finds all host families in data set containing nested families needing to be renamed.

    :param input_directory_path: Fully qualified directory path containing rename directives and family base data report.
    :type input_directory_path: str

    :return:
        Result class instance.

        - result.status: True if any host families are found with nested families needing renaming, otherwise False.
        - result.message: processing steps with time stamps
        - result.result: [:class:`.FamilyDataFamily`] the root families which directly host a family to be renamed

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
    try:
        # read overall family base data from file
        report_file_path = get_report_file_path(
            input_directory_path, FAMILY_BASE_DATA_REPORT_NAME
        )
        if report_file_path is None:
            raise ValueError(
                "No family base data report found in: {}".format(input_directory_path)
            )
        read_result = read_root_families_from_report(report_file_path)
        if read_result.status is False:
            raise ValueError(read_result.message)
        root_families = read_result.result
        return_value.append_message(
            "{} Read overall family base data report. {} root families found.".format(
                t_process.stop(), len(root_families)
            )
        )
        # check if input file existed and contained data
        if len(root_families) > 0:
            t_process.start()
            file_rename_list_status = rFamRenameUtils.get_rename_directives(
                input_directory_path
            )
            return_value.append_message(
                "{} Read data from file! Rename family entries [{}] found.".format(
                    t_process.stop(), len(file_rename_list_status.result)
                )
            )
            # check if any rename directives
            if len(file_rename_list_status.result) > 0:
                t_process.start()
                # identify actual root families with nested families at top level which require renaming.
                host_root_families = get_direct_host_root_families(
                    root_families,
                    [
                        FamilyDataFamily(
                            family_name=directive.name,
                            family_category=directive.category,
                        )
                        for directive in file_rename_list_status.result
                    ],
                )
                return_value.append_message(
                    "{} Found {} root families.".format(
                        t_process.stop(), len(host_root_families)
                    )
                )
                return_value.result = host_root_families
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
            False, "Failed to find host families with exception: {}".format(e)
        )
    return return_value
