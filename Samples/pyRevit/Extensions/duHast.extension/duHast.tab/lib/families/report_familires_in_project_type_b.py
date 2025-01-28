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
from duHast.Revit.Family.Reporting.report_fam_types_from_project_via_xml import (
    get_all_family_type_data_from_project_file,
)
from duHast.Revit.Family.Reporting.families_report_header import LIBRARY_FAMILIES_HEADER
from duHast.pyRevit.Objects.ProgressPyRevit import ProgressPyRevit
from duHast.pyRevit.console_output import print_header
from duHast.Utilities.files_csv import write_report_data_as_csv

from families.util.print_table import print_result_table


def report_families_in_project_entry(doc, output, forms):
    """
    Report all families in project to csv file. This function is the entry point for the pyRevit command.

    Reports:

    - Family Name
    - Family Category
    - Family Type Name
    - parameter properties
    - parameter value

    :param doc: Revit Document
    :type doc: Document
    :param output: pyRevit output
    :type output: Output
    :param forms: pyRevit forms
    :type forms: Forms

    :return: Result
    """

    # set up a status tracker
    return_value = Result()
    family_data = []

    try:

        # set up a pyRevit progress bar
        with forms.ProgressBar(
            title="Reading: {value} of {max_value}",
            cancellable=True,
        ) as pb:

            # set up a call back for pyRevit progressbar
            progress_callback = ProgressPyRevit(form=pb)

            print_header("Reporting families in project:")
            report_result = get_all_family_type_data_from_project_file(
                doc=doc, ignore_list_path=None, progress_callback=progress_callback
            )

            print("Finished reading families from project")

            # update return value with comparison result
            return_value.update(report_result)
            if report_result.status == False:
                print(
                    "Failed to get family data from project with exception: {}".format(
                        report_result.message
                    )
                )
                return return_value

            # store report result
            family_data = report_result.result

        print(
            "Finished reading families in project with status: {}".format(
                report_result.status
            )
        )

        # print comparison result to pyRevit output
        print_result_table(
            output=output,
            data=family_data,
            header=LIBRARY_FAMILIES_HEADER,
            table_title="fams",
        )

        print_header("Writing report to csv file")

        # pop a warning to user that this might take a while if rows exceed 10000
        if len(family_data) > 10000:
            print("This might take a while...rows to save: {}".format(len(family_data)))

        # save report to csv file
        file_path = forms.save_file(file_ext="csv", title="Save report to csv file")

        if file_path and len(file_path) > 0:
            write_result = write_report_data_as_csv(
                file_name=file_path,
                header=LIBRARY_FAMILIES_HEADER,
                data=report_result.result,
                quoting=csv.QUOTE_MINIMAL,
            )
            if write_result.status:
                return_value.append_message(
                    "Successfully wrote families report to: {} ".format(file_path)
                )
            else:
                return_value.update_sep(
                    False,
                    "Failed to write families report to: {} ".format(
                        write_result.status
                    ),
                )
            print(
                "Finished writing report to csv file: {} with status: {}".format(
                    file_path, write_result.status
                )
            )

        else:
            return_value.append_message("No file path selected")

    except Exception as e:
        return_value.update_sep(
            False, "Failed to report families with exception: {}".format(e)
        )

    print("Finished")

    return return_value
