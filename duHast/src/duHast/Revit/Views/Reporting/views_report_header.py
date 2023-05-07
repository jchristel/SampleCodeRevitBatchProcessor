"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains the header row for any Revit sheet and views reports. 
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

#: header used in views report
import Autodesk.Revit.DB as rdb

#: header used in views report
REPORT_VIEWS_HEADER = ["HOSTFILE", "Id"]

#: header used in sheets report
REPORT_SHEETS_HEADER = ["HOSTFILE", "Id"]

#: header used in schedules report
REPORT_SCHEDULES_HEADER = ["HOSTFILE", "Id"]


def get_sheets_report_headers(doc):
    """
    A list of headers used in report files
    Hardcoded header list is expanded by parameters added to sheet category in model.

    Note: if no sheet views are in a file this will report the hardcoded header only.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of headers.
    :rtype: list str
    """

    collector_views = rdb.FilteredElementCollector(doc).OfClass(rdb.ViewSheet)
    # copy headers list
    headers = REPORT_SHEETS_HEADER[:]
    for v in collector_views:
        # get all parameters attached to sheet
        paras = v.GetOrderedParameters()
        for para in paras:
            headers.append(para.Definition.Name)
        break
    return headers


def get_schedules_report_headers(doc):
    """
    A list of headers used in report files
    Hardcoded header list is expanded by parameters added to PlanView class in model.

    Note: if no schedule views are in a file this will report the hardcoded header only.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of headers.
    :rtype: list str
    """

    collector_views = rdb.FilteredElementCollector(doc).OfClass(rdb.ViewSchedule)
    # copy headers list
    headers = REPORT_SCHEDULES_HEADER[:]
    for v in collector_views:
        # get all parameters attached to schedules
        paras = v.GetOrderedParameters()
        for para in paras:
            headers.append(para.Definition.Name)
        break
    return headers


def get_views_report_headers(doc):
    """
    A list of headers used in report files
    Hardcoded header list is expanded by parameters added to PlanView class in model.
    Revit ui only lists 'views' 'sheets' and 'schedules' as a categories to add project parameters to.
    Therefore any parameters attached to class ViewPlan should apply to all other view types with exception of schedules and sheets.

    Note: if no plan views are in a file this will report the hardcoded header only.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of headers.
    :rtype: list str
    """

    collector_views = rdb.FilteredElementCollector(doc).OfClass(rdb.ViewPlan)
    # copy headers list
    headers = REPORT_VIEWS_HEADER[:]
    for v in collector_views:
        # get all parameters attached to views
        paras = v.GetOrderedParameters()
        for para in paras:
            headers.append(para.Definition.Name)
        break
    return headers
