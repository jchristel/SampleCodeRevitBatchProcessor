'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains the Revit view report functionality.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''
#
#License:
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

from duHast.APISamples.Views.Reporting.RevitViewsReportHeader import REPORT_SHEETS_HEADER, get_report_headers
from duHast.APISamples.Common import RevitElementParameterGetUtils as rParaGet
from duHast.Utilities import Result as res, FilesTab as filesTab


def get_sheet_report_data(doc, hostName):
    '''
    Gets sheet data to be written to report file.
    The data returned includes all sheet properties available in the file.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param hostName: The file hostname, which is added to data returned
    :type hostName: str
    :return: list of list of sheet properties.
    :rtype: list of list of str
    '''

    collectorViews = rdb.FilteredElementCollector(doc).OfClass(rdb.ViewSheet)
    views = []
    for v in collectorViews:
        # get all parameters attached to sheet
        paras = v.GetOrderedParameters()
        data = [hostName, str(v.Id)]
        for para in paras:
            # get values as utf-8 encoded strings
            value = rParaGet.get_parameter_value_utf8_string (para)
            try:
                data.append (value)
            except:
                data.append('Failed to retrieve value')
        views.append(data)
    return views


def write_sheet_data(doc, fileName, currentFileName):
    '''
    Writes to file all sheet properties.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param fileName: The fully qualified file path of the report file.
    :type fileName: str
    :param currentFileName: The current revit file name which will be appended to data in the report.
    :type currentFileName: str
    :return: 
        Result class instance.
        - .result = True if data was written successfully. Otherwise False.
        - .message will contain write status.
    :rtype: :class:`.Result`
    '''

    returnValue = res.Result()
    try:
        data = get_sheet_report_data(doc, currentFileName)
        headers = get_report_headers(doc)
        filesTab.write_report_data(
            fileName,
            headers,
            data)
        returnValue.update_sep(True, 'Successfully wrote data file')
    except Exception as e:
        returnValue.update_sep(False, str(e))
    return returnValue


def filter_data_by_properties(data, headers, sheetProperties):
    '''
    Filters sheet data by supplied property names.
    Data gets filtered twice: property needs to exist in headers list as well as in sheet properties list.
    :param data: List of sheet properties to be kept.
    :type data: list of list of str
    :param headers: Filter: list of headers representing property names.
    :type headers: list of str
    :param sheetProperties: list of sheet properties to be extracted from data
    :type sheetProperties: list of str
    :return: List of sheet properties matching filters.
    :rtype: list of list of str
    '''

    # add default headers to properties to be filtered first
    dataIndexList= [iter for iter in range(len(REPORT_SHEETS_HEADER))]
    # build index pointer list of data to be kept
    for f in sheetProperties:
        if (f in headers):
            dataIndexList.append(headers.index(f))
    # filter data out
    newData = []
    for d in data:
        dataRow = []
        for i in dataIndexList:
            dataRow.append(d[i])
        newData.append(dataRow)
    return newData


def write_sheet_data_by_property_names(doc, fileName, currentFileName, sheetProperties):
    '''
    Writes to file sheet properties as nominated in past in list.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param fileName: The fully qualified file path of the report file.
    :type fileName: str
    :param currentFileName: The current Revit file name which will be appended to data in the report.
    :type currentFileName: str
    :param sheetProperties: List of sheet properties to be extracted from sheets.
    :type sheetProperties: list of str
    :return: 
        Result class instance.
        - .result = True if data was written successfully. Otherwise False.
        - .message will contain write status.
    :rtype: :class:`.Result`
    '''

    returnValue = res.Result()
    try:
        data = get_sheet_report_data(doc, currentFileName)
        headers = get_report_headers(doc)
        data = filter_data_by_properties(data, headers, sheetProperties)
        # change headers to filtered + default
        headers = REPORT_SHEETS_HEADER[:]
        headers = headers + sheetProperties
        # write data out to file
        filesTab.write_report_data(
            fileName,
            headers,
            data)
        returnValue.update_sep(True, 'Successfully wrote data file')
    except Exception as e:
        returnValue.update_sep(False, str(e))
    return returnValue