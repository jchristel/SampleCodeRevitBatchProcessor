'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains utility function(s) for grid reports. 
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
from duHast.APISamples.Common import RevitWorksets as rWork
from duHast.Utilities import Utility as util, FilesIO as fileIO
from duHast.APISamples.Grids import RevitGrids as rGrid


def get_grid_report_data(doc, revit_file_path):
    '''
    Gets grid data ready for being printed to file
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param revit_file_path: fully qualified file path of Revit file
    :type revit_file_path: str
    :return: list of list of revit grid properties.
    :rtype: [[str]]
    '''

    data = []
    for p in rdb.FilteredElementCollector(doc).OfClass(rdb.Grid):
        data.append([
            fileIO.get_file_name_without_ext(revit_file_path),
            str(p.Id.IntegerValue),
            util.encode_ascii (p.Name),
            rWork.get_workset_name_by_id(doc, p.WorksetId.IntegerValue),
            rGrid.get_max_extent_as_string(p)])
    return data