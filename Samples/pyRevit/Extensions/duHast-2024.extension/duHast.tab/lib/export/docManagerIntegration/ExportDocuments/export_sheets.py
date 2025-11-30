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

from export.docManagerIntegration.ExportDocuments.export_user_ui import get_revision_file_path
from export.docManagerIntegration.docIntutils.revision_data_get import get_revision_data
from export.docManagerIntegration.docIntutils.sheet_data_get import get_sheet_data

DEBUG = True


def export_sheets_entry(doc, output, forms):
    """
    Exports sheet data to csv for import to doc manager.

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
        
        # get user to select revision input file
        revision_file_path = get_revision_file_path()
        
        if revision_file_path is None or revision_file_path == "":
            message = "No revision file selected. Aborting export."
            return_value.update_sep(
                False, message
            )
            print_error(message)
            return return_value
        
        if DEBUG:
            print_header("Revision File Selection")
            print("Using revision file path: {}".format(revision_file_path))
        
        
        # read the revision data from csv
        rev_data_result = get_revision_data(revision_file_path)
        if not rev_data_result.status:
            message = "Failed to get revision data from file: {}\n{}".format(revision_file_path, rev_data_result.message)
            return_value.update_sep(False, message)
            print_error(message)
            return return_value
        
        # extract revision data from result
        revision_data = rev_data_result.result[0]
        
        if DEBUG:
            print_header("Revision Data Retrieved")
            print("Retrieved {} revision records from file.".format(len(revision_data)))
            for rev in revision_data:
                print("Rev date: {}, description: {}, db id: {}".format(rev.date, rev.description, rev.database_id))
                
        # get all sheets and their revision info
        sheet_result = get_sheet_data(doc, revision_data)
        if not sheet_result.status:
            message = "Failed to get sheet data from document.\n{}".format(sheet_result.message)
            return_value.update_sep(False, message)
            print_error(message)
            return return_value
        
        # extract sheet data from result
        sheet_data = sheet_result.result[0]
        if DEBUG:
            print_header("Sheet Data Retrieved")
            print("Retrieved {} sheets from document.".format(len(sheet_data)))
            for sheet in sheet_data:
                print("Sheet number: {}, name: {}, current revision: {}".format(sheet.number, sheet.name, sheet.current_revision_indicator))
                # write out revision info
                for rev in sheet.revisions:
                    print("...Rev date: {}, description: {}, db id: {}".format(rev.date, rev.description, rev.database_id))
        
        # build export data
        export_data = []
        for sheet in sheet_data:
            export_string = sheet.get_doc_manager_export_string(
                custom_fields=[], revision_data=revision_data
            )
            export_data.append(export_string)
        
        if DEBUG:
            print_header("Export Data Built")
            print("Built export data for {} sheets.".format(len(export_data)))
            for data in export_data:
                print("Export data: {}".format(data))



    except Exception as e:
        # handle any exceptions that occur during the export process
        message = "An error occurred while exporting sheets: {}".format(e)
        return_value.update_sep(
            False, message
        )
        print_error(message)


    print("\nFinished exporting sheets.")

    return return_value