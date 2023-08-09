"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to Revit views. 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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


def get_sheet_from_view(view, sht_num_elem_dict):
    """
    Get the sheet of a view. Sheet number to element dictionary can
    be produced with get_sheet_num_to_elem_dict function from
    duHast.Revit.Views.Utility.sheets
    :param view: The view to get the sheet of
    :type view: View
    :param sht_num_elem_dict: A dictionary of sheet numbers and sheets
    :type sht_num_elem_dict: dict
    :return: The sheet of the view
    :rtype: ViewSheet
    """
    sht_num_param = view.get_Parameter(BuiltInParameter.VIEWPORT_SHEET_NUMBER)
    if sht_num_param != None:
        sht_num = sht_num_param.AsString()

        if sht_num == "":
            None

        try:
            return sht_num_elem_dict[sht_num]
        except KeyError as e:
            None

    else:
        return None
