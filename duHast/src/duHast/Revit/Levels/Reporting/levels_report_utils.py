'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains utility function(s) for level reports. 
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

from duHast.Revit.Common import worksets as rWork
from duHast.Utilities import utility as util
from duHast.Utilities.unit_conversion import convert_imperial_feet_to_metric_mm


def get_level_report_data(doc, revitFilePath):
    '''
    Gets level data ready for being printed to file.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param revitFilePath: The file hostname, which is added to data returned.
    :type revitFilePath: str
    :return: list of list of revit level properties.
    :rtype: list of list of str
    '''

    data = []
    for p in rdb.FilteredElementCollector(doc).OfClass(rdb.Level):
        data.append([
            revitFilePath,
            str(p.Id.IntegerValue),
            util.encode_ascii(p.Name),
            util.encode_ascii(rWork.get_workset_name_by_id(doc, p.WorksetId.IntegerValue)),
            str(convert_imperial_feet_to_metric_mm(p.Elevation))])
    return data