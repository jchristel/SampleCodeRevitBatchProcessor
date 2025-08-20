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


from duHast.Revit.Views.Export.sheets_to_data import get_all_sheet_data
from duHast.Utilities.Objects.result import Result
from duHast.Utilities.files_json import write_json_to_file
from duHast.Utilities.Objects.timer import Timer
from duHast.Data.Objects.Collectors import data_sheet as ds
from duHast.Data.Utils.data_to_file import build_json_for_file


def sheets_export_entry(doc, output, forms):

    """
    Exports sheets from the current Revit document to a JSON file.

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

    try:

        # get sheet data
        sheet_data = get_all_sheet_data(doc)

        # convert into a dictionary
        dic = {
            ds.DataSheet.data_type:sheet_data
        }

        # add some more properties before writing to json
        json_formatted = build_json_for_file(dic, "{}".format(doc.Title))
        
        # save report to json file
        file_path = forms.save_file(file_ext='json', title="Save report to json file")

        if (file_path and len(file_path) > 0):
            # start timer
            t=Timer()
            t.start()

            # write data
            write_status = write_json_to_file(json_data=json_formatted,data_output_file_path= file_path)
            return_value.update(write_status)

            # log the result
            print("Finished writing report to csv file: {} with status: {}".format(file_path, write_status.status))
            print(t.stop())
                    
        else:
            return_value.append_message("No file path selected")
    
    except Exception as e:
        return_value.update_sep(
            False, "Failed to export sheet data with exception: {}".format(e)
        )
        print("Failed to export sheet data with exception: {}".format(e))

    print("Finished")

    return return_value