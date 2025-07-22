# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2025, Jan Christel
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

from duHast.Utilities.Objects.result import Result
from duHast.pyRevit.console_output import print_header
from duHast.Utilities.files_get import (
    get_files_from_directory_walker_with_filters_simple,
)
from duHast.Revit.Family.family_utils import load_family
from duHast.Revit.Common.Objects.FailureHandlingConfiguration import (
    FailureHandlingConfig,
)
from duHast.Utilities.files_io import remove_backup_revit_files_from_list
import os


def print_me(message):
    """
    A function to print a message to the console from the failure handling function

    :param message: the message to print
    :type message: str
    """

    print(message)


def get_families(directory):
    """
    Get all families in a directory and discard any family that occurs more than once

    :param directory: the directory to search for families
    :type directory: str
    :return: a list of unique family file paths
    :rtype: list
    """

    families_in_directory = get_files_from_directory_walker_with_filters_simple(
        folder_path=directory, file_extension=".rfa"
    )

    filtered_families = []
    file_names = []

    # filter out family backup files ( ending in .00??.rfa )
    families_in_directory = remove_backup_revit_files_from_list(families_in_directory)

    # filter out families which occur more than once
    for path in families_in_directory:
        file_name = os.path.basename(path)
        if file_name not in file_names:
            filtered_families.append(path)

    return filtered_families


def get_user_selection(forms, families):
    """
    Get user to select families to load

    :param families: a list of family file paths
    :type families: list
    :return: a list of family file paths selected by the user
    :rtype: list
    """

    # check if we got any?
    if len(families) == 0:
        return None

    # get the user to select the source ( returns a string)
    selection = forms.SelectFromList.show(
        sorted(families), button_name="Select families to load", multiselect=True
    )

    if selection == None:
        return None
    else:
        return selection


def load_families(doc, families, forms):
    """
    Load families into the document.

    :param doc: the revit document
    :type doc: Document
    :param families: a list of family file paths
    :type families: list
    :param forms: the pyRevit forms module
    :type forms: module

    :return:
        Result class instance.

        - result.status (bool) True if families where loaded without an exception, otherwise False.
        - result.message contains log messages.
        - result.result will be an empty list.

        On exception:

        - result.status (bool) will be False.
        - result.message will contain exception message.
    :rtype: :class:`.Result`
    """

    # set up a status tracker
    return_value = Result()

    print_header("Starting to load families...")

    max_counter = len(families)
    counter = 0

    # define failure handling for the transaction ( roll back on any warnings or errors )
    failure_handling_config = FailureHandlingConfig(
        roll_back_on_warning=True,
        print_warnings=True,
        roll_back_on_error=True,
        print_errors=True,
        output_function=print_me,
    )

    # set up a pyrevit progress bar
    with forms.ProgressBar(
        title="Loading families: {value} of {max_value}", cancellable=True
    ) as pb:
        try:

            for fam in families:

                # update progress
                pb.update_progress(counter, max_counter)

                print("Loading family: {}".format(fam))
                # load family
                result_loader = load_family(
                    doc=doc,
                    family_file_path=fam,
                    failure_config=failure_handling_config,
                )
                print("{}".format(result_loader.message))

                return_value.update(result_loader)

                # update progress
                counter += 1

                # cancelled?
                if pb.cancelled:
                    message = "User cancelled."
                    print(message)
                    return_value.update_sep(False, message=message)
                    # get out of loop
                    break

        except Exception as e:
            message = "Failed to load families with exception: {}".format(e)
            print(message)
            return_value.update_sep(False, message=message)

    return return_value


def load_families_entry(doc, output, forms):
    """
    Entry point for loading families

    :param doc: the revit document
    :type doc: Document
    :param output: the pyRevit output module
    :type output: module
    :param forms: the pyRevit forms module
    :type forms: module

    :return:
        Result class instance.

        - result.status (bool) True if families where loaded without an exception, otherwise False.
        - result.message contains log messages.
        - result.result will be an empty list.

        On exception:

        - result.status (bool) will be False.
        - result.message will contain exception message.
    :rtype: :class:`.Result`
    """

    # set up a status tracker
    return_value = Result()

    try:

        # get user to select a directory
        family_out_folder_path = None
        family_out_folder_path = forms.pick_folder("Select the family import folder")
        if family_out_folder_path is None:
            message = "No folder selected. Exiting."
            print(message)
            return_value.update_sep(False, message=message)
            return return_value

        else:
            print("Loading families from directory: {}".format(family_out_folder_path))

        # get all families in that directory and discard any family that occurs more than once
        families_to_load = get_families(family_out_folder_path)

        # show user a list of families to load
        families_to_load_filtered = get_user_selection(forms, families_to_load)
        if families_to_load_filtered is None:
            message = "No families selected to load. Exiting."
            print(message)
            return_value.update_sep(False, message=message)
            return return_value

        # load families
        result_load = load_families(doc, families_to_load_filtered, forms)

        # report on what was loaded
        return_value.update(result_load)

    except Exception as e:
        message = "Failed to load families with exception: {}".format(e)
        print(message)
        return_value.update_sep(False, message=message)

    # print ("\n{}".format(return_value.message))
    print("Finished")

    return return_value
