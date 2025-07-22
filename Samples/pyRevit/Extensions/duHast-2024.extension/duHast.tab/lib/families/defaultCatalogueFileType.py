
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
from duHast.Revit.Family.family_types import create_family_type, delete_family_type, get_all_family_type_names
from duHast.Revit.Family.family_parameter_utils import set_family_parameter_value

# parameters to reset
PARAMETERS_TO_RESET = []

# set up some options for the user to select
YES = "Yes"
NO_GET_ME_OUT_OF_HERE = "Oh No, Get me out of here!"

def get_user_options(forms):
    """
    Gets the user options for deleting all types in a family

    Options are: YES

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
        ops,  message="Do you really want to delete all types in this family?", config=configs
    )

    return ui_options

def default_catalogue_file_type_entry(doc, output, forms):
    """
    Creates a default catalogue file type, resets AusHFG parameters, removes all other tpes from the family

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param output: pyRevit output.
    :type output: pyRevit.output
    :param forms: pyRevit forms.
    :type forms: pyRevit.forms
    :return: Result object with status and message.
    :rtype: Result
    """
    
    # set up a status tracker
    return_value = Result()

    # get user options
    user_selection = get_user_options(forms)

    if user_selection == None or user_selection == NO_GET_ME_OUT_OF_HERE:
        return_value.update_sep(False, "User cancelled operation")
        print("User cancelled operation")
        return return_value

    # set default catalogue file type
    default_cat_file_type = "Refer To Catalog File"

    # create default catalogue type
    create_type_result = create_family_type(doc, default_cat_file_type)

    # check if dummy type was created
    if not create_type_result.status:
        return_value.update_sep(False, create_type_result.message)
        return return_value
    
    print("Default catalogue file type created: {}".format(create_type_result.message))
    
    # delete all other types
    type_names_result = get_all_family_type_names(doc)
    if not type_names_result.status:
        return_value.update_sep(False, type_names_result.message)
        return return_value
    
    print("All type names retrieved: {}".format(type_names_result.result))
    
    # remove the default type from the list
    type_names = type_names_result.result
    type_names.remove(default_cat_file_type)

    print("Type names to delete: {}".format(type_names))

    # delete all other types
    for type_name in type_names:
        delete_result = delete_family_type(doc, type_name)
        if not delete_result.status:
            return_value.update_sep(False, delete_result.message)
        else:
            print("Type {} deleted: {}".format(type_name, delete_result.message))
    
    # reset parameters
    # Get the FamilyManager
    family_manager = doc.FamilyManager

    for para_name in PARAMETERS_TO_RESET:
        # Get the parameter
        parameter = family_manager.get_Parameter(para_name)
        if parameter:
            set_result = set_family_parameter_value(doc, family_manager, parameter, default_cat_file_type)
            return_value.update(set_result)
        else: 
            return_value.append_message("Parameter not found: {}".format(para_name))
    


    print(return_value.message)
    print("Finished setting default catalogue file type")

    return return_value