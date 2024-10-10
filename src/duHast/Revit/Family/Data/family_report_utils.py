"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Family report data utility module containing functions to manipulate report files.
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

from duHast.Utilities.Objects.result import Result
from duHast.Revit.Family.Data.family_report_reader import read_data_into_families
from duHast.Utilities.files_io import file_exist


def _check_families_still_exist(family_data):
    """
    Checks whether families still exist on file server.

    Reason why families no longer exist:

    - family got deleted or moved
    - family got renamed

    :param famData: A list containing FamilyDataFamily instances.
    :type famData: [:class:`.FamilyDataFamily`]

    :return:
        Result class instance.

        - .status True if successfully removed any outdated family data or None needed removing. Otherwise False.
        - .message will contain list of families removed or message nothing needed to be removed.
        - . result will contain new list of FamilyDataFamily instances which still exist on the file server

        On exception:

        - result.status (bool) will be False.
        - result.message will contain generic exception message.
        - result.result will be empty
    :rtype: :class:`.Result`
    """

    return_value = Result()
    filtered_list = []
    family_was_removed = False
    try:
        # check which ones do not exist anymore
        for family_data_instance in family_data:
            if file_exist(family_data_instance.family_file_path):
                filtered_list.append(family_data_instance)
            else:
                return_value.append_message(
                    "Removed family: {}".format(family_data_instance.family_file_path)
                )
                family_was_removed = True

        if family_was_removed == False:
            return_value.append_message("No family required removing from data.")

        # update return data
        return_value.update_sep(True, "Successfully updated family data.")
        return_value.result = filtered_list

    except Exception as e:
        return_value.update_sep(
            False,
            "Failed to check whether families still exist with exception: {}".format(e),
        )
    return return_value


def combine_reports(previous_report_path, new_report_path):
    """
    This combines family reports:

    - reading reports into FamilyDataFamily instances
    - comparing the previous report families with the new report families and
        - adding any new families found in the new reports
        - adding previous report families not found in new report families

    This function checks at the end whether families still exist on file server. If not, they will be removed from the data set.

    :param previous_report_path: A fully qualified file path to the previous report file.
    :type previous_report_path: str
    :param new_report_path: A fully qualified file path to the new report file.
    :type new_report_path: str

    :return:
        Result class instance.

        - .status True if successfully combined report(s). Otherwise False.
        - .message will contain count of new families added and previous families retained.
        - . result will contain list of FamilyDataFamily instances representing the combined data set

        On exception:

        - result.status (bool) will be False.
        - result.message will contain generic exception message.
        - result.result will be empty
    :rtype: :class:`.Result`
    """

    return_value = Result()
    combined_families = []
    try:
        # checks:
        # are past in path strings
        if isinstance(previous_report_path, str) == False:
            raise TypeError(
                "previous_report_path should be of type string but is: {}".format(
                    type(previous_report_path)
                )
            )
        if isinstance(new_report_path, str) == False:
            raise TypeError(
                "new_report_path should be of type string but is: {}".format(
                    type(new_report_path)
                )
            )

        # read values from previous path
        previous_families_read_result = read_data_into_families(
            path_to_data=previous_report_path
        )
        # check read was successful
        if previous_families_read_result.status == False:
            raise ValueError(previous_families_read_result.message)
        else:
            return_value.append_message(
                "Successfully read {} families from: {}".format(
                    len(previous_families_read_result.result), previous_report_path
                )
            )

        # read values from new path
        new_families_read_result = read_data_into_families(path_to_data=new_report_path)
        # check read was successful
        if new_families_read_result.status == False:
            raise ValueError(new_families_read_result.message)
        else:
            return_value.append_message(
                "Successfully read {} families from: {}".format(
                    len(new_families_read_result.result), new_report_path
                )
            )

        # some stats:
        new_families_added = 0
        previous_families_retained = 0

        # check if any new families where retrieved
        if len(new_families_read_result.result) > 0:
            new_families_added = len(new_families_read_result.result)
            combined_families = new_families_read_result.result
            # take new families as base line and append previous report families only which have no match in new families
            for previous_family in previous_families_read_result.result:
                if previous_family not in combined_families:
                    combined_families.append(previous_family)
                    previous_families_retained += 1
        else:
            # return previous families unchanged since no new families exist
            combined_families = previous_families_read_result.result
            previous_families_retained = len(previous_families_read_result.result)

        # set the return value
        return_value.append_message(
            "Combined report contains {} new families and {} previous report families where retained.".format(
                new_families_added, previous_families_retained
            )
        )
        return_value.result = combined_families

        # check if all families still exist on the server...if not remove from list
        check_files_exists = _check_families_still_exist(combined_families)
        if check_files_exists.status:
            if len(check_files_exists.result) != len(combined_families):
                return_value.append_message(
                    "Removed {} families from data set as they no longer exist on server.".format(
                        len(combined_families) - len(check_files_exists.result)
                    )
                )
                return_value.result = check_files_exists.result
            else:
                return_value.append_message(
                    "All families still exist on server. None was removed from data set."
                )
        else:
            return_value.update_sep(
                False,
                "Failed to check file exists with exception: {}".format(
                    check_files_exists.message
                ),
            )
            # reset the result to an empty list!
            return_value.result = []

    except Exception as e:
        return_value.update_sep(
            False, "An exception ocurred when combining reports: {}".format(e)
        )

    return return_value
