"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains the Revit view report functionality.
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

from duHast.Revit.Views.Reporting.views_report_header import (
    REPORT_VIEWS_HEADER,
    get_views_report_headers,
)
from duHast.Revit.Views.views import get_views_of_type
from duHast.Revit.Views.Reporting.view_property_filter import filter_data_by_properties
from duHast.Revit.Common import parameter_get_utils as rParaGet
from duHast.Utilities.Objects import result as res
from duHast.Utilities import files_csv as filesCSV
from duHast.Revit.Views.Reporting.view_property_utils import convert_view_data_to_list

#: list of view types to be reported on.
VIEW_TYPES = [
    rdb.ViewType.FloorPlan,
    rdb.ViewType.CeilingPlan,
    rdb.ViewType.Elevation,
    rdb.ViewType.ThreeD,
    rdb.ViewType.DraftingView,
    rdb.ViewType.EngineeringPlan,
    rdb.ViewType.AreaPlan,
    rdb.ViewType.Section,
    rdb.ViewType.Detail,
    rdb.ViewType.Walkthrough,
    rdb.ViewType.Rendering,
]


def get_views_report_data(doc, host_name):
    """
    Gets view data to be written to report file.
    The data returned includes all views properties available in the file.

    For View types reported on refer to VIEW_TYPES list.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param host_name: The file hostname, which is added to data returned
    :type host_name: str
    :return: list of list of view properties.
    :rtype: list of list of str
    """

    views = []
    for vt in VIEW_TYPES:
        collector_views = get_views_of_type(doc, vt)
        for v in collector_views:
            # get all parameters attached to sheet
            paras = v.GetOrderedParameters()
            data = {
                REPORT_VIEWS_HEADER[0]: host_name,
                REPORT_VIEWS_HEADER[1]: str(v.Id),
            }
            for para in paras:
                # get values as utf-8 encoded strings
                value = rParaGet.get_parameter_value_utf8_string(para)
                try:
                    data[para.Definition.Name] = value
                except:
                    data[para.Definition.Name] = "Failed to retrieve value"
            views.append(data)
    return views


def get_views_report_data_filtered(doc, host_name, view_properties):
    """
    Gets view data to be written to report file.
    The data returned is filtered by property list past in.

    For View types reported on refer to VIEW_TYPES list.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param host_name: The file hostname, which is added to data returned
    :type host_name: str
    :param view_properties: List of view properties to be extracted from views.
    :type view_properties: list of str
    :return: list of list of view properties.
    :rtype: list of list of str
    """

    data = get_views_report_data(doc, host_name)
    headers = get_views_report_headers(doc)
    views_filtered = filter_data_by_properties(
        data, headers, view_properties, REPORT_VIEWS_HEADER
    )
    return views_filtered


def write_views_data(doc, file_name, current_file_name):
    """
    Writes to file all views properties.

    file type: csv

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param file_name: The fully qualified file path of the report file.
    :type file_name: str
    :param current_file_name: The current revit file name which will be appended to data in the report.
    :type current_file_name: str
    :return:
        Result class instance.
        - .result = True if data was written successfully. Otherwise False.
        - .message will contain write status.
    :rtype: :class:`.Result`
    """

    return_value = res.Result()
    try:
        data = get_views_report_data(doc, current_file_name)
        headers = get_views_report_headers(doc)
        data_converted = convert_view_data_to_list(data, headers)
        filesCSV.write_report_data_as_csv(file_name, headers, data_converted)
        return_value.update_sep(
            True, "Successfully wrote data file at {}".format(file_name)
        )
    except Exception as e:
        return_value.update_sep(False, str(e))
    return return_value


def write_view_data_by_property_names(
    doc, file_name, current_file_name, view_properties
):
    """
    Writes to file sheet properties as nominated in past in list.

    file type: csv

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param file_name: The fully qualified file path of the report file.
    :type file_name: str
    :param current_file_name: The current Revit file name which will be appended to data in the report.
    :type current_file_name: str
    :param sheet_properties: List of sheet properties to be extracted from sheets.
    :type sheet_properties: list of str
    :return:
        Result class instance.
        - .result = True if data was written successfully. Otherwise False.
        - .message will contain write status.
    :rtype: :class:`.Result`
    """

    return_value = res.Result()
    try:
        data = get_views_report_data_filtered(doc, current_file_name, view_properties)
        # change headers to filtered + default
        headers = REPORT_VIEWS_HEADER[:] + view_properties
        data_converted = convert_view_data_to_list(data, headers)
        # write data out to file
        filesCSV.write_report_data_as_csv(file_name, headers, data_converted)
        return_value.update_sep(
            True, "Successfully wrote data file at {}".format(file_name)
        )
    except Exception as e:
        return_value.update_sep(False, str(e))
    return return_value
