"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Implementation of a user pick action with a custom element selection filter.
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

from Autodesk.Revit.UI.Selection import ObjectType

from duHast.Revit.UI.Objects.CustomSelectionFilter import CustomSelectionFilter
from duHast.Revit.UI.custom_selection_filter_element import selection_filter_floors

def get_user_selection(doc, uidoc, ui_text, selection_filter=selection_filter_floors):
    """
    Get user selection of set down families.

    :param doc: Revit Document
    :type doc: Autodesk.Revit.DB.Document
    :param uidoc: Revit UIDocument
    :type uidoc: Autodesk.Revit.UI.UIDocument
    :param ui_text: User text for the selection dialog
    :type ui_text: str
    :return: Tuple containing a list of selected elements and a list of selected element ids.
    :rtype: (list, list)
    """

    elements_selected = []
    elements_selected_ids = []
    try:
        # get the selected elements
        sel_filter = CustomSelectionFilter(selection_filter)
        sel_elements = uidoc.Selection.PickObjects(
            ObjectType.Element, sel_filter, ui_text
        )

        # get the actual selected elements ( PickObject returns a bunch of reference objects only!)
        for e in sel_elements:
            elements_selected_ids.append(e.ElementId)
            element = doc.GetElement(e.ElementId)
            elements_selected.append(element)

    except Exception as e:
        print(e)
    return elements_selected, elements_selected_ids