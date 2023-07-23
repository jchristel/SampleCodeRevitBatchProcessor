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
