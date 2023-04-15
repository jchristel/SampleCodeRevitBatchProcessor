'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to purging unused image links.
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

from duHast.APISamples.Common import RevitCommonAPI as com
from duHast.APISamples.Links.RevitImageLinks import GetImageInstancesInModel, GetImageTypeInModel


def GetAllUnusedImageTypeIdsInModel(doc):
    '''
    Gets all image types with no instances placed in a model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of ids representing image types.
    :rtype: list  Autodesk.Revit.DB.ElementId
    '''

    unusedImages = com.get_not_placed_types(doc, GetImageTypeInModel, GetImageInstancesInModel)
    unusedTypeIds = []
    for i in unusedImages:
        unusedTypeIds.append(i.Id)
    return unusedTypeIds


def GetAllUnusedImageTypeIdsInModelWithGroupCheck(doc):
    '''
    Gets all image types with no instance placed in a model but includes group definition check.
    This only returns valid data if at least one instance of the group is placed in the model!!
    Otherwise images in groups which are not placed will not be flagged by this filter!
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of ids representing image types.
    :rtype: list  Autodesk.Revit.DB.ElementId
    '''

    unusedTypeIds = GetAllUnusedImageTypeIdsInModel(doc)
    # and filter by any type id's in groups which may not be placed and hence no instance present in the model
    unusedTypeIds = com.get_unused_type_ids_from_detail_groups(doc, unusedTypeIds)
    return unusedTypeIds