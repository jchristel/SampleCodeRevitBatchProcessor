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

from Autodesk.Revit.DB import  ColorDepthType, ElementId, ExportPaperFormat, PDFExportOptions, PDFExportQualityType, TableCellCombinedParameterData

def set_pdf_export_option(naming_rule):
    pdf_export_option = PDFExportOptions()

    # Set the naming rule if valid
    if (PDFExportOptions.IsValidNamingRule(naming_rule)):
        # Set the naming rule for the PDF export options
        pdf_export_option.SetNamingRule(naming_rule)
    else:
        # If the naming rule is not valid, set it to None
        pdf_export_option.SetNamingRule(None)
        print("Invalid naming rule provided. Using default naming rule.")

    #disable export in background
    #pdf_export_option.SetExportInBackground(False)

    pdf_export_option.AlwaysUseRaster = False
    pdf_export_option.ColorDepth =  ColorDepthType.Color
    pdf_export_option.Combine = False
    pdf_export_option.PaperFormat =  ExportPaperFormat.Default # use sheet size
    pdf_export_option.ExportQuality = PDFExportQualityType.DPI600

    #pdf_export_option.FileName = file_name

    pdf_export_option.HideCropBoundaries = True
    #pdf_export_option.HideReferencePlanes = True
    pdf_export_option.HideScopeBoxes = True
    pdf_export_option.HideUnreferencedViewTags = True
    pdf_export_option.MaskCoincidentLines = True
    pdf_export_option.ReplaceHalftoneWithThinLines = False
    pdf_export_option.StopOnError = False
    pdf_export_option.ViewLinksInBlue = False

    return pdf_export_option


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
        
    # Split the string by the delimiters and return the chunks
    chunks = [chunk.strip() for chunk in sheet_name_string.split("*") if chunk.strip()]

    # Create a list to hold the naming rules
    rules = List[TableCellCombinedParameterData]()

    # Initialize the prefix variable
    prefix = None

    # Build the naming rule using the provided string
    for chunk in chunks:

        # Create a new naming rule
        rule = TableCellCombinedParameterData.Create()

        # set the prefix value if it is not None
        if prefix is not None:
            rule.Prefix = prefix
            # reset the prefix
            prefix = None
        
        # check if this is a parameter name
        if chunk in para_dic.keys():
            rule.ParamId = para_dic[chunk]

        # if not check if this is a separator string (:-: is a dash)
        elif chunk.startswith(":") and chunk.endswith(":"):
            sep_string = chunk[1:-1]
            # this is the separator string to the last parameter in the rules list!
            if len(rules) > 0:
                index = len(rules) - 1
                rules[index].Separator = sep_string

        # check if the is a prefix or suffix (?P?sdsds?P?) is a prefix and this is the suffix (?S?sdsds?S?)
        elif chunk.startswith("?P?") and chunk.endswith("?P?"):
            value = chunk[3:-3]
            # prefix is applied to next rule
            prefix = value
        elif chunk.startswith("?S?") and chunk.endswith("?S?"):
            value = chunk[3:-3]
            # suffix is applied to previous rule
            if len(rules) > 0:
                index = len(rules) - 1
            rules[index].Suffix = value
            
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
    
    # Create the naming rule for the PDF export
    naming_rule = create_naming_rule(sheet_name_string, view_sheet)

    # Create the PDF export options
    pdf_export_option = set_pdf_export_option(naming_rule)

    sheets = List[ElementId]()
    sheets.Add(view_sheet.Id)
    # Export the sheet to PDF
    export_result = doc.Export(output_directory, sheets,pdf_export_option)
    return export_result


def export_sheets_to_pdf(doc, sheets, sheet_name_string, output_directory):
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
    
    # Create the naming rule for the PDF export
    naming_rule = create_naming_rule(sheet_name_string, sheets[0])

    # Create the PDF export options
    pdf_export_option = set_pdf_export_option(naming_rule)

    # convert to .net list
    sheets_net = List[ElementId]()
    for sheet in sheets:
        sheets_net.Add(sheet.Id)

    # Export the sheets to PDF
    export_result = doc.Export(output_directory, sheets_net, pdf_export_option)
    return export_result