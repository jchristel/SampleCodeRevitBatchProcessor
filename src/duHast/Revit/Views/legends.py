"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to Revit legends. 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2024, Jan Christel
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

from Autodesk.Revit.DB import FilteredElementCollector, View, ViewType

from duHast.Revit.Views.views import get_views_not_on_sheet


def get_view_legends(doc):
    """
    Get all view legends in a model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: All view legends in the model
    :rtype: list of Autodesk.Revit.DB.View
    """

    view_legends = []
    col = FilteredElementCollector(doc).OfClass(View)
    for v in col:
        # filter out templates
        if v.ViewType == ViewType.Legend:
            view_legends.append(v)
    return view_legends


def get_view_legends_not_placed(doc):
    """
    Returns all unplaced legend views

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: All view legends in the model not on a sheet
    :rtype: list of Autodesk.Revit.DB.View
    """

    # get all legends in model:
    all_legend_views = get_view_legends(doc=doc)

    # get all views not on sheets
    all_views_not_on_sheets = get_views_not_on_sheet(doc=doc)

    unplaced_legends = []
    # loop over views and find legends
    for view in all_views_not_on_sheets:
        if view.ViewType == ViewType.Legend:
            unplaced_legends.append(view)

    return unplaced_legends
