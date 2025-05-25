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
from duHast.pyRevit.console_output import print_header, print_error
from duHast.Revit.ExtensibleSchemas.extensible_schemas import does_schema_exist
from duHast.pyRevit.net_dll_loader import load_net_dll_path


from export.utility import get_sheet_parameter_data
from export import settings
from export.settings_utils import get_name_settings_from_schema
from export.ui_data_get import get_ui_data


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

        # load .net interface dlls
        set_dll_path_result = load_net_dll_path([ "PDFDWGExporterSelectionUI.dll"]) #"Utils.23.0.0.3.dll",

        # check if the dlls were loaded successfully
        if not set_dll_path_result.status:
            print_error(set_dll_path_result.message)
            return_value.update_sep(False, set_dll_path_result.message)
            return return_value
        
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
            # get the rename settings from the schema
            rename_settings = settings_getter_result.result[0]
            

        ui_data = get_ui_data(doc)
        print("UI data for sheets: {}".format(ui_data))

        # import the UI class from the PDFDWGExporterUI namespace
        from duHastNet.UI.PDFDWGExporterSelectionUI import Main
       
        # create an instance of the Main class
        main = Main(sheetsInModel=ui_data[0], printSetsInModel=ui_data[1])
        # show the output window
        export_settings = main.Execute()


        # # get going
        # sheet_counter = 0

        # # convert sheet ids to view sheets
        # sheets_to_export = []
        # for sheet_id in selected_sheet_ids:
        #     # get the sheet element
        #     sheet_to_export= doc.GetElement(sheet_id)
        #     sheets_to_export.append(sheet_to_export)


        # # set up a pyRevit progress bar
        # with forms.ProgressBar(
        #     title="Exporting sheets: {value} of {max_value}", cancellable=True
        # ) as pb:
            
        #     for sheet_id in selected_sheet_ids:
        #         # increase the progress bar
        #         sheet_counter += 1

        #         pb.update_progress(sheet_counter, max_value=len(selected_sheet_ids))

        #         # get the sheet element
        #         sheet = doc.GetElement(sheet_id)

        #         print_header ("Exporting sheet {}-{}...".format(sheet.SheetNumber, sheet.Name))

           
        #         # export the pdf
        #         export_sheet_pdf_result = export_sheet_to_pdf(
        #             doc=doc,
        #             view_sheet=sheet,
        #             sheet_name_string=rename_settings.pdf_settings,    
        #             output_directory= output_directory, 
        #         )

        #         # check if the export was successful
        #         if export_sheet_pdf_result.status == False:
        #             print_error(export_sheet_pdf_result.message)
        #         else:
        #             print(export_sheet_pdf_result.message)
        #         return_value.update(export_sheet_pdf_result)

        #         # check if sheet need to be exported to dwg
        #         if export_sheets_flag:
                    
        #             # export dwg
        #             export_sheet_dwg_result = export_sheet_to_dwg(
        #                 doc=doc,
        #                 view_sheet=sheet,
        #                 sheet_name_string=rename_settings.dwg_settings, 
        #                 output_directory= output_directory,
        #                 dwg_export_option_name=rename_settings.dwg_export_scheme_name,
        #             )
        #             # check if the export was successful
        #             if export_sheet_dwg_result.status == False:
        #                 print_error(export_sheet_dwg_result.message)
        #             else:
        #                 print(export_sheet_dwg_result.message)
        #             return_value.update(export_sheet_dwg_result)
                  
        #         else:
        #             message = "...Skipped exporting sheet {} to DWG.".format(sheet.Name)
        #             return_value.update_sep(
        #                 True, message
        #             )
        #             print(message)
                    
        #         # check for cancel
        #         if pb.cancelled:
        #             return_value.update_sep(False, "User cancelled.")
        #             break

    except Exception as e:
        # handle any exceptions that occur during the export process
        message = "An error occurred while exporting sheets: {}".format(e)
        return_value.update_sep(
            False, "Failed to export sheets with exception: {}".format(e)
        )
        print(message)


    print("\nFinished exporting sheets to PDF and DWG files.")

    return return_value