#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2024, Jan Christel
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
from duHast.pyRevit.console_output import print_header, print_error
from duHast.Revit.Revisions.revisions import get_all_revisions
from duHast.Utilities.files_csv import write_report_data_as_csv

DEBUG = False

import datetime

def parse_date(date_str):
    # Possible formats
    formats = ["%d/%m/%y", "%d/%m/%Y", "%d.%m.%y", "%d.%m.%Y"]
    
    for fmt in formats:
        try:
            return datetime.datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    
    return None


def export_revs_entry(doc, output, forms):
    """
    Exports revisions to csv to be imported to doc manager.

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
        revisions = get_all_revisions(doc)

        # check what came back and respond accordingly
        if len(revisions) == 0:
            message = "No revisions found in the model."
            return_value.update_sep(
                False, message
            )
            print_error(message)
            return return_value
    
        if DEBUG:
            print_header("Revisions found in model:")
            for rev in revisions:
                print(
                    "Description: {}, Date: {}, Issued By: {}".format(
                        rev.description,
                        rev.revision_date,
                        rev.issued_by
                    )
                )
        

        print_header("Converting revisions to output format...")

        # convert revisions to an output doc manager expects when importing new revisions:
        # Id,Revision Date,Description
        # where Id is "NEW"
        # Revision Date is in format 2025-01-15 (yyyy-mm-dd)
        # Description is text
        output_revisions = []

        for rev in revisions:

            # get the revision date
            rev_date = parse_date(rev.revision_date)

            if rev_date is None:
                message = "Could not parse date '{}' for revision '{}'.".format(
                    rev.revision_date,
                    rev.description
                )
                return_value.update_sep(
                    False, message
                )
                # if date could not be parsed, skip this revision
                if DEBUG:
                    print_error(message)
                continue
            
            rev_date_string = rev_date.strftime("%d-%m-%Y")

            output_revisions.append(["NEW", rev_date_string, rev.description])
        
        # check if any revisions could be converted
        if len(output_revisions) == 0:
            message = "No revisions could be converted to output format."
            return_value.update_sep(
                False, message
            )
            print_error(message)
            return return_value


        print("\nRevisions converted to output format: {}".format(len(output_revisions)))

        #set up a header for the csv file
        header = ["Id", "Revision Date", "Description"]

        # get a file path to save the comparison result
        file_path = forms.save_file(file_ext='csv', title="Save revisions to csv file")

        if (file_path and len(file_path) > 0):
            write_result = write_report_data_as_csv(file_name=file_path, header= header,  data=output_revisions , quoting=csv.QUOTE_MINIMAL)
            if(write_result.status):
                print("Successfully wrote revisions to: {} ".format(file_path ))
            else:
                print("Failed to write revisions to: {} ".format(file_path ))
                print("Error: {}".format(write_result.message))
        else:
            print("No file path selected")
        
    except Exception as e:
        # handle any exceptions that occur during the export process
        message = "An error occurred while exporting revisions: {}".format(e)
        return_value.update_sep(
            False, message
        )
        print_error(message)


    print("\nFinished exporting revisions.")

    return return_value