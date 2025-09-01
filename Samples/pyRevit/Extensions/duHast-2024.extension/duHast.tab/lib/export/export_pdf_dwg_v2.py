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
from duHast.pyRevit.console_output import print_header, print_error
from duHast.Revit.ExtensibleSchemas.extensible_schemas import does_schema_exist
from duHast.pyRevit.net_dll_loader import load_net_dll_path
from duHast.Revit.NetSupport.dll_names import PDF_AND_DWG_EXPORTER_SELECTION_UI

from export.utility import get_sheet_parameter_names
from export import settings
from export.settings_utils import get_name_settings_from_schema
from export.ui_data_get import get_ui_data
from export.print_sets_update import update_print_sets_from_ui
from export.export_sheets import export_sheets

from Autodesk.Revit.DB import ElementId

DEBUG = False

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
        # load .net interface dlls
        set_dll_path_result = load_net_dll_path([PDF_AND_DWG_EXPORTER_SELECTION_UI]) #"Utils.23.0.0.3.dll",

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
            message = "It looks like there are export settings stored in this file. Run set up first.\n... {}".format(settings_getter_result.message)
            return_value.update_sep(False, message)
            print_error(message)
            return return_value
        else:
            # get the rename settings from the schema
            rename_settings = settings_getter_result.result[0]
            if DEBUG:
                print_header("Got rename settings")
                print("...PDF settings: [{}]".format(rename_settings.pdf_settings))
                print("...DWG settings: [{}]".format(rename_settings.dwg_settings))
                print("...DWG export scheme name: [{}]".format(rename_settings.dwg_export_scheme_name))

        # get the parameters assigned to sheets
        parameter_names = get_sheet_parameter_names(doc)
        if DEBUG:
            print_header("Got parameter names")
            print ("\n...".join(parameter_names))


        # get the data required for the UI
        ui_data = get_ui_data(doc)
        
        # import the UI class from the PDFDWGExporterUI namespace
        from duHastNet.UI.PDFDWGExporterSelectionUI import Main
         
        # create an instance of the Main class
        main = Main(
            sheetsInModel=ui_data[0], 
            printSetsInModel=ui_data[1],
            schedulesInModel = ui_data[2],
            currentPDFExportString = rename_settings.pdf_settings,
            currentDWGExportString = rename_settings.dwg_settings,
            parameterNames=parameter_names,
        )

        # show the output window
        selection_settings = main.Execute()
        if DEBUG:
            print("...export settings: \n...{}".format(selection_settings))
        

        # check for updated print sets first
        # update print sets in model
        update_print_set_result = update_print_sets_from_ui(doc, main.PrintSetsUpdated)
        return_value.update(update_print_set_result)

        if DEBUG:
            print("...update print sets result: {}".format(update_print_set_result.status))


        print_header("Exporting sheets to PDF and DWG files")
        
        # check if any sheets were selected
        if not selection_settings.SheetIdsToExport or selection_settings.SheetIdsToExport.Count == 0:
            message = "No sheets selected for export."
            return_value.update_sep(False, message)
            print_error(message)
            return return_value
        
        if DEBUG:
            print("...sheets to export: {}".format(selection_settings.SheetIdsToExport.Count))
        
        # check if the output directory is set
        if not selection_settings.ExportDirectoryPath or selection_settings.ExportDirectoryPath == "":
            message = "No output directory set. Please set an output directory."
            return_value.update_sep(False, message)
            print_error(message)
            return return_value
        
        if DEBUG:
            print("...output directory: {}".format(selection_settings.ExportDirectoryPath))
            
        # check the export mode
        if not selection_settings.ExportModus  or selection_settings.ExportModus  == "":
            message = "No export mode set. Please set an export mode."
            return_value.update_sep(False, message)
            print_error(message)
            return return_value
        
        if DEBUG:
            print("...export mode: {}".format(selection_settings.ExportModus ))
        

        # call the export function
        export_result = export_sheets (doc, rename_settings, selection_settings, forms)
        return_value.update(export_result)

        if DEBUG:
            print("...export result: {}".format(export_result.status))

    except Exception as e:
        # handle any exceptions that occur during the export process
        message = "An error occurred while exporting sheets: {}".format(e)
        return_value.update_sep(
            False, message
        )
        print_error(message)


    print("\nFinished exporting sheets to PDF and DWG files.")

    return return_value