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


from duHast.Revit.Exports.export_pdf import export_sheet_to_pdf
from duHast.Revit.Exports.export_dwg import export_sheet_to_dwg

from Autodesk.Revit.DB import ElementId

def export_sheets (doc, rename_settings, selection_settings, forms):

    # set up a status tracker
    return_value = Result()

    try:
        
        # check what we are exporting in terms of format
        from duHastNet.UI.PDFDWGExporterSelectionUI.Models import Constants    
        export_pdf = True if selection_settings.ExportModus  == Constants.ExportModusPDF or selection_settings.ExportModus  == Constants.ExportModusPDFandDWG  else False
        export_dwg = True if selection_settings.ExportModus  == Constants.ExportModusDWG or selection_settings.ExportModus  == Constants.ExportModusPDFandDWG  else False

        # get going
        sheet_counter = 0

        # convert sheet ids to view sheets
        sheets_to_export = []
        for sheet_id in selection_settings.SheetIdsToExport:
            # get the sheet element
            sheet_to_export= doc.GetElement(ElementId(sheet_id))
            sheets_to_export.append(sheet_to_export)

        # set up a pyRevit progress bar
        with forms.ProgressBar(
            title="Exporting sheets: {value} of {max_value}", cancellable=True
        ) as pb:
            
            for sheet in sheets_to_export:
                # increase the progress bar
                sheet_counter += 1

                pb.update_progress(sheet_counter, max_value=len(sheets_to_export))

                print_header ("Exporting sheet {}-{}...".format(sheet.SheetNumber, sheet.Name))

                if export_pdf:
                    # export the pdf
                    export_sheet_pdf_result = export_sheet_to_pdf(
                        doc=doc,
                        view_sheet=sheet,
                        sheet_name_string=rename_settings.pdf_settings,    
                        output_directory= selection_settings.ExportDirectoryPath, 
                    )

                    # check if the export was successful
                    if export_sheet_pdf_result.status == False:
                        print_error(export_sheet_pdf_result.message)
                    else:
                        print(export_sheet_pdf_result.message)
                    return_value.update(export_sheet_pdf_result)
                else:
                    message = "...Skipped exporting sheet {} to PDF.".format(sheet.Name)
                    return_value.update_sep(
                        True, message
                    )
                    print(message)

                # check if sheet need to be exported to dwg
                if export_dwg:
                    
                    # export dwg
                    export_sheet_dwg_result = export_sheet_to_dwg(
                        doc=doc,
                        view_sheet=sheet,
                        sheet_name_string=rename_settings.dwg_settings, 
                        output_directory= selection_settings.ExportDirectoryPath,
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
            False, message
        )
        print_error(message)


    print("\nFinished exporting sheets to PDF and DWG files.")

    return return_value