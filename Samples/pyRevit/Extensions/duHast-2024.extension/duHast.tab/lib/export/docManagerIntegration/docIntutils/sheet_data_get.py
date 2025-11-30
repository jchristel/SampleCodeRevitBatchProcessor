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

from duHast.Utilities.Objects.result import Result
from duHast.Utilities.date_parse import parse_date
from duHast.Revit.Common.parameter_get_utils import get_built_in_parameter_value, get_parameter_value_by_name
from duHast.Revit.Views.sheets import get_all_sheets
from export.docManagerIntegration.Objects.DocManagerSheetData import DocManagerSheetData
from export.docManagerIntegration.Objects.DocManagerRevData import DocManagerRevData

from Autodesk.Revit.DB import BuiltInParameter


# the sheet number is built from these parts
# constant for sheet number
SHEET_NUMBER = "SheetNumber"
# the sheet number is built from these parts
SHEET_NUMBER_BUILDER = ["HSL_SHEET_SEQUENCE", SHEET_NUMBER]

# constant for sheet name
SHEET_NAME = "SheetName"
# the sheet name is built from these parts
SHEET_NAME_BUILDER = [SHEET_NAME]

def build_sheet_number(sheet):
    """
    Build sheet number from parts defined in SHEET_NUMBER_BUILDER

    :param sheet: Revit sheet object
    :return: built sheet number string
    """

    sheet_number_full = []
    for parameter_name in SHEET_NUMBER_BUILDER:
        if parameter_name == "SheetNumber":
            sheet_number = sheet.SheetNumber
            sheet_number_full.append(sheet_number)
        else:
            # custom parameter part
            sheet_number_part = get_parameter_value_by_name(sheet, parameter_name)
            if sheet_number_part:
                sheet_number_full.append(str(sheet_number_part))
                
    # build string from parts
    sheet_number = "".join(sheet_number_full)
    return sheet_number


def build_sheet_name(sheet):
    """
    Build sheet name from parts defined in SHEET_NAME_BUILDER

    :param sheet: Revit sheet object
    :return: sheet name string
    """

    sheet_name_full = []

    for parameter_name in SHEET_NAME_BUILDER:
        if parameter_name == "SheetName":
            sheet_name = get_built_in_parameter_value(sheet, BuiltInParameter.SHEET_NAME)
            sheet_name_full.append(str(sheet_name))
        else:
            # custom parameter part
            sheet_name_part = get_parameter_value_by_name(sheet, parameter_name)
            if sheet_name:
                sheet_name_full.append(str(sheet_name_part))
    
    sheet_name = "".join(sheet_name_full)
    
    return sheet_name



def match_sheet_revision_to_database_revision(revision, revision_database_data):
    """
    Match a sheet revision to revision data from database data.

    :param revision: Revit revision object
    :param revision_database_data: list of revision data from database
    :return: matching database id or None
    """

    data_base_rev = None

    for revision_database_entry in revision_database_data:

        # convert date strings to date objects for comparison
        date_in_revit_revision = parse_date(revision.RevisionDate)
        date_in_database_revision = parse_date(revision_database_entry.date)

        if revision_database_entry.description == revision.Description and date_in_revit_revision == date_in_database_revision:
            data_base_rev = revision_database_entry
            break

    return data_base_rev


def get_sheet_data(doc, revision_database_data):
    return_value = Result()
    
    try:
        
        # get all sheets in the document
        sheets = get_all_sheets(doc)
        
        sheet_data = []
        for sheet in sheets:
            # build the sheet number from parts
            sheet_number = build_sheet_number(sheet)

            # get the sheet name
            sheet_name =  build_sheet_name(sheet)
            
            # set up doc manager sheet data object
            doc_manager_sheet = DocManagerSheetData(sheet_number, sheet_name)
            sheet_data.append(doc_manager_sheet)

            # get the sheet's revisions
            # get revisions already on sheet (this is important, since they need to be passed in again when adding a new revision!)
            # this call converts ids to a c# List<ElementId> : ids.ToList[ElementId]()
            revision_ids = sheet.GetAllRevisionIds()

            for rev_id in revision_ids:
                # get revision object from id
                revision = doc.GetElement(rev_id)
                if revision:

                    # get the matching revision data from the database data passed in
                    data_base_rev = match_sheet_revision_to_database_revision(revision, revision_database_data)
                        
                    if not data_base_rev:
                        # no matching revision found in database data
                        message = "No matching revision found in database data for revision with date: {} and description: {}".format(revision.RevisionDate, revision.Description)
                        return_value.update_sep(False, message)
                        continue

                    # add to sheet's revision on sheet list
                    doc_manager_sheet.add_revision(data_base_rev)
                    
            # set the current revision indicator
            current_revit_revision_id = sheet.GetCurrentRevision()

            if not current_revit_revision_id or current_revit_revision_id.IntegerValue == -1:
                # no current revision set
                continue

            current_revit_revision = doc.GetElement(current_revit_revision_id)
            current_database_revision = match_sheet_revision_to_database_revision(current_revit_revision, revision_database_data)

            if current_database_revision:
                # store the current revision info
                doc_manager_sheet.current_revision = current_database_revision
                current_revision_indicator = get_built_in_parameter_value(sheet, BuiltInParameter.SHEET_CURRENT_REVISION)
                doc_manager_sheet.current_revision_indicator = current_revision_indicator

            else:
                message = "No matching current revision found in database data for current revision with date: {} and description: {}".format(current_revit_revision.RevisionDate, current_revit_revision.Description)
                return_value.update_sep(False, message)


        return_value.update_sep(True, "Successfully retrieved sheet data from document.")
        return_value.result.append(sheet_data)
        return return_value
    except Exception as e:
        message = "Error getting sheet data from file. Error: {}".format(e)
        return_value.update_sep(False, message)
        return return_value