"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to Revit view port to data view port conversion. 
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


from duHast.Data.Objects.Collectors.data_sheet_view_port import DataSheetViewPort
from duHast.Data.Objects.Collectors.Properties.data_view_port_type_names import (
    DataViewPortTypeNames,
)
from duHast.Data.Objects.Collectors.data_view_3d import DataViewThreeD
from duHast.Data.Objects.Collectors.data_view_elevation import DataViewElevation
from duHast.Data.Objects.Collectors.data_view_plan import DataViewPlan
from duHast.Data.Objects.Collectors.data_view_schedule import DataViewSchedule
from duHast.Data.Objects.Collectors.Properties.data_schedule_segement import DataScheduleSegment


from duHast.Utilities.unit_conversion import convert_imperial_feet_to_metric_mm

from duHast.Revit.Common.Geometry.points import convert_XYZ_to_point2

from Autodesk.Revit.DB import SectionType, ViewType


def _get_view_port_type(doc, revit_view_port):
    """
    Returns a string reprensenting the viewport type on None if to be ignored (not match with view port types of interest)

    :param doc: The Revit document.
    :type doc: Autodesk.Revit.DB.Document
    :param view_port: A Revit ViewPort
    :type view_port: Autodesk.Revit.DB.ViewPort

    :return: The viewport type name or none
    :rtype: str or None
    """

    view = doc.GetElement(revit_view_port.ViewId)

    if view.ViewType == ViewType.FloorPlan:
        return DataViewPortTypeNames.FLOOR_PLAN
    elif view.ViewType == ViewType.Elevation:
        return DataViewPortTypeNames.ELEVATION
    elif view.ViewType == ViewType.ThreeD:
        return DataViewPortTypeNames.THREE_D
    elif view.ViewType == ViewType.Schedule:
        # thats unlikely
        return DataViewPortTypeNames.SCHEDULE
    else:
        return None


def _get_view_crop(view):
    # get bounding box
    crop_box = view.CropBox

    # there is a very very slight chance that view is not cropped ...it should be but...
    if crop_box:
        # get the outlines min and max points as 2d points
        bb_max_2d = convert_XYZ_to_point2(crop_box.Max)
        bb_min_2d = convert_XYZ_to_point2(crop_box.Min)

        return bb_min_2d, bb_max_2d
    else:
        return None


def _get_plan_view(view):
    """
    Converts data from a Revit plan view to a data plan view instance

    :param view: The Revit view
    :type view: Autodesk.Revit.DB.ViewPlan

    :return: A data view instance
    :rtype: :class:`.DataViewPlan`
    """

    data_instance = DataViewPlan()

    # get the view crop
    bb_min_2d, bb_max_2d = _get_view_crop(view)
    if bb_min_2d and bb_max_2d:
        data_instance.bounding_box.update(bb_min_2d, bb_max_2d)

    # get any tags in the view
    return data_instance


def _get_elevation_view(view):
    """
    Converts data from a Revit elevation view to a data elevation view instance

    :param view: The Revit view
    :type view: Autodesk.Revit.DB.ViewSection

    :return: A data view instance
    :rtype: :class:`.DataViewElevation`
    """

    data_instance = DataViewElevation()

    # get bounding box
    bb_min_2d, bb_max_2d = _get_view_crop(view)
    if bb_min_2d and bb_max_2d:
        data_instance.bounding_box.update(bb_min_2d, bb_max_2d)

    # orientation (which edge of the bounding box is this elevation facing?)
    # get any tags in the view

    return data_instance


def _get_three_d_view(view):
    """
    Converts data from a Revit 3D view to a data 3D view instance

    :param view: The Revit view
    :type view: Autodesk.Revit.DB.View3D

    :return: A data view instance
    :rtype: :class:`.DataViewThreeD`
    """

    data_instance = DataViewThreeD()

    # get bounding box
    bb_min_2d, bb_max_2d = _get_view_crop(view)
    if bb_min_2d and bb_max_2d:
        data_instance.bounding_box.update(bb_min_2d, bb_max_2d)

    # orientation (eye point and view direction)
    return data_instance


def _get_schedule_view(view):
    """
    Converts data from a Revit schedule view to a data schedule view instance

    :param view: The Revit view
    :type view: Autodesk.Revit.DB.ViewSchedule

    :return: A data view instance
    :rtype: :class:`.DataViewSchedule`
    """

    data_instance = DataViewSchedule()

    # here is a way to extract number of rows: (old...)
    # https://thebuildingcoder.typepad.com/blog/2012/05/the-schedule-api-and-access-to-schedule-data.html
    # this might be better and more up to date: https://forums.autodesk.com/t5/revit-api-forum/how-to-get-schedule-data/td-p/7319520
    # in fact it does show how to get to number of rows easily...

    table = view.GetTableData()
    section = table.GetSectionData(SectionType.Body)
    number_of_rows = section.NumberOfRows

    # store the number of data rows
    data_instance.total_number_of_rows = number_of_rows

    # The total count of schedule segments. 1 means the schedule is not split yet.
    for i in range(view.GetSegmentCount() - 1):
        seg_data = DataScheduleSegment()
        seg_data.index = i
        seg_height = convert_imperial_feet_to_metric_mm(view.GetSegmentHeight(i))
        seg_data.height = seg_height
        data_instance.segments.append(seg_data)

    # get bounding box
    # TODO:
    return data_instance


