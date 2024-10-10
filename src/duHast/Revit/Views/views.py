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

import clr
import System

# import common library modules
from duHast.Revit.Common import common as com
from duHast.Revit.Views.Utility.view_types import _get_view_types
from duHast.Revit.Views.schedules_revision_filter import (
    filter_revision_schedules,
    filter_schedules,
)
from duHast.Revit.Views.sheets import get_all_sheets
from duHast.Revit.Areas.areas import get_area_scheme_by_name, get_area_schemes, get_views_by_area_scheme_name
from duHast.Revit.Common.parameter_get_utils import (
    get_built_in_parameter_value,
    get_parameter_value_as_element_id,
)

# import Autodesk
from Autodesk.Revit.DB import (
    BuiltInParameter,
    ElementClassFilter,
    ElementId,
    FilteredElementCollector,
    View,
    ViewType,
)


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
    col = FilteredElementCollector(doc).OfClass(View)
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
    col = FilteredElementCollector(doc).OfClass(View)
    for v in col:
        # filter out browser organization and other views which cant be deleted
        if (
            v.IsTemplate == False
            and filter(v) == True
            and v.ViewType != ViewType.SystemBrowser
            and v.ViewType != ViewType.ProjectBrowser
            and v.ViewType != ViewType.Undefined
            and v.ViewType != ViewType.Internal
            and v.ViewType != ViewType.DrawingSheet
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
    views_in_model = get_views_in_model(doc=doc, filter=filter_schedules)
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


def get_view_phase_id(view):
    """
    Get the views phase id.

    Note if view does not support phase id and Invlaid ElementId (-1) is returned

    :param view: The view of which to return the phase id
    :type view: Autodesk.Revit.DB.View

    :return: An element id representing the phase id. If view does not support phases then an Invalid id (-1) will be returned.
    :rtype: list of Autodesk.Revit.DB.ElementId
    """

    # set up the default value ( no phase )
    return_value = ElementId.InvalidElementId

    # attempt to get the phase id from the view
    phase_id = get_built_in_parameter_value(
        element=view,
        built_in_parameter_def=BuiltInParameter.VIEW_PHASE,
        parameter_value_getter=get_parameter_value_as_element_id,
    )

    # check what came back and return accordingly
    if phase_id is not None:
        return phase_id
    else:
        return return_value


def get_area_scheme_of_view(doc, view):
    """
    Returns the area scheme an area plan is associated with.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param view: The view of which to return the area scheme
    :type view: Autodesk.Revit.DB.View
    :return: The area scheme if the view is of type AreaPlan otherwise None
    :rtype: str or None
    """
    if view.ViewType != ViewType.AreaPlan:
        return None
    
    area_schemes_in_model = get_area_schemes(doc=doc)

    for area_scheme in area_schemes_in_model:
        views_by_area_scheme = get_views_by_area_scheme_name(doc=doc, area_scheme_name=area_scheme.Name)
        for view_in_scheme in views_by_area_scheme:
            if view_in_scheme.Id == view.Id:
                return area_scheme
    
    return None