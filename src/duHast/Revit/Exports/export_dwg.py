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
from duHast.Utilities.Objects import result as res
from duHast.Utilities.directory_io import directory_exists
from duHast.UI.Objects.ProgressBase import ProgressBase
from duHast.Revit.Exports.Utility.convert_pdf_dwg_settings import convert_settings_json_string_to_settings_objects
from duHast.Revit.Exports.Utility.export_utility import replace_illegal_characters_from_dwg_file_name


from System.Collections.Generic import List

from Autodesk.Revit.DB import ACADVersion, BaseExportOptions,Document, DWGExportOptions,ElementId,ViewSheet

from duHast.Revit.Exports.Utility.export_utility import get_sheet_parameter_data


def set_dwg_export_option():

    # Create a new instance of DWGExportOptions
    dwg_export_options = DWGExportOptions()

    dwg_export_options.FileVersion = ACADVersion.R2010
    dwg_export_options.HideReferencePlane = True
    dwg_export_options.HideScopeBox = True
    dwg_export_options.HideUnreferenceViewTags	= True
    dwg_export_options.MergedViews = True

    return dwg_export_options


def get_all_dwg_export_options(doc):
    """
    Retrieves all DWG export options.

    :param doc: The Revit document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A list of DWG export options.
    :rtype: list
    """

    # Get the export options for the specified setup name
    dwg_export_options = DWGExportOptions.GetPredefinedOptions(doc)

    # Get the export option names
    setup_names = BaseExportOptions.GetPredefinedSetupNames(doc)

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

    return None


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

    return_value = res.Result()
    try:

        # Check if we got a document
        if not isinstance(doc, Document):
            raise TypeError("doc must be an instance of Autodesk.Revit.DB.Document")
    
        # Check if we got a list of sheets
        if not isinstance(view_sheet,  ViewSheet):
            raise TypeError("view_sheet must be an Autodesk.Revit.DB.ViewSheet instances")
        
        # Check if the output directory exists
        if not directory_exists(output_directory):
            return_value.update_sep(False, "Output directory does not exist.")
            return return_value

        # Check if the sheet name string is a string or None
        if not isinstance(sheet_name_string, str) and sheet_name_string is not None:
            raise TypeError("sheet_name_string must be a string or None")
        
        # check if the dwg export option name is a string or None
        if dwg_export_option_name is not None and not isinstance(dwg_export_option_name, str):
            raise TypeError("dwg_export_option_name must be a string or None")


        dwg_export_option = None

        if dwg_export_option_name:
            dwg_export_option = get_dwg_export_option_by_name(doc, dwg_export_option_name)
            if dwg_export_option is None:
                return_value.update_sep(False, "DWG export option {} not found.".format(dwg_export_option_name))
                return return_value
        else:
            # Set the naming rule if provided
            dwg_export_option = set_dwg_export_option()
    
        # convert to .net list
        sheets = List[ElementId]()
        sheets.Add(view_sheet.Id)

        # Export the sheet to PDF
        export_result = doc.Export(
            output_directory,
            "",
            sheets,
            dwg_export_option
        )

        # reporting..
        sheet_identifier = "{} {}".format(view_sheet.SheetNumber, view_sheet.Name)

        # Check if the export was successful
        if export_result:
            return_value.update_sep(True, "Exported sheet {} to DWG successfully.".format(sheet_identifier))
        else:
            return_value.update_sep(False, "Export of sheet {} failed.".format(sheet_identifier))

        # If the export was successful, rename the file
        if export_result:
            # need to rename the cad file after export...
            # Get the export file name
            exported_file_name = view_sheet.SheetNumber + " - " + view_sheet.Name

            # remove the invalid characters from the file name
            # this is the name Revit uses to export the file (Revit replaces characters that are 'not allowed' in file names with dashes)
            exported_file_name = replace_illegal_characters_from_dwg_file_name(exported_file_name)
            
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
                return_value.update_sep(False, "More than one file found matching {} . Please check the output directory.".format(exported_file_name))
                return return_value
            elif len(files_match) == 0:
                # no file found
                return_value.update_sep(False, "No file found matching {} . Please check the output directory.".format(exported_file_name))
                return return_value

            # Get the sheet parameter data
            sheet_parameter_data = get_sheet_parameter_data(view_sheet)

            # convert name rules string to settings objects
            dwg_name_rules = convert_settings_json_string_to_settings_objects(sheet_name_string)
            
            # set up new sheet name
            sheet_name_new = []

            # set up a rule counter to keep track of whether a rule is the last of the rules
            rule_counter = 0

            # loop over the naming rules
            for rule in dwg_name_rules:

                if rule.propertyName not in sheet_parameter_data:
                    # if the rule is not a parameter name, skip it
                    continue

                # check if the rule has a prefix
                if rule.prefix is not None:
                    sheet_name_new.append(rule.prefix)

                # add the parameter value to the sheet name
                sheet_name_new.append(sheet_parameter_data[rule.propertyName])

                # check if the rule has a suffix
                if rule.suffix is not None:
                    sheet_name_new.append(rule.suffix)

                # only add the separator if it is not None and not the last one
                if rule.separator is not None and rule_counter < len(dwg_name_rules):
                    sheet_name_new.append(rule.separator)

                # increase the rule counter
                rule_counter += 1

            # build the sheet name from the chunks list
            sheet_name_new_joined = "".join(sheet_name_new)

            # remove the invalid characters from the file name
            # but keep the full stop if any to match the doc number / name in Revit
            sheet_name_new_joined = replace_illegal_characters_from_dwg_file_name(sheet_name_new_joined, replace_full_stop=False)

            # built the new file name
            new_file_name = os.path.join(output_directory , sheet_name_new_joined + ".dwg")

            # Rename the file
            rename_result = rename_file(files_match[0], new_file_name)

            if(rename_result):
                return_value.append_message("...File renamed successfully to match naming rule: {}".format(sheet_name_new_joined))
            else:
                return_value.update_sep(False, "...File rename to {} failed.".format(sheet_name_new_joined))

        else:
            # if the export failed, we don't need to rename the file
            return_value.append_message("...Export failed, no need to rename the file.")

        return return_value
    
    except Exception as e:
        # handle the exception
        return_value.update_sep(False, "Error exporting sheets to dwg: {}".format(str(e)))
        return return_value
    