def _get_view_data(view):
    """
    Set up view data instance depending ov view type

    :param view: The view to be converted
    :type view: Autodesk.Revit.DB.View

    :return: A data view instance
    :rtype: :class:`.DataViewBase`
    """

    view_data_instance = None

    # check view type
    if view.ViewType == ViewType.FloorPlan:
        # plan view
        view_data_instance = _get_plan_view(view=view)
    elif view.ViewType == ViewType.Elevation:
        # elevation
        view_data_instance = _get_elevation_view(view=view)
    elif view.ViewType == ViewType.ThreeD:
        # 3D
        view_data_instance = _get_three_d_view(view=view)
    elif view.ViewType == ViewType.Schedule:
        # schedule
        view_data_instance = _get_schedule_view(view=view)

    return view_data_instance


def convert_revit_viewport_to_data_instance(doc, revit_view_port):
    """
    Converts a Revit ViewPort into a data viewport

    :param doc: The Revit document.
    :type doc: Autodesk.Revit.DB.Document
    :param view_port: A Revit ViewPort
    :type view_port: Autodesk.Revit.DB.ViewPort
    :return: A populated data viewport instance
    :rtype: :class:`.DataSheetViewPort`
    """

    view_port_type = _get_view_port_type(doc, revit_view_port)
    if view_port_type == None:
        # ignore this viewport
        return None

    # set up data instances
    view_port_data = DataSheetViewPort()

    # get an outline from the Revit view port
    view_port_outline = revit_view_port.GetBoxOutline()

    # get the outlines min and max points as 2d points
    bb_max_2d = convert_XYZ_to_point2(view_port_outline.MaximumPoint)
    bb_min_2d = convert_XYZ_to_point2(view_port_outline.MinimumPoint)

    # update the bounding box property of the view port instance
    view_port_data.bounding_box.update(bb_min_2d, bb_max_2d)

    # get the viewport centre
    centre_point = convert_XYZ_to_point2(revit_view_port.GetBoxCenter())
    view_port_data.centre_point = centre_point

    # set the viewport type
    view_port_data.vp_type = view_port_type

    # set the view
    revit_view = doc.GetElement(revit_view_port.ViewId)
    view_data = _get_view_data(view=revit_view)
    view_port_data.view = view_data

    return view_port_data


def convert_revit_schedule_sheet_instances_to_data_instance(
    doc, sheet, revit_schedule_sheet_instances
):
    """
    Converts a list of schedule sheet instances to view port data instances

    :param doc: The Revit document.
    :type doc: Autodesk.Revit.DB.Document
    :param sheet: The sheet of which to get the schedule instance from.
    :type sheet: Autodesk.Revit.DB.ViewSheet
    :param revit_schedule_sheet_instances: A list of schedule sheet instances
    :type revit_schedule_sheet_instances: [Autodesk.Revit.DB.ScheduleSheetInstance]
    :return: A list of populated data viewport instances
    :rtype: [:class:`.DataSheetViewPort`]
    """

    all_view_port_data = []

    # loop over all schedule sheet instances
    for schedule_sheet_instance in revit_schedule_sheet_instances:

        # set up data instances
        view_port_data = DataSheetViewPort()
        view_port_data.vp_type = DataViewPortTypeNames.SCHEDULE

        # bounding box:
        bbox = schedule_sheet_instance.get_BoundingBox(sheet)
        # get the outlines min and max points as 2d points
        bb_max_2d = convert_XYZ_to_point2(bbox.Max)
        bb_min_2d = convert_XYZ_to_point2(bbox.Min)

        # get the viewport centre
        centre_point = convert_XYZ_to_point2(schedule_sheet_instance.Point)
        view_port_data.centre_point = centre_point

        # update the bounding box property of the view port instance
        view_port_data.bounding_box.update(bb_min_2d, bb_max_2d)

        # get the schedule view data
        schedule_view = doc.GetElement(schedule_sheet_instance.ScheduleId)
        view_data = _get_schedule_view(schedule_view)
        view_port_data.view = view_data

        # append to list to be returned
        all_view_port_data.append(view_port_data)

    return all_view_port_data
