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

from duHast.Utilities.files_csv import  write_report_data_as_csv
from colour_schemes.colour_fill_schemes import get_all_colour_schemes
from colour_schemes.colour_fill_selection import user_select_colour_scheme
from colour_schemes.colour_fill_scheme_report import get_report_data_of_colour_fill_scheme


def save_report( header, data):

    return_value = Result()
    # get file path from user
    file_name = None
    sf_dlg = Forms.SaveFileDialog()  # (file_ext="json", title="Save template data")
    sf_dlg.Filter = "Text files (*.csv)|*.csv|All files (*.*)|*.*"
    if sf_dlg.ShowDialog() == Forms.DialogResult.OK:
        file_name = sf_dlg.FileName

    if file_name is None:
        return_value.update_sep(
            False, "No file name for data file selected. Exiting."
        )
        return return_value

    # write data to file
    try:
        write_result = write_report_data_as_csv(
            file_name,
            header,
            data,
            quoting=csv.QUOTE_MINIMAL
        )
    
        return_value.update(write_result)

        return return_value
    
    except Exception as e:
        return_value.update_sep(False, "Error writing file: {}".format(e))
        return return_value

def export_colour_scheme_entry(doc, output, forms):

    """
    Exports the colour scheme to a file.

    :param doc: The Revit document.
    :param output: The output object.
    :param forms: The forms object.
    """
    
    return_value = Result()

    try:

        #  get the user to select the scheme
        scheme_selection_result = user_select_colour_scheme(doc, forms)

        # check if anything was selected
        if not scheme_selection_result.status:
            return scheme_selection_result
        
        # convert the result to a list to be exported
        colour_fill_scheme = scheme_selection_result.result[0]

        # get the report data
        report_data = get_report_data_of_colour_fill_scheme(doc=doc, colour_fill_scheme=colour_fill_scheme)

        # get the header row
        header = report_data[0].get_report_headers()

        report_data_list = []
        for d in report_data:
            report_data_list.append(d.get_report_data())

        # write data to file
        save_result = save_report(header, report_data_list)
        if( not save_result.status):
            print("Error writing file: {}".format(save_result.message))
            return_value.update(save_result.message)
            return return_value

        
        return_value.append_message(save_result.message)

        print("Finished.")
        return return_value

    except Exception as e:
        return_value.update_sep(False, "Error exporting colour scheme: {}".format(e))

        print(e)
        return return_value
    
