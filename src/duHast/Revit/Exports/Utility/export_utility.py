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

from duHast.Revit.Common import parameter_get_utils as rParaGet

def get_sheet_parameter_data (view_sheet):
    """
    Retrieves the parameter data from a given view sheet.

    :param view_sheet: The view sheet element from which to retrieve parameter data.
    :type view_sheet: Autodesk.Revit.DB.ViewSheet
    :return: A dictionary containing the parameter names and their corresponding values.
    :rtype: dict
    """

    data = {}
    paras = view_sheet.GetOrderedParameters()

    for para in paras:
            # get values as utf-8 encoded strings
            # for some characters this still throws an exception...added ascii encoding
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


def replace_illegal_characters_from_dwg_file_name(current_file_name, replace_full_stop=True):
    """
    replaces illegal characters with dashes in the given string.
    
    :param string: The string to replace characters in.
    :type string: str
    
    :return: The amended string.
    :rtype: str
    """
    
    # Define the illegal characters
   
    illegal_characters = {
        ".":"-",
        "/":"-",
    }
    
    # Replace each illegal character with the designated replacement string
    for char, replacement in illegal_characters.items():
        # only replace full stop if indicated
        if char == "." and not replace_full_stop:
            continue
        current_file_name = current_file_name.replace(char,  replacement)
    
    return current_file_name