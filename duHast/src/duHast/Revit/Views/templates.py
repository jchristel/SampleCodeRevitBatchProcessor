"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to Revit view templates. 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
#
# License:
#
#
# Revit Batch Processor Sample Code
#
# Copyright (c) 2023  Jan Christel
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#

import Autodesk.Revit.DB as rdb

from duHast.Revit.Common import common as com
from duHast.Revit.Views.Utility.view_types import _get_view_types


def get_view_templates(doc):
    """
    Get all view templates in a model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: All view templates in the model
    :rtype: list of Autodesk.Revit.DB.View
    """

    view_templates = []
    col = rdb.FilteredElementCollector(doc).OfClass(rdb.View)
    for v in col:
        # filter out templates
        if v.IsTemplate:
            view_templates.append(v)
    return view_templates


def get_view_templates_ids(doc):
    """
    Get all view template ids in a model
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: All view templates Id's in the model
    :rtype: list of Autodesk.Revit.DB.ElementId
    """

    ids = []
    col = rdb.FilteredElementCollector(doc).OfClass(rdb.View)
    for v in col:
        # filter out templates
        if v.IsTemplate:
            ids.append(v.Id)
    return ids


def get_used_view_templates_ids(doc):
    """
    Gets ids of view templates used in views in the model only
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: All used view templates Id's in the model
    :rtype: list of Autodesk.Revit.DB.ElementId
    """

    view_template_ids_used = []
    # get all view templates assigned to views
    col = rdb.FilteredElementCollector(doc).OfClass(rdb.View)
    for v in col:
        # filter out browser organization and other views which cant be deleted
        if (
            v.IsTemplate == False
            and v.ViewType != rdb.ViewType.SystemBrowser
            and v.ViewType != rdb.ViewType.ProjectBrowser
            and v.ViewType != rdb.ViewType.Undefined
            and v.ViewType != rdb.ViewType.Internal
            and v.ViewType != rdb.ViewType.DrawingSheet
        ):
            if (
                v.ViewTemplateId not in view_template_ids_used
                and v.ViewTemplateId != rdb.ElementId.InvalidElementId
            ):
                view_template_ids_used.append(v.ViewTemplateId)
    return view_template_ids_used


def get_default_view_type_template_ids(doc):
    """
    Gets view template Id's used as default by view types
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: All view templates Id's which are used as default in view types in the model
    :rtype: list of Autodesk.Revit.DB.ElementId
    """

    view_template_ids_used = []
    # get all templates assigned to view family types:
    view_family_templates = com.get_similar_type_families_by_type(doc, _get_view_types)
    for vt in view_family_templates:
        for id in vt[1]:
            # get the element
            vt_fam = doc.GetElement(id)
            if (
                vt_fam.DefaultTemplateId not in view_template_ids_used
                and vt_fam.DefaultTemplateId != rdb.ElementId.InvalidElementId
            ):
                view_template_ids_used.append(vt_fam.DefaultTemplateId)
    return view_template_ids_used


def get_all_used_view_template_ids(doc):
    """
    Get all used view template Id's.

    Templates can either be:
    - used as default by view types
    - used by a view

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: All view templates Id's which are used in the model.
    :rtype: list of Autodesk.Revit.DB.ElementId
    """

    vtv = get_used_view_templates_ids(doc)
    view_family_templates = get_default_view_type_template_ids(doc)
    for id in view_family_templates:
        if id not in vtv:
            vtv.append(id)
    return vtv


def get_template_ids_which_can_have_filters(doc, filter_by_type):
    """
    Get all templates in a model of given type

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param filter_by_type: List of view types of which to return view templates from
    :type filter_by_type: list of Autodesk.Revit.DB.ViewType
    :return: All view templates in the model
    :rtype: list of Autodesk.Revit.DB.View
    """

    view_templates = []
    col = rdb.FilteredElementCollector(doc).OfClass(rdb.View)
    for v in col:
        # filter out templates
        if v.IsTemplate:
            for filter in filter_by_type:
                if v.ViewType == filter:
                    view_templates.append(v)
                    break
    return view_templates


def get_all_unused_view_template_ids(doc):
    """
    Gets all view template Id's not used by view types or by views
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: All view templates Id's which are not used in the model.
    :rtype: list of Autodesk.Revit.DB.ElementId
    """
    used_vts = get_all_used_view_template_ids(doc)
    vt_in_model = get_view_templates(doc)
    unused_vts = []
    for vt in vt_in_model:
        if vt.Id not in used_vts:
            unused_vts.append(vt.Id)
    return unused_vts
