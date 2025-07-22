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


import csv

from pyrevit.framework import Forms

from duHast.Utilities.Objects.result import Result
from duHast.pyRevit.console_output import print_header, print_error
from duHast.Revit.ColourFillSchemes.colour_fill_schemes_updates import update_by_values, update_existing_and_add_new_values

from colour_schemes.colour_fill_selection import  import_colour_fill_scheme_from_file,  select_colour_scheme_to_import,  user_select_colour_scheme, get_user_options, ADD_AND_UPDATE, UPDATE


def import_colour_scheme_entry(doc, output, forms):
    """
    Imports the colour scheme from a file.

    :param doc: The Revit document.
    :param output: The output object.
    :param forms: The forms object.
    """
    
    return_value = Result()

    try:
        # get file selection from user and file content
        data_import_result = import_colour_fill_scheme_from_file(forms=forms)
        
        if data_import_result.status == False:
            print_error(data_import_result.message)
            return data_import_result

        # get user to select which colour fill scheme to import
        import_selection_result = select_colour_scheme_to_import (forms, data_import_result.result[0])
        if import_selection_result.status == False:
            print_error(import_selection_result.message)
            return import_selection_result

        # get the colour fill scheme data
        colour_fill_settings = import_selection_result.result

        # get the user to select which colour fill scheme to update
        scheme_selection_result = user_select_colour_scheme(doc, forms, "Select colour fill schemes to modify")
        # check if anything was selected
        if not scheme_selection_result.status:
            print_error("No colour fill scheme to modify selected.")
            return scheme_selection_result

        # get the user to decide as to whether to update matching data or import new and and update existing data
        user_selection = get_user_options(forms)

        if user_selection == UPDATE:
            # update the colour fill scheme colour values only
            update_result = update_by_values(doc, scheme_selection_result.result[0], colour_fill_settings)
            print(update_result)
        elif user_selection == ADD_AND_UPDATE:
            update_result = update_existing_and_add_new_values(doc, scheme_selection_result.result[0], colour_fill_settings)
            print(update_result)
        else:
            print_error("No valid user selection made. Exiting.")
            return_value.update_sep(False, "No valid user selection on update mode made. Exiting.")
            return return_value


        print("Finished.")
        return return_value

    except Exception as e:
        return_value.update_sep(False, "Error importing colour scheme: {}".format(e))

        print_error(e)
        return return_value