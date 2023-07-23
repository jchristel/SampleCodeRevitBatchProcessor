"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains the Revit sheet report functionality.
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

import Autodesk.Revit.DB as rdb

from duHast.Revit.Views.Reporting.views_report_header import (
    REPORT_SHEETS_HEADER,
    get_sheets_report_headers,
)
from duHast.Revit.Views.Reporting.view_property_filter import filter_data_by_properties
from duHast.Revit.Common import parameter_get_utils as rParaGet
from duHast.Utilities.Objects import result as res
from duHast.Revit.Views.Reporting.view_property_utils import convert_view_data_to_list
from duHast.Utilities.files_csv import write_report_data_as_csv


def get_sheet_report_data(doc, host_name):
    """
    Gets sheet data to be written to report file.
    The data returned includes all sheet properties available in the file.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param host_name: The file hostname, which is added to data returned
    :type host_name: str
    :return: list of list of sheet properties.
    :rtype: list of list of str
    """

    collector_views = rdb.FilteredElementCollector(doc).OfClass(rdb.ViewSheet)
    views = []
    for v in collector_views:
        # get all parameters attached to sheet
        paras = v.GetOrderedParameters()
        data = {
            REPORT_SHEETS_HEADER[0]: host_name,
            REPORT_SHEETS_HEADER[1]: str(v.Id),
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


def get_sheets_report_data_filtered(doc, host_name, sheet_properties):
    """
    Gets sheet data to be written to report file.
    The data returned is filtered by property list past in.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param host_name: The file hostname, which is added to data returned
    :type host_name: str
    :param view_properties: List of view properties to be extracted from sheets.
    :type view_properties: list of str
    :return: list of list of view properties.
    :rtype: list of list of str
    """

    data = get_sheet_report_data(doc, host_name)
    headers = get_sheets_report_headers(doc)
    sheets_filtered = filter_data_by_properties(
        data, headers, sheet_properties, REPORT_SHEETS_HEADER
    )
    return sheets_filtered


def write_sheet_data(doc, file_name, current_file_name):
    """
    Writes to file all sheet properties.

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
        data = get_sheet_report_data(doc, current_file_name)
        headers = get_sheets_report_headers(doc)
        data_converted = convert_view_data_to_list(data, headers)
        write_report_data_as_csv(file_name, headers, data_converted)
        return_value.update_sep(True, "Successfully wrote data file")
    except Exception as e:
        return_value.update_sep(False, str(e))
    return return_value


def write_sheet_data_by_property_names(
    doc, file_name, current_file_name, sheet_properties
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
        data = get_sheets_report_data_filtered(doc, current_file_name, sheet_properties)
        # change headers to filtered + default
        headers = REPORT_SHEETS_HEADER[:] + sheet_properties
        data_converted = convert_view_data_to_list(data, headers)
        # write data out to file
        write_report_data_as_csv(file_name, headers, data_converted)
        return_value.update_sep(True, "Successfully wrote data file")
    except Exception as e:
        return_value.update_sep(False, str(e))
    return return_value
