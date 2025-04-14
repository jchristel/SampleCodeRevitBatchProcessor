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
import os

from duHast.Utilities.files_io import rename_file
from duHast.Utilities.files_get import get_files_single_directory

from System.Collections.Generic import List

from Autodesk.Revit.DB import ACADVersion, BaseExportOptions, DWGExportOptions,ElementId

from export.utility import get_sheet_parameter_data, get_naming_chunks

def set_dwg_export_option():

    # Create a new instance of DWGExportOptions
    dwg_export_options = DWGExportOptions()

    dwg_export_options.FileVersion = ACADVersion.R2010
    dwg_export_options.HideReferencePlane = True
    dwg_export_options.HideScopeBoxe = True
    dwg_export_options.HideUnreferenceViewTags	= True
    dwg_export_options.MergedViews = True

    return dwg_export_options


def get_dwg_export_option_by_name(doc, dwg_export_option_name):
    """
    Retrieves the DWG export option by name.

    :param dwg_export_option_name: The name of the DWG export option.
    :type dwg_export_option_name: str
    :return: The DWG export option.
    :rtype: Autodesk.Revit.DB.DWGExportOptions
    """
    
    setup_names = BaseExportOptions.GetPredefinedSetupNames(doc)

    for setup_name in setup_names:
        if setup_name == dwg_export_option_name:
            # Get the export options for the specified setup name
            dwg_export_options = DWGExportOptions.GetPredefinedOptions(doc, setup_name)
            return dwg_export_options

    return dwg_export_options



def export_sheet_to_dwg (doc, view_sheet, sheet_name_string, output_directory, dwg_export_option_name=None):
    """
    Exports a Revit sheet to PDF using the provided naming rule and output directory.

    :param doc: The Revit document.
    :type doc: Autodesk.Revit.DB.Document
    :param view_sheet: The sheet to export.
    :type view_sheet: Autodesk.Revit.DB.ViewSheet
    :param sheet_name_string: The string to build the sheet name.
    :type sheet_name_string: str
    :param output_directory: The directory to save the PDF file.
    :type output_directory: str
    """

    dwg_export_option = None

    if dwg_export_option_name:
        dwg_export_option = get_dwg_export_option_by_name(doc, dwg_export_option_name)
    else:
        # Set the naming rule if provided
        dwg_export_option = set_dwg_export_option(dwg_export_option_name)
   

    sheets = List[ElementId]()
    sheets.Add(view_sheet.Id)

    # Export the sheet to PDF
    export_result = doc.Export(
        output_directory,
        "",
        sheets,
        dwg_export_option
    )

    print("...Export sheet with status: {}".format(export_result))
    
    if export_result:
        # need to rename the cad file after export??
        # Get the export file name
        exported_file_name = view_sheet.SheetNumber + " - " + view_sheet.Name

        # find the file
        files_match = get_files_single_directory(
            folder_path= output_directory, 
            file_prefix="", 
            file_suffix=exported_file_name, 
            file_extension=".dwg"
        )

        # check if the file exists
        if len(files_match) > 1:
            # more than one file found
            return False
        elif len(files_match) == 0:
            # no file found
            return False

        sheet_parameter_data = get_sheet_parameter_data(view_sheet)
        sheet_name_new = []

        # Split the string by the delimiters and return the chunks
        chunks = get_naming_chunks(sheet_name_string)

        # Build the naming rule using the provided string
        for chunk in chunks:
            if chunk in sheet_parameter_data:
                # if the chunk is a parameter name, get the parameter value
                param_value = sheet_parameter_data[chunk]
                sheet_name_new.append(param_value)
            else:
                # if the chunk does not contain a parameter name, add it as is
                sheet_name_new.append(chunk)

        
        sheet_name_new_joined = "".join(sheet_name_new)

        # built the new file name
        new_file_name = os.path.join(output_directory , sheet_name_new_joined + ".dwg")

        # Rename the file
        rename_result = rename_file(files_match[0], new_file_name)

        if(rename_result):
            print("...File renamed successfully to match naming rule.")
        else:
            print("...File rename failed.")

        export_result = export_result and rename_result




    return export_result