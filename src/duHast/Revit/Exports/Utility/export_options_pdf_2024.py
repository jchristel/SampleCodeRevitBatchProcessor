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



from Autodesk.Revit.DB import  ColorDepthType, ExportPaperFormat, PDFExportOptions, PDFExportQualityType


def set_pdf_export_option_2024(
        naming_rule, 
        always_use_raster = False, 
        color_depth = ColorDepthType.Color,
        combine = False,
        paper_format =  ExportPaperFormat.Default,
        export_quality = PDFExportQualityType.DPI600,
        hide_crop_boundaries = True,
        hide_scope_boxes = True,
        hide_unreferenced_view_tags = True,
        mask_coincident_lines = True,
        replace_halftone_with_thin_lines = False,
        stop_on_error = False,
        view_links_in_blue = False,
        ):
    """
    Sets the PDF export options for the Revit document.
    :param naming_rule: The naming rule for the PDF export.
    :type naming_rule: str
    
    :return: The PDF export options.
    :rtype: Autodesk.Revit.DB.PDFExportOptions
    """

    pdf_export_option = PDFExportOptions()

    # Set the naming rule if valid
    if (PDFExportOptions.IsValidNamingRule(naming_rule)):
        # Set the naming rule for the PDF export options
        pdf_export_option.SetNamingRule(naming_rule)
    else:
        # If the naming rule is not valid, set it to None
        pdf_export_option.SetNamingRule(None)
        return None

    pdf_export_option.AlwaysUseRaster = always_use_raster
    pdf_export_option.ColorDepth =  color_depth
    pdf_export_option.Combine = combine
    pdf_export_option.PaperFormat = paper_format # use sheet size
    pdf_export_option.ExportQuality = export_quality

    pdf_export_option.HideCropBoundaries = hide_crop_boundaries
    pdf_export_option.HideScopeBoxes = hide_scope_boxes
    pdf_export_option.HideUnreferencedViewTags = hide_unreferenced_view_tags
    pdf_export_option.MaskCoincidentLines = mask_coincident_lines
    pdf_export_option.ReplaceHalftoneWithThinLines = replace_halftone_with_thin_lines
    pdf_export_option.StopOnError = stop_on_error
    pdf_export_option.ViewLinksInBlue = view_links_in_blue

    return pdf_export_option