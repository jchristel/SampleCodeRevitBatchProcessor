"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A number of helper functions relating to pyrevit directory selection.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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


from duHast.Utilities.Objects.result import Result
from duHast.Utilities.directory_io import get_all_nested_directories

# set up some options for the user to select
SINGLE_FOLDER_OPTION = "Single folder"
NESTED_FOLDER_OPTION = "Include nested folders"


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
    ops = [SINGLE_FOLDER_OPTION,NESTED_FOLDER_OPTION]
    configs = {
        SINGLE_FOLDER_OPTION: {"background": "0xFF55FF"},
        NESTED_FOLDER_OPTION: {"background": "0xFF55FF"},
    }
    ui_options = forms.CommandSwitchWindow.show(
        ops,  message="Select Directory Option", config=configs
    )

    return ui_options


def get_process_directories(forms, form_title="Select directory"):
    """
    Gets the directories to process

    :param forms: the forms object
    :type forms: Forms
    :return: the directories to process
    :rtype: list
    """

    # set up a status tracker
    return_value = Result()
    try:

        # get the library directory path
        library_path = forms.pick_folder(title=form_title)
        if not library_path:
            message = "No directory selected."
            print(message)
            return_value.update_sep(False, message)
            return return_value
        
        # display UI to get user options re single or nested folders
        user_option =  get_user_options(forms)
        
        # check what came back
        if user_option == SINGLE_FOLDER_OPTION:
            # get the library directory path
            return_value.result.append (library_path)
        elif user_option == NESTED_FOLDER_OPTION:
            # get all subdirs
            child_dirs = get_all_nested_directories(library_path)
            # get all children
            return_value.result=child_dirs
            # make sure root dir is included too
            return_value.result.append(library_path)
        else:
            return_value.update_sep(False, "No valid directory option selected")
    except Exception as e:
        return_value.update_sep(
            False, "Failed to get directories: {}".format(e)
        )

    return return_value