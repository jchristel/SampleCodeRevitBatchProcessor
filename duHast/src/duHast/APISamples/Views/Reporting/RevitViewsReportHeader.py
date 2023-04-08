'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains the header row for any Revit sheet and views reports. 
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

#: header used in views report
import Autodesk.Revit.DB as rdb

REPORT_VIEWS_HEADER = ['HOSTFILE']


#: header used in sheets report
REPORT_SHEETS_HEADER = ['HOSTFILE','Id']


def GetReportHeaders(doc):
    '''
    A list of headers used in report files
    Hardcoded header list is expanded by parameters added to sheet category in model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of headers.
    :rtype: list str
    '''

    collectorViews = rdb.FilteredElementCollector(doc).OfClass(rdb.ViewSheet)
    # copy headers list
    headers = REPORT_SHEETS_HEADER[:]
    for v in collectorViews:
        # get all parameters attached to sheet
        paras = v.GetOrderedParameters()
        for para in paras:
            headers.append (para.Definition.Name)
        break
    return headers