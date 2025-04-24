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
from duHast.pyRevit.console_output import print_error, print_header
from duHast.Revit.Common.delete import delete_by_element_ids

# set up some options for the user to select
YES = "Yes"
NO_GET_ME_OUT_OF_HERE = "Oh No, Get me out of here!"


def get_user_options(forms):
    """
    Gets the user options for saving the family output directory.

    Options are: YES or NO_GET_ME_OUT_OF_HERE

    :param forms: the forms object
    :type forms: Forms
    :return: the user options
    :rtype: dict
    """

    # ask user for single directory or directory by category
    # and if existing families are to be ignored
    ops = [YES,NO_GET_ME_OUT_OF_HERE]
    configs = {
        YES: {"background": "#FF0000"},
        NO_GET_ME_OUT_OF_HERE : {"background": "#00FF00"},
    }
    ui_options = forms.CommandSwitchWindow.show(
        ops,  message="Do you want to delete the original filled region ?", config=configs
    )

    return ui_options


def post_processing_filled_region(doc, forms, filled_region):
    """
    Check if the filled region the push it family is based on is meant to be deleted.

    :param doc: the Revit document
    :type doc: Document
    :param forms: the pyRevit forms object
    :type forms: Forms
    :param filled_region: The filled region to check to post process (delete?)
    :type filled_region: Autodesk.Revit.DB.FilledRegion

    :return: Result class instance.

        - `result.status` (bool): True if the families where created successfully, otherwise False.
        - `result.message` (str): Confirmation of successful creation.
        - `result.result` (list): File path to wall host family.

    On exception:

        - `result.status` (bool): False.
        - `result.message` (str): Generic exception message.
        - `result.result` (list): Empty.
    :rtype: :class:`.Result`

    """

    # set up a status tracker
    return_value = Result()

    try:
        # output a header to the console
        print_header("Get A Room - post processing filled region")

        user_selection = get_user_options(forms)

        # check if user selection is valid
        if user_selection == None or user_selection == NO_GET_ME_OUT_OF_HERE:
            return_value.append_message("User cancelled operation, no filled region deleted.")
            return return_value
    
        # delete the filled region
        delete_result = delete_by_element_ids(
            doc=doc,
            ids=[filled_region.Id],
            transaction_name = "delete filled region {}".format(filled_region.Id.IntegerValue),
            element_name="Filled Region",
        )

        return_value.update(delete_result)

    except Exception as e:
        message = "Failed to post process filled region: {}".format(e)
        return_value.update_sep(False, message)
    
    return return_value