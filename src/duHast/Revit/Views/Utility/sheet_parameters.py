"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to Sheets
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2023, Jan Christel
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

from Autodesk.Revit.DB import BuiltInParameter


def get_sheet_number(sht):
    """
    Get the sheet number of a sheet
    :param sht: The sheet to get the number of
    :type sht: ViewSheet
    :return: The sheet number
    :rtype: str
    """

    try:
        return sht.get_Parameter(BuiltInParameter.SHEET_NUMBER).AsString()
    except:
        return None


def get_sheet_name(sht):
    """
    Get the sheet name of a sheet
    :param sht: The sheet to get the name of
    :type sht: ViewSheet
    :return: The sheet name
    :rtype: str
    """

    try:
        return sht.get_Parameter(BuiltInParameter.SHEET_NAME).AsString()
    except:
        return None


def get_sheet_num_name_comb(sht, num_first=True, separator=" - "):
    """
    Get the sheet number and name of a sheet and returns the the combination
    of the two. Typically helpful for logging/printing.

    :type sht: ViewSheet
    :param num_first: Whether the sheet number should be first in the string. Defaults to True
    :type num_first: bool
    :param splitter: The string to split the sheet number and name with. Defaults to ' - '
    :type splitter: str
    :return: The sheet number and name
    :rtype: str

    """

    num = get_sheet_number(sht)
    name = get_sheet_name(sht)

    if all([num, name]):
        if num_first:
            return num + separator + name
        else:
            return name + separator + num
    else:
        return None
