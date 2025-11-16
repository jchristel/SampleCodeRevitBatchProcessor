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
from duHast.Revit.Family.family_types_get_data_from_xml import (
    get_type_data_via_XML_from_family_file,
)
from duHast.Utilities.files_io import get_file_name_without_ext

from families.util.family_on_disc_selection import get_families, get_user_selection
from duHast.Revit.Family.family_types_catalogue import export_catalogue_file


def report_data(fam_type_data, output):
    """
    Prints family type data to the pyRevit output as a table.

    :param fam_type_data: The family type data.
    :type fam_type_data: list[FamilyTypeData]
    :param output: pyRevit output
    :type output: pyRevit output module
    """

    rows_data = []
    for fam_type in fam_type_data:
        for p in fam_type.parameters:
            row = [
                fam_type.root_name_path,
                fam_type.root_category_path,
                fam_type.family_file_path,
                fam_type.family_type_name,
                p.name,
                p.value,
                p.type,
                p.units,
                p.type_of_parameter,
            ]
            rows_data.append(row)

    columns = [
        "Family Name",
        "Family Category",
        "family File Path",
        "Type Name",
        "Parameter Name",
        "Parameter Value",
        "Parameter Type",
        "Parameter Units",
        "Parameter Type Of",
    ]

    format_by_columns = [""] * len(columns)

    output.print_table(
        table_data=rows_data,
        title="Family Catalogue Data",
        columns=columns,
        formats=format_by_columns,
    )


def export_catalogue_file_entry(doc, output, forms):
    """
    Exports family type data to an xml file, reads that data back into custom objects and prints it to the pyRevit output as a table.

    :param doc: The current Revit document.
    :type doc: Autodesk.Revit.DB.Document
    :param output: pyRevit output
    :type output: pyRevit output module
    :param forms: pyRevit forms
    :type forms: pyRevit forms module

    :return:
        Result class instance.

        - result.status (bool) True if files where processed without an exception, otherwise False.
        - result.message contains log messages.
        - result.result will be an empty list.

        On exception:

        - result.status (bool) will be False.
        - result.message will contain exception message.
    :rtype: :class:`.Result`
    """

    # set up a status tracker
    return_value = Result()

    # get user to select a directory
    family_out_folder_path = None
    family_out_folder_path = forms.pick_folder(
        "Select the family data export directory"
    )
    if family_out_folder_path is None:
        message = "No folder selected. Exiting."
        print(message)
        return_value.update_sep(False, message=message)
        return return_value

    else:
        print("Saving family type data to directory: {}".format(family_out_folder_path))

    # get all families in that directory and discard any family that occurs more than once
    families_to_process = get_families(family_out_folder_path)

    # show user a list of families to load
    families_to_process_filtered = get_user_selection(forms, families_to_process)
    if families_to_process_filtered is None:
        message = "No families selected to process. Exiting."
        print(message)
        return_value.update_sep(False, message=message)
        return return_value

    counter = 0
    max_counter = len(families_to_process_filtered)
    # set up a pyRevit progress bar
    with forms.ProgressBar(
        title="Exporting family type data families: {value} of {max_value}",
        cancellable=True,
    ) as pb:
        # set up data container
        all_data = []
        # loop over selection and get data
        for family_path in families_to_process_filtered:
            # update progress
            pb.update_progress(counter, max_counter)
            # get the family name
            family_name = get_file_name_without_ext(family_path)
            # extract the data
            data_result = get_type_data_via_XML_from_family_file(
                application=doc.Application,
                family_name=family_name,
                family_path=family_path,
            )
            # logging
            return_value.update_sep(data_result.status, data_result.message)
            # some user feedback
            print(
                "data extraction result for: {} {}".format(
                    family_name, data_result.message
                )
            )
            if data_result.status:
                all_data = all_data + data_result.result[0]

            # check for cancel
            if pb.cancelled:
                return_value.update_sep(False, "User cancelled.")
                # get out of loop
                break

            counter += 1

    # print all_data
    report_data(all_data, output)

    return return_value
