'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to stair path annotation. 
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
import Autodesk.Revit.DB.Architecture as rdbA

from duHast.APISamples.Annotation import RevitArrowHeads as rArrow


def get_all_stair_path_types(doc):
    '''
    Gets all stairs path types in the model/
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A filtered element collector of stair path types
    :rtype: Autodesk.Revit.DB.FilteredElementCollector of stair path types
    '''

    return rdb.FilteredElementCollector(doc).OfClass(rdbA.StairsPathType)

def get_stairs_path_arrow_head_ids(doc):
    '''
    Gets all arrow head symbol ids used in stairs path types in a model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids representing arrow head symbols
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    usedIds = rArrow.get_arrow_head_ids_from_type(doc, get_all_stair_path_types, rArrow.ARROWHEAD_PARAS_STAIRS_PATH)
    return usedIds