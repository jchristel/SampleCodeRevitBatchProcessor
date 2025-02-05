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
from duHast.Revit.Family.Reporting.report_fam_types_differences_from_XML import (
    compare_family_files_in_project_against_library,
)
from duHast.Revit.Family.Reporting.families_report_header import (
    LIBRARY_VS_PROJECT_FAMILIES_COMPARISON_HEADER,
)
from duHast.pyRevit.Objects.ProgressPyRevit import ProgressPyRevit
from duHast.Utilities.files_csv import write_report_data_as_csv


from families.util.print_table import print_result_table

# directories to process (add more directories as needed)
# these directories will be searched for xml files
PROCESS_DIRECTORIES = [
    r"\\path\location\one",
    r"\\path\location\two",
    r"\\path\location\three",
]

# path to the ignore list file
# this file will be used to ignore certain families in the comparison
# the file should be a csv file with a two columns:
# family name
# family category
IGNORE_FAMILIES_LIST_PATH = r"\\location\to\your\ignore\file\type_ignore_file_test.csv"


def compare_loaded_families_vs_library_entry(doc, output, forms):
    """
    Reports on loaded families in a project file vs families in a library location.

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
        # set up a pyRevit progress bar
        with forms.ProgressBar(
            title="Comparing: {value} of {max_value}",
            cancellable=True,
        ) as pb:

            # set up a call back for pyRevit progressbar
            progress_callback = ProgressPyRevit(form=pb)

            print("Comparing families against library:")
            compare_result = compare_family_files_in_project_against_library(
                doc=doc,
                process_directories=PROCESS_DIRECTORIES,
                ignore_list_path=IGNORE_FAMILIES_LIST_PATH,
                progress_callback=progress_callback,
            )

            # update return value with comparison result
            return_value.update(compare_result)

        # sort the comparison result by family name
        sorted_result = sorted(compare_result.result)
        # print comparison result to pyRevit output
        print_result_table(
            output=output,
            data=sorted_result,
            header=LIBRARY_VS_PROJECT_FAMILIES_COMPARISON_HEADER,
            table_title="comparison result",
        )

        # get user to pick a file path to save the comparison result
        file_path = forms.save_file(
            file_ext="csv", title="Save comparison result to csv file"
        )

        if file_path and len(file_path) > 0:
            # attempt to write the comparison result to a csv file
            write_result = write_report_data_as_csv(
                file_name=file_path,
                header=LIBRARY_VS_PROJECT_FAMILIES_COMPARISON_HEADER,
                data=sorted_result,
                quoting=csv.QUOTE_MINIMAL,
            )

            # update return value with write result
            if write_result.status:
                return_value.append_message(
                    "Succefully wrote comparison report to: {} ".format(
                        write_result.status
                    )
                )
            else:
                return_value.update_sep(
                    False,
                    "Failed to write comparison report to: {} ".format(
                        write_result.status
                    ),
                )

        else:
            return_value.append_message("No file path selected")
    except Exception as e:
        return_value.update_sep(
            False, "Failed to compare families with exception: {}".format(e)
        )

    print("\n{}".format(return_value.message))
    print("Finished")

    return return_value
