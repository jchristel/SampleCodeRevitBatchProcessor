'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains utility function(s) for workset reports. 
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

from duHast.Utilities import Utility as util
from duHast.APISamples.Common.RevitWorksets import GetWorksetsFromCollector


def GetWorksetReportData(doc, revitFilePath):
    '''
    Gets workset data ready for being written to file.
    - HOSTFILE
    - ID
    - NAME
    - ISVISIBLEBYDEFAULT
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param revitFilePath: The fully qualified file path of Revit file.
    :type revitFilePath: str
    :return: The workset data in a nested list of string
    :rtype: list of list of str
    '''

    data = []
    worksets = GetWorksetsFromCollector(doc)
    for ws in worksets:
        data.append([
            revitFilePath,
            str(ws.Id.IntegerValue),
            util.EncodeAscii(ws.Name),
            str(ws.IsVisibleByDefault)])
    return data