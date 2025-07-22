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

import clr
import os
import sys

from System.Collections.Generic import List

from duHast.Revit.Common import parameter_get_utils as rParaGet
from duHast.Revit.Views.sheets import get_all_sheets

from Autodesk.Revit.DB import BuiltInParameter

# set up some options for the user to select
EXPORT_PDF_ONLY = "PDF only"
EXPORT_PDF_AND_DWG = "PDF and DWG"

# exclude the following parameters from sheet data retrieval
DEFAULT_PARAMETER_EXCLUDE_LIST = [
    BuiltInParameter.VIEW_VISIBLE_CATEGORIES,
    BuiltInParameter.VIEW_DEPENDENCY,
    BuiltInParameter.VIEW_FIXED_SKETCH_PLANE,
    BuiltInParameter.ELEM_PARTITION_PARAM,
]

def get_sheet_parameter_names(doc):

    """
    Get the parameter names assigned to sheets.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of parameter names assigned to sheets.
    :rtype: List[str]
    """
    
    # get all sheets in the document
    sheets = get_all_sheets(doc)

    parameter_names = List[str]()

    parameter_names_not_ordered =[]
    # get the parameter names from the first sheet
    for sheet in sheets:
        parameters = sheet.GetOrderedParameters()
        for p in parameters:
            parameter_names_not_ordered.append(p.Definition.Name)
       
        break
   
    # order the parameter names
    parameter_names_not_ordered = sorted(parameter_names_not_ordered, key=lambda x: x.lower())

    # add to .net list to be returned
    for name in parameter_names_not_ordered:
        parameter_names.Add(name)

    return parameter_names

def get_sheet_parameter_data (view_sheet, exclude_parameters = DEFAULT_PARAMETER_EXCLUDE_LIST):
    """
    Gets the parameter data for a given view sheet.

    :param view_sheet: The view sheet to get the parameter data from.
    :type view_sheet: Autodesk.Revit.DB.ViewSheet
    :param exclude_parameters: A list of parameters to exclude from the data.
    :type exclude_parameters: list
    :return: A dictionary containing the parameter data.
    :rtype: dict
    """

    data = {}
    paras = view_sheet.GetOrderedParameters()

    for para in paras:
            # get values as utf-8 encoded strings
            # for some characters this still throws an exception...added ascii encoding

            # ignore visibility graphics
            if para.Definition.BuiltInParameter in exclude_parameters:
                continue


            # get the value of the parameter
            value = rParaGet.get_parameter_value_utf8_string(para)
            try:
                data[para.Definition.Name] = value
            except:
                data[para.Definition.Name] = "Failed to retrieve value"

    return data

def get_naming_chunks(sheet_name_string):
    """
    Splits the sheet name string into chunks based on the delimiters.
    
    :param sheet_name_string: The sheet name string to split.
    :type sheet_name_string: str
    :return: A list of chunks.
    :rtype: list
    """
    
    # Split the string by the delimiters and return the chunks
    return [chunk.strip() for chunk in sheet_name_string.split("*") if chunk.strip()]

def get_user_options(forms):
    """
    Gets the user options exporting pdf and dwg or just pdf

    Options are: pdf only, pdf and dwg

    :param forms: the forms object
    :type forms: Forms
    :return: the user options
    :rtype: dict
    """

    # ask user for single directory or directory by category
    # and if existing families are to be ignored
    ops = [EXPORT_PDF_ONLY,EXPORT_PDF_AND_DWG]
    configs = {
        EXPORT_PDF_ONLY: {"background": "0xFF55FF"},
        EXPORT_PDF_AND_DWG: {"background": "0xFF55FF"},
    }
    ui_options = forms.CommandSwitchWindow.show(
        ops,  message="Select export option", config=configs
    )

    return ui_options