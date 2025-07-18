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

from duHast.Utilities.Objects.result import Result
from duHast.pyRevit.Objects.ProgressPyRevit import ProgressPyRevit
from duHast.Revit.Family.Reporting.report_differences_in_reports import compare_family_reports_outer_join
from duHast.Utilities.files_io import get_file_name_without_ext
from duHast.Utilities.files_csv import write_report_data_as_csv

from families.util.print_table import print_result_table

from duHast.pyRevit.directory_picker import get_process_directories
from duHast.Utilities.files_get import get_files_single_directory


def convert_data_to_csv(data):
    """
    Convert data to csv format.

    :param data: Data to convert.
    :type data: dict
    
    :return: Data in csv format.
    :rtype: list
    """

    csv_data = []
    for key, value in data.items():
        row = []
        for entry in key:
            row.append(entry)
        for entry in value:
            row.append(entry)
        csv_data.append(row)
    
    # sort by family and type name
    sorted_rows = sorted(csv_data, key=lambda x: (x[0],  x[2]))

    return sorted_rows

def get_library_reports(forms):
    """
    Get path of library reports to compare.

    :param forms: pyRevit forms module.
    :type forms: pyRevit forms module

    :return: List of library report file paths.
    :rtype: list
    """

    library_files = []
    # get the directories to process
    directories_result = get_process_directories(forms)

    if not directories_result.status:
        return library_files


    files = []
    # get all csv files in the directories
    for directory in directories_result.result:
        files = get_files_single_directory(folder_path=directory, file_prefix="", file_suffix="", file_extension=".csv")

        if files and len(files) > 0:
            library_files.extend(files)

    # display a list to the user where they can select the files to process
    selected_files = forms.SelectFromList.show(sorted(files), button_name='{}'.format("Select library reports"), multiselect= True)

    if selected_files and len(selected_files) > 0:
        return selected_files
    else:
        return []



def compare_library_reports_entry(doc, output, forms):
    """
    Compares reports from different libraries.
    Reports need to be created by report_families_in_library function.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param output: pyRevit output
    :type output: pyRevit output module
    :param forms: pyRevit forms
    :type forms: pyRevit forms module

    :return:
        Result class instance.

        - result.status (bool) True if families where reported without an exception, otherwise False.
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

        # get user selected library reports
        print("Select library reports to compare:")

        process_reports = get_library_reports(forms)
        if len(process_reports) == 0:
            message = "No valid library reports selected"
            print(message)
            return_value.update_sep(False, message)
            return return_value
            
        #set up a pyRevit progress bar
        with forms.ProgressBar(
            title="Comparing: {value} of {max_value}",
            cancellable=True,
        ) as pb:
            
            print("Comparing libraries:")
            # set up a call back for pyRevit progressbar
            progress_callback = ProgressPyRevit(form=pb)
            
            compare_result = compare_family_reports_outer_join(process_reports)
            #print(compare_result.result)
            
            report_names =[get_file_name_without_ext(file) for file in process_reports ] 
            header = ["Family Name", "Category", "Family Type", "Parameter Name"] + report_names

            data_converted = convert_data_to_csv(compare_result.result)
            print_result_table (output=output, data=data_converted, header=header,table_title="comparison result")

            # get a file path to save the comparison result
            file_path = forms.save_file(file_ext='csv', title="Save comparison result to csv file")

            if (file_path and len(file_path) > 0):
                write_result = write_report_data_as_csv(file_name=file_path, header= header,  data=data_converted , quoting=csv.QUOTE_MINIMAL)
                if(write_result.status):
                    print("Succefully wrote comparison report to: {} ".format(file_path ))
                else:
                    print("Failed to write comparison report to: {} ".format(file_path ))
                    print("Error: {}".format(write_result.message))
            else:
                print("No file path selected")

    except Exception as e:
        return_value.update_sep(
            False, "Failed to compare reports with exception: {}".format(e)
        )

    print("\n{}".format(return_value.message))
    print("Finished")

    return return_value
