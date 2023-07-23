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
# Copyright © 2023, Jan Christel
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
import System

# import common library modules
from duHast.Revit.Common import common as com
from duHast.Revit.Views.Utility.view_types import _get_view_types
from duHast.Revit.Views.schedules import filter_revision_schedules
from duHast.Revit.Views.sheets import get_all_sheets

# import Autodesk
import Autodesk.Revit.DB as rdb


def get_view_types(doc):
    """
    Returns all view family types in a model
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A filtered element collector.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    """

    collector = _get_view_types(doc)
    return collector


def get_view_type_ids(doc):
    """
    Returns all view family type ids in a model

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: ids of view family types
    :rtype: list of Autodesk.Revit.DB.ElementId
    """

    ids = []
    col = get_view_types(doc)
    ids = com.get_ids_from_element_collector(col)
    return ids


def get_views_of_type(doc, view_type):
    """
    Gets all views in a model of a given type. Excludes templates.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param view_type: Filter: the view type
    :type view_type: Autodesk.Revit.DB.ViewType

    :return: list of views
    :rtype: list of Autodesk.Revit.DB.View
    """

    views = []
    col = rdb.FilteredElementCollector(doc).OfClass(rdb.View)
    for v in col:
        if v.ViewType == view_type and v.IsTemplate == False:
            views.append(v)
    return views


# ----------------------------------------------------------------------------------------


def get_viewport_on_sheets(doc, sheets):
    """
    Get all view ports on sheets provided.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param sheets: list of sheets of which to return the view ports from.
    :type sheets: list of Autodesk.Revit.DB.ViewSheet

    :return: list of view ports
    :rtype: list of Autodesk.Revit.DB.Viewport
    """

    view_ports = []
    for sheet in sheets:
        try:
            viewport_ids = sheet.GetAllViewports()
            if viewport_ids != None:
                for viewport_id in viewport_ids:
                    viewport = doc.GetElement(viewport_id)
                    view_ports.append(viewport)
        except Exception as e:
            print("Get view ports on sheet: {} threw exception: {}".format(sheet, e))
    return view_ports


def get_views_in_model(doc, filter):
    """
    Gets all views in a model which are matching a filter and are:

    - not template views
    - not system browser
    - not project browser
    - not undefined
    - not Internal
    - not sheets


    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param filter: function checking view
    :type filter: func(view) returning a bool

    :return: list of views
    :rtype: list of Autodesk.Revit.DB.View
    """

    views = []
    col = rdb.FilteredElementCollector(doc).OfClass(rdb.View)
    for v in col:
        # filter out browser organization and other views which cant be deleted
        if (
            v.IsTemplate == False
            and filter(v) == True
            and v.ViewType != rdb.ViewType.SystemBrowser
            and v.ViewType != rdb.ViewType.ProjectBrowser
            and v.ViewType != rdb.ViewType.Undefined
            and v.ViewType != rdb.ViewType.Internal
            and v.ViewType != rdb.ViewType.DrawingSheet
        ):
            views.append(v)
    return views


def get_views_not_on_sheet(doc):
    """
    Gets all views not placed on a sheet. (Excludes schedules)

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A list of views which are currently not placed on a sheet.
    :rtype: list of Autodesk.Revit.DB.View
    """

    views_not_on_sheet = []
    # get all sheets
    sheets_in_model = get_all_sheets(doc)
    # get all viewPorts on sheets
    view_ports_on_sheets = get_viewport_on_sheets(doc, sheets_in_model)
    # get all views in model
    views_in_model = get_views_in_model(doc, filter_revision_schedules)
    # check whether view has a viewport if not ... its not placed on a sheet
    for view_in_model in views_in_model:
        match = False
        for view_ports_on_sheet in view_ports_on_sheets:
            if view_ports_on_sheet.ViewId == view_in_model.Id:
                match = True
                break
        if match == False:
            views_not_on_sheet.append(view_in_model)
    return views_not_on_sheet
