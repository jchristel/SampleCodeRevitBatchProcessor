"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to image links.
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

from duHast.Revit.Common import common as com


def get_images_types_in_model(doc):
    """
    Gets all image link types and image link instances in a model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A filtered element collector of image types.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    """

    collector = rdb.FilteredElementCollector(doc).OfClass(rdb.ImageType)
    return collector


def get_images_type_ids_in_model(doc):
    """
    Gets all image link type Ids and image link instance ids in a model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of ids representing image types and image instances.
    :rtype: list  Autodesk.Revit.DB.ElementId
    """

    ids = []
    col = get_images_types_in_model(doc)
    ids = com.get_ids_from_element_collector(col)
    return ids


def sort_image_link_types_by_import_or_linked(doc):
    """
    Returns two lists: First one: images linked into model, second one images saved into model from model itself (no external file reference)
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: Two lists of image types and instances (?)
    :rtype: list Autodesk.Revit.DB.ImageType, list Autodesk.Revit.DB.ImageType
    """

    image_link = []
    image_import = []
    collector_image_types = get_images_types_in_model(doc)
    for im in collector_image_types:
        if im.IsLoadedFromFile():
            image_link.append(im)
        else:
            image_import.append(im)
    return image_link, image_import


def get_all_image_link_type_linked_in_model(doc):
    """
    Gets all image link types which are links (external referenced) in a model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A list of image types and instances (?)
    :rtype: list Autodesk.Revit.DB.ImageType
    """

    image_links, image_import = sort_image_link_types_by_import_or_linked(doc)
    return image_links


def get_all_image_link_type_imported_in_model(doc):
    """
    Gets all image link types which are imported (not an external reference) in a model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A list of image types and instances (?)
    :rtype: list Autodesk.Revit.DB.ImageType
    """

    image_links, image_import = sort_image_link_types_by_import_or_linked(doc)
    return image_import


def get_image_types_in_model(doc):
    """
    Gets all image types in a model.
    Filters by category.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A filtered element collector of image types.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    """

    return (
        rdb.FilteredElementCollector(doc)
        .OfCategory(rdb.BuiltInCategory.OST_RasterImages)
        .WhereElementIsElementType()
    )


def get_image_instances_in_model(doc):
    """
    Gets all image instances placed in a model.
    Filters by category.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A filtered element collector of image instances.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    """

    return (
        rdb.FilteredElementCollector(doc)
        .OfCategory(rdb.BuiltInCategory.OST_RasterImages)
        .WhereElementIsNotElementType()
    )