def export_sheets_to_dwg(doc, sheets, sheet_name_string, output_directory, dwg_export_option_name=None, callback=None):
    """
    Exports a list of Revit sheets to DWG using the provided naming rule and output directory.

    :param doc: The Revit document.
    :type doc: Autodesk.Revit.DB.Document
    :param sheets: The list of sheets to export.
    :type sheets: list
    :param sheet_name_string: The string to build the sheet name.
    :type sheet_name_string: str
    :param output_directory: The directory to save the DWG file.
    :type output_directory: str
    :param dwg_export_option_name: The name of the DWG export option.
    :type dwg_export_option_name: str
    :param callback: The callback to update the progress.
    :type callback: ProgressBase

    :return: The result of the export operation.
    :rtype: Result
    """

    return_value = res.Result()

    try:

        # Check if we got a document
        if not isinstance(doc, Document):
            raise TypeError("doc must be an instance of Autodesk.Revit.DB.Document")
    
        # Check if we got a list of sheets
        if not isinstance(sheets, list) or not all(isinstance(sheet, ViewSheet) for sheet in sheets):
            raise TypeError("sheets must be a list of Autodesk.Revit.DB.ViewSheet instances")
        
        # Check if the output directory exists
        if not directory_exists(output_directory):
            return_value.update_sep(False, "Output directory does not exist.")
            return return_value

        # Check if the sheet name string is a string or None
        if not isinstance(sheet_name_string, str) and sheet_name_string is not None:
            raise TypeError("sheet_name_string must be a string or None")
        
        # check if the dwg export option name is a string or None
        if dwg_export_option_name is not None and not isinstance(dwg_export_option_name, str):
            raise TypeError("dwg_export_option_name must be a string or None")
    
        # check if the callback is of progressBase
        if callback is not None and not isinstance(callback, ProgressBase):
            raise TypeError("callback must be an instance of ProgressBase or None")
        
        # Check if the callback is None, if so export all in one go
        if callback is None:

            # loop over sheet at the time and export to pdf
            for i, sheet in enumerate(sheets):

                # Export the sheet to PDF
                export_result = export_sheet_to_dwg(doc, sheet, sheet_name_string, output_directory, dwg_export_option_name)
                return_value.update(export_result)
           
        else:
            # export one sheet at the time and update the progress
            total_sheets = len(sheets)
            callback.update(0,  total_sheets)

            # loop over sheet at the time and export to pdf
            for i, sheet in enumerate(sheets):

                # update the progress
                callback.update(i, total_sheets)

                # Export the sheet to PDF
                export_result = export_sheet_to_dwg(doc, sheet, sheet_name_string, output_directory, dwg_export_option_name)
                return_value.update(export_result)

                # check if user cancel the export
                if callback.is_cancelled():
                    return_value.append_message("User cancelled!")
                    break
    
    except Exception as e:
        # handle the exception
        return_value.update_sep(False, "Error exporting sheets to DWG: {}".format(str(e)))
        return return_value