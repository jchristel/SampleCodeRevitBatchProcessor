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

from System.Collections.Generic import List

from Autodesk.Revit.DB import  Document, ElementId, TableCellCombinedParameterData, ViewSheet

from duHast.Utilities.Objects import result as res
from duHast.UI.Objects.ProgressBase import ProgressBase
from duHast.Utilities.directory_io import directory_exists
from duHast.Revit.Exports.Utility.export_options_pdf_2024 import set_pdf_export_option_2024
from duHast.Revit.Exports.Utility.convert_pdf_dwg_settings import convert_settings_json_string_to_settings_objects

def create_naming_rule(sheet_name_string, sample_sheet):
    """
    Creates a naming rule for the PDF export based on the provided sheet name string.
    
    :param sheet_name_string: The sheet name string to use for the naming rule.
    :type sheet_name_string: str
    :return: The created naming rule.
    :rtype: str
    """
    

    # get all parameters from the sheet and id to build the naming rule
    para_dic = {}
    paras = sample_sheet.GetOrderedParameters()
    for p in paras:
        para_dic[p.Definition.Name] = p.Id

    # get settings from settings string
    settings =  convert_settings_json_string_to_settings_objects(sheet_name_string)
   
    # Create a list to hold the naming rules
    rules = List[TableCellCombinedParameterData]()

    # Build the naming rule using the provided string
    for setting in settings:

        # check if parameter exists if not skip this setting
        if setting.propertyName not in para_dic.keys():
            continue

        # Create a new naming rule
        rule = TableCellCombinedParameterData.Create()

        # set the prefix value if it is not None
        if setting.prefix is not None:
            rule.Prefix = setting.prefix
        
        if setting.suffix is not None:
            rule.Suffix = setting.suffix
        
        if setting.separator is not None:
            rule.Separator = setting.separator
        
        # check if this is a parameter name
        if setting.propertyName in para_dic.keys():
            rule.ParamId = para_dic[setting.propertyName]

        # add the rule to the list of rules 
        rules.Add(rule)

    return rules


def export_sheet_to_pdf (doc, view_sheet, sheet_name_string, output_directory):
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
        
        # Create the naming rule for the PDF export
        naming_rule = create_naming_rule(sheet_name_string, view_sheet)

        # Create the PDF export options
        pdf_export_option = set_pdf_export_option_2024(naming_rule)

        sheets = List[ElementId]()
        sheets.Add(view_sheet.Id)
        # Export the sheet to PDF
        export_result = doc.Export(output_directory, sheets,pdf_export_option)

        # reporting..
        sheet_identifier = "{} {}".format(view_sheet.SheetNumber, view_sheet.Name)

        if export_result:
            return_value.append_message("Sheet {} exported to PDF successfully.".format(sheet_identifier))
        else:
            return_value.update_sep(False, "Failed to export sheet {} to PDF.".format(sheet_identifier))

        return return_value
    
    except Exception as e:
            # handle the exception
            return_value.update_sep(False, "Error exporting sheets to PDF: {}".format(str(e)))
            return return_value


def export_sheets_to_pdf(doc, sheets, sheet_name_string, output_directory, callback=None):
    """
    Exports multiple Revit sheets to PDF using the provided naming rule and output directory.

    :param doc: The Revit document.
    :type doc: Autodesk.Revit.DB.Document
    :param sheets: The list of sheets to export.
    :type sheets: List[Autodesk.Revit.DB.ViewSheet]
    :param sheet_name_string: The string to build the sheet name.
    :type sheet_name_string: str
    :param output_directory: The directory to save the PDF files.
    :type output_directory: str
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

        # check if the callback is of progressBase
        if callback is not None and not isinstance(callback, ProgressBase):
            raise TypeError("callback must be an instance of ProgressBase or None")


        # Check if the callback is None, if so export all in one go
        if callback is None:

            # Create the naming rule for the PDF export
            naming_rule = create_naming_rule(sheet_name_string, sheets[0])

            # Create the PDF export options
            pdf_export_option = set_pdf_export_option_2024(naming_rule=naming_rule)

            # convert to .net list
            sheets_net = List[ElementId]()
            for sheet in sheets:
                sheets_net.Add(sheet.Id)

            # Export the sheets to PDF
            export_result = doc.Export(output_directory, sheets_net, pdf_export_option)

            if export_result:
                return_value.update_sep(True, "Sheets exported to PDF successfully.")
            else:
                return_value.update_sep(False, "Failed to export sheets to PDF.")
        else:
            # export one sheet at the time and update the progress
            total_sheets = len(sheets)
            callback.update(0,  total_sheets)

            # loop over sheet at the time and export to pdf
            for i, sheet in enumerate(sheets):

                # update the progress
                callback.update(i, total_sheets)

                # Export the sheet to PDF
                export_result = export_sheet_to_pdf(doc, sheet, sheet_name_string, output_directory)
                return_value.update(export_result)

                # check if user cancel the export
                if callback.is_cancelled():
                    return_value.append_message("User cancelled!")
                    break
        
        return return_value
    except Exception as e:
        # handle the exception
        return_value.update_sep(False, "Error exporting sheets to PDF: {}".format(str(e)))
        return return_value
   