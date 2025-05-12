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
from duHast.Revit.Views.sheets import get_all_sheets
from duHast.Revit.Exports.export_pdf import export_sheet_to_pdf
from duHast.Revit.Exports.export_dwg import export_sheet_to_dwg
from duHast.Revit.ExtensibleSchemas.extensible_schemas import does_schema_exist
from duHast.pyRevit.ui_element_selection import get_element_selection_from_user
from duHast.pyRevit.console_output import print_header, print_error
from duHast.pyRevit.directory_picker import get_process_directory

UI_SHEET_STRING = "*HSL_SHEET_SEQUENCE**Sheet Number*-*Sheet Name*[*Current Revision Date*,*Current Revision Description*]"
#SHEET_NAME_PDF = "*HSL_SHEET_SEQUENCE**Sheet Number*:-:*Sheet Name*?P?[?P?*Current Revision*?S?]?S?"
#SHEET_NAME_DWG = "*HSL_SHEET_SEQUENCE**Sheet Number*-DWG-*Sheet Name*[*Current Revision*]"

#DWG_EXPORT_OPTION_NAME = "HSL_PROJECT_INTERNAL"


from export.utility import get_sheet_parameter_data, get_naming_chunks, get_user_options, EXPORT_PDF_ONLY, EXPORT_PDF_AND_DWG
from export import settings
from export.settings_utils import get_name_settings_from_schema

def sheet_name_builder_ui(element, sheet_name_string):
    """
    Builds the sheet name using the provided string.

    :param element: The sheet element.
    :type element: Autodesk.Revit.DB.Element
    :param sheet_name_string: The string to build the sheet name.
    :type sheet_name_string: str
    :return: The built sheet name.
    :rtype: str
    """

    # get all parameters from the sheet and their values
    sheet_parameter_data = get_sheet_parameter_data(element)

    # replace the placeholders in the string with the actual values
    sheet_name_chunks= get_naming_chunks(sheet_name_string)

    sheet_name = []

    for chunk in sheet_name_chunks:
        # if the chunk contains a parameter name, replace it with the value
        if chunk in sheet_parameter_data.keys():
            sheet_name.append(sheet_parameter_data[chunk])
        else:
            # if the chunk does not contain a parameter name, add it as is
            sheet_name.append(chunk)

    # join the chunks with a space and return the sheet name
    sheet_name = "".join(sheet_name)

    # Build the sheet name using the provided string
    return sheet_name

def sheet_getter(doc):
    """
    Gets all sheets from the document.

    :param doc: The Revit document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of all sheets in the document.
    :rtype: list
    """

    sheets_filtered = []
    # Get all sheets in the document
    sheets = get_all_sheets(doc=doc)

    for s in sheets:
        if s.IsPlaceholder:
            continue

        # Get the sheet ID
        sheets_filtered.append(s)

    return sheets_filtered

def export_pdf_dwg_entry(doc, output, forms):
    """
    Exports sheets to pdf and dwg files.

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
        print_header("Exporting sheets to PDF and DWG files")
        
        # check if extensible schema exists
        if not does_schema_exist(settings.EXPORTER_ADD_IN_GUID):
            message = "Cant find any settings for this file. Please run the settings add-in first."
            return_value.update_sep(False, message)
            print_error(message)
            return return_value

        # place holder for the sheet name rule strings
        rename_settings = None

        # get the output directory from the schema
        settings_getter_result = get_name_settings_from_schema(doc=doc)
        if settings_getter_result.status is False:
            message = "Failed to get settings: {}".format(settings_getter_result.message)
            return_value.update_sep(False, message)
            print_error(message)
            return return_value
        else:
            # get the output directory from the schema
            rename_settings = settings_getter_result.result[0]
            

        # build action to get sheets from model
        def sheet_getter_in_line(doc):
            result_action =  sheet_getter(
                doc=doc
            )
            return result_action
    
        # build action for the sheet name to be displayed in UI
        def sheet_name_builder_ui_in_line(element):
            return sheet_name_builder_ui(
                element=element,
                sheet_name_string=UI_SHEET_STRING
            )

        # get the user to select which sheet to export
        selected_sheet_ids=get_element_selection_from_user(
            doc=doc,
            forms=forms,
            element_getter=sheet_getter_in_line,
            element_selection_description="Select sheets to export",
            ui_element_name_builder= sheet_name_builder_ui_in_line,
        )

        # check if the user selected any sheets
        if  selected_sheet_ids is None or len(selected_sheet_ids) == 0:
            return_value.update_sep(False, "No sheets to export where selected.")
            print("{}\nFinished.".format(return_value.message))
            return return_value


        # get the output directory
        process_dirs_result = get_process_directory(forms)
        if not process_dirs_result.status:
            print(process_dirs_result.message)
            return_value.update_sep(False, process_dirs_result.message)
            return return_value

        # get the directories to process
        output_directory = process_dirs_result.result[0]
        
        # check whether user wants to export pdf and dwg's
        user_option = get_user_options(forms)

        if user_option == EXPORT_PDF_AND_DWG:
            export_sheets_flag = True
        else:
            export_sheets_flag = False
        
        # get going
        sheet_counter = 0

        # convert sheet ids to view sheets
        sheets_to_export = []
        for sheet_id in selected_sheet_ids:
            # get the sheet element
            sheet_to_export= doc.GetElement(sheet_id)
            sheets_to_export.append(sheet_to_export)


        # set up a pyRevit progress bar
        with forms.ProgressBar(
            title="Exporting sheets: {value} of {max_value}", cancellable=True
        ) as pb:
            
            for sheet_id in selected_sheet_ids:
                # increase the progress bar
                sheet_counter += 1

                pb.update_progress(sheet_counter, max_value=len(selected_sheet_ids))

                # get the sheet element
                sheet = doc.GetElement(sheet_id)

                print_header ("Exporting sheet {}-{}...".format(sheet.SheetNumber, sheet.Name))

           
                # export the pdf
                export_sheet_pdf_result = export_sheet_to_pdf(
                    doc=doc,
                    view_sheet=sheet,
                    sheet_name_string=rename_settings.pdf_settings,    
                    output_directory= output_directory, 
                )

                # check if the export was successful
                if export_sheet_pdf_result.status == False:
                    print_error(export_sheet_pdf_result.message)
                else:
                    print(export_sheet_pdf_result.message)
                return_value.update(export_sheet_pdf_result)

                # check if sheet need to be exported to dwg
                if export_sheets_flag:
                    
                    # export dwg
                    export_sheet_dwg_result = export_sheet_to_dwg(
                        doc=doc,
                        view_sheet=sheet,
                        sheet_name_string=rename_settings.dwg_settings, 
                        output_directory= output_directory,
                        dwg_export_option_name=rename_settings.dwg_export_scheme_name,
                    )
                    # check if the export was successful
                    if export_sheet_dwg_result.status == False:
                        print_error(export_sheet_dwg_result.message)
                    else:
                        print(export_sheet_dwg_result.message)
                    return_value.update(export_sheet_dwg_result)
                  
                else:
                    message = "...Skipped exporting sheet {} to DWG.".format(sheet.Name)
                    return_value.update_sep(
                        True, message
                    )
                    print(message)
                    
                # check for cancel
                if pb.cancelled:
                    return_value.update_sep(False, "User cancelled.")
                    break

    except Exception as e:
        # handle any exceptions that occur during the export process
        message = "An error occurred while exporting sheets: {}".format(e)
        return_value.update_sep(
            False, "Failed to export sheets with exception: {}".format(e)
        )
        print(message)


    print("\nFinished exporting sheets to PDF and DWG files.")

    return return_value