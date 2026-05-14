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

import os

from duHast.Utilities.Objects.result import Result
from duHast.Revit.Family.family_functions import get_name_to_family_dict
from duHast.Revit.Common.Objects.FailureHandlingConfiguration import (
    FailureHandlingConfig,
)

from duHast.pyRevit.console_output import print_header
from duHast.Revit.Common.failure_handling import with_failures_processing_handler
from duHast.Revit.Common import file_io as rFile
from duHast.pyRevit.UI.ui_element_selection import get_element_selection_from_user

from duHast.Utilities.directory_io import create_target_directory
from duHast.Utilities.files_io import file_exist

# set up some options for the user to select
SINGLE_FOLDER_OPTION = "Single folder"
OVERWRITE_EXISTING_FAMILIES_OPTION = "Overwrite existing families"


def print_me(message):
    """
    A function to print a message to the console from the failure handling function

    :param message: the message to print
    :type message: str
    """

    print(message)


def get_save_out_directory(base_directory, category_name, save_out_single_directory):
    """
    Gets the directory to save out the family to. If save_out_single_directory is True then the base_directory is returned. If save_out_single_directory is False then the category_name is appended to the base_directory and returned.
    This will also create the target directory if it does not exist.


    :param base_directory: the base directory to save out to
    :type base_directory: str
    :param category_name: the category name to save out to
    :type category_name: str
    :param save_out_single_directory: whether to save out to a single directory
    :type save_out_single_directory: bool

    :return: the directory to save out to
    :rtype: str
    """

    if save_out_single_directory:
        return base_directory
    else:
        if category_name is not None:
            target_dir = os.path.join(base_directory, category_name)
            create_folder_flag = create_target_directory(base_directory, category_name)
            if create_folder_flag:
                return target_dir
            else:
                return base_directory
        else:
            return base_directory


def get_user_options(forms):
    """
    Gets the user options for saving out families

    Options are: save out to single directory, exclude existing families, overwrite existing families

    :param forms: the forms object
    :type forms: Forms
    :return: the user options
    :rtype: dict
    """

    # ask user for single directory or directory by category
    # and if existing families are to be ignored
    ops = []
    switches = [SINGLE_FOLDER_OPTION, OVERWRITE_EXISTING_FAMILIES_OPTION]
    configs = {
        SINGLE_FOLDER_OPTION: {"background": "0xFF55FF"},
        OVERWRITE_EXISTING_FAMILIES_OPTION: {"background": "0xFF55FF"},
    }
    ui_options, ui_switches = forms.CommandSwitchWindow.show(
        ops, switches=switches, message="Select Option", config=configs
    )

    return ui_switches


def save_loaded_families_entry(doc, output, forms, simple_ui=True):
    """
    Saves out selected families to a folder

    :param doc: the Revit document
    :type doc: Autodesk.Revit.DB.Document
    :param output: pyRevit output
    :type output: pyRevit output module
    :param forms: pyRevit forms
    :type forms: pyRevit forms module

    :return:
        Result class instance.

        - result.status (bool) True if families where saved without an exception, otherwise False.
        - result.message contains log messages.
        - result.result will be an empty list.

        On exception:

        - result.status (bool) will be False.
        - result.message will contain exception message.
    :rtype: :class:`.Result`
    """

    return_value = Result()

    try:

        def element_getter(doc):
            # get families in model
            families = get_name_to_family_dict(doc)
            fam_elements = []
            for fam_name, family in families.items():
                # filter out families which cannot be saved
                if family.IsEditable:
                    fam_elements.append(family)

            return fam_elements

        # get user to select families
        elements_selected = get_element_selection_from_user(
            doc=doc,
            forms=forms,
            element_getter=element_getter,
            element_selection_description="select families to export",
            multiselect=True,
        )

        # get user to select which ones to save out
        if len(elements_selected) == 0:
            message = "no families to export selected"
            print(message)
            return_value.append_message(message=message)
            return return_value
        else:
            print("{} families selected to save out".format(len(elements_selected)))

        # get user to select a directory
        family_out_folder_path = None
        family_out_folder_path = forms.pick_folder("Select the family export folder")
        if family_out_folder_path is None:
            message = "No folder selected. Exiting."
            print(message)
            return_value.update_sep(False, message=message)
            return return_value

        else:
            print("Saving families to directory: {}".format(family_out_folder_path))

        # set switches based on user input
        save_out_single_directory = True
        overwrite_existing_families = True
        # get user choices
        if not simple_ui:
            rswitches = get_user_options(forms)
            if rswitches is not None:
                save_out_single_directory = rswitches[SINGLE_FOLDER_OPTION]
                overwrite_existing_families = rswitches[
                    OVERWRITE_EXISTING_FAMILIES_OPTION
                ]

        # define failure handling for the transaction ( do not roll back on any warnings or errors )
        failure_handling_settings = FailureHandlingConfig(
            roll_back_on_warning=False,
            print_warnings=True,
            roll_back_on_error=False,
            print_errors=True,
            output_function=print_me,
        )

        print_header("Starting to save families...")
        # set up a pyRevit progress bar
        with forms.ProgressBar(
            title="Saving families: {value} of {max_value}", cancellable=True
        ) as pb:

            try:
                # set progress counter
                counter = 0

                # loop over selected families
                for fam_id in elements_selected:

                    # get the family from the document
                    fam = doc.GetElement(fam_id)

                    # check if the family can be saved in the first place
                    if fam.IsEditable:

                        # set up an action to be run per family...otherwise if all families run in one action this will
                        # stop the family export if one fails...this way it will continue to the next family
                        def action():

                            action_return_value = Result()
                            # set up a placeholder for the family document
                            family_doc = None

                            # open family
                            try:
                                # Get Family document for family
                                family_doc = doc.EditFamily(fam)
                                message = "Opened family: {}".format(fam.Name)
                                print(message)
                                return_value.append_message(message=message)
                            except Exception as e:
                                message = "Failed to open family {} with {}".format(
                                    fam.Name, e
                                )
                                print(message)
                                return_value.append_message(message=message)

                            # update progress
                            pb.update_progress(counter, len(elements_selected))

                            # save out family directory
                            family_out_folder_specific = get_save_out_directory(
                                base_directory=family_out_folder_path,
                                category_name=fam.FamilyCategory.Name,  # needs updating
                                save_out_single_directory=save_out_single_directory,
                            )

                            # attempt to save family if it was opened ok
                            if family_doc is not None:
                                # check if family already exists in target directory
                                if (
                                    file_exist(
                                        os.path.join(
                                            family_out_folder_specific,
                                            fam.Name + ".rfa",
                                        )
                                    )
                                    and overwrite_existing_families
                                ) or not file_exist(
                                    os.path.join(
                                        family_out_folder_specific, fam.Name + ".rfa"
                                    )
                                ):
                                    try:
                                        # save family out
                                        save_result = rFile.save_as_family(
                                            family_doc,
                                            family_out_folder_specific,
                                            fam.Name,
                                            [[fam.Name, fam.Name]],
                                        )
                                        if save_result.status:
                                            print("Saved family: {}".format(fam.Name))
                                        action_return_value.update(save_result)
                                    except Exception as e:
                                        message = (
                                            "Failed to save family {} with {}".format(
                                                fam.Name, e
                                            )
                                        )
                                        print(message)
                                        action_return_value.update_sep(
                                            False, message=message
                                        )
                                else:
                                    message = "Family {} already exists in target folder: {}. Skipping".format(
                                        fam.Name, family_out_folder_specific
                                    )
                                    print(message)
                                    action_return_value.append_message(message=message)

                                return action_return_value
                            else:
                                message = "Could not retrieve family document. Skipping family: {}".format(
                                    fam.Name
                                )
                                print(message)
                                action_return_value.append_message(message=message)
                            return action_return_value

                        # run the action
                        dummy = with_failures_processing_handler(
                            app=doc.Application,
                            action=action,
                            fail_config=failure_handling_settings,
                        )
                        return_value.update(dummy)
                    else:
                        message = "Cant save family: {} (Is a system family?)".format(
                            fam.Name
                        )
                        print(message)
                        return_value.append_message(message=message)

                    # update progress
                    counter = counter + 1

                    # cancelled?
                    if pb.cancelled:
                        message = "User cancelled."
                        print(message)
                        return_value.update_sep(False, message=message)
                        # leave loop
                        break

            except Exception as e:
                message = "Failed to save families with exception: {}".format(e)
                print(message)
                return_value.update_sep(False, message=message)
    except Exception as e:
        message = "Failed to save families with exception: {}".format(e)
        print(message)
        return_value.update_sep(False, message=message)

    # print ("\n{}".format(return_value.message))
    print("Finished")

    return return_value
