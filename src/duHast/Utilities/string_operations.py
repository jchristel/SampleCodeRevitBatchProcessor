# -*- coding: utf-8 -*-
"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains string functions for string re-formatting. 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


"""
#
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

import re


def remove_currency_sign(number_string):
    """
    Remove a set of currency signs from a string.

    supported currency signs: $, €, £, ¥, ₹

    :param number_string: The string to remove the currency sign from.
    :type number_string: str

    :return: The string without the currency sign.
    :rtype: str
    """

    # Regular expression to match common currency signs at the start of the string
    pattern = r"^[\$\€\£\¥\₹]"

    # Remove the currency sign if present
    cleaned_string = re.sub(pattern, "", number_string)

    return cleaned_string


def replace_new_lines(input_string):
    """
    Replace all new line characters with a space and remove trailing spaces.

    :param input_string: The string to modify.
    :type input_string: str

    :return: The modified string.
    :rtype: str
    """

    # Replace all new line characters with a space
    modified_string = input_string.replace("\n", " ")
    # Remove trailing spaces
    return modified_string.rstrip()


def remove_trailing_characters_from_number_string(number_string):
    """
    Remove trailing characters from a number string.
    This function is used to remove unit strings from a number string.

    :param number_string: The string to remove trailing characters from.
    :type number_string: str

    :return: The number string without trailing characters.
    :rtype: str
    """

    # Check if p_value contains a number followed by a unit string (including special characters)
    number_unit_pattern = re.compile(r"^(\d+(\.\d+)?)\s*([^\d\s]+)$")
    match = number_unit_pattern.match(number_string)
    if match:
        # found a unit string, just return the number
        value = match.group(1)
        return value
    else:
        # No unit string found, just use the value as is
        return number_string
