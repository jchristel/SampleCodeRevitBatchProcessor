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

from duHast.APISamples.Common import common as com
from duHast.APISamples.Links.image_links import get_image_instances_in_model, get_image_types_in_model


def get_all_unused_image_type_ids_in_model(doc):
    '''
    Gets all image types with no instances placed in a model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of ids representing image types.
    :rtype: list  Autodesk.Revit.DB.ElementId
    '''

    unused_images = com.get_not_placed_types(doc, get_image_types_in_model, get_image_instances_in_model)
    unused_type_ids = []
    for i in unused_images:
        unused_type_ids.append(i.Id)
    return unused_type_ids


def get_all_unused_image_type_ids_in_model_with_group_check(doc):
    '''
    Gets all image types with no instance placed in a model but includes group definition check.
    This only returns valid data if at least one instance of the group is placed in the model!!
    Otherwise images in groups which are not placed will not be flagged by this filter!
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of ids representing image types.
    :rtype: list  Autodesk.Revit.DB.ElementId
    '''

    unused_type_ids = get_all_unused_image_type_ids_in_model(doc)
    # and filter by any type id's in groups which may not be placed and hence no instance present in the model
    unused_type_ids = com.get_unused_type_ids_from_detail_groups(doc, unused_type_ids)
    return unused_type_ids