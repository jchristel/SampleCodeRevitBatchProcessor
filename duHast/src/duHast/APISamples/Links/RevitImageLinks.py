'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to image links.
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

from duHast.APISamples.Common import RevitCommonAPI as com


def GetImagesTypesInModel(doc):
    '''
    Gets all image link types and image link instances in a model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A filtered element collector of image types.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    collector = rdb.FilteredElementCollector(doc).OfClass(rdb.ImageType)
    return collector


def GetImagesTypeIdsInModel(doc):
    '''
    Gets all image link type Ids and image link instance ids in a model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of ids representing image types and image instances.
    :rtype: list  Autodesk.Revit.DB.ElementId
    '''

    ids = []
    col = GetImagesTypesInModel(doc)
    ids = com.get_ids_from_element_collector(col)
    return ids


def SortImageLinkTypesByImportOrLinked(doc):
    '''
    Returns two lists: First one: images linked into model, second one images saved into model from model itself (no external file reference)
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: Two lists of image types and instances (?)
    :rtype: list Autodesk.Revit.DB.ImageType, list Autodesk.Revit.DB.ImageType 
    '''

    imageLink = []
    imageImport = []
    collectorImageTypes = GetImagesTypesInModel(doc)
    for im in collectorImageTypes:
        if(im.IsLoadedFromFile()):
            imageLink.append(im)
        else:
            imageImport.append(im)
    return imageLink, imageImport


def GetAllImageLinkTypeLinkedInModel(doc):
    '''
    Gets all image link types which are links (external referenced) in a model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A list of image types and instances (?)
    :rtype: list Autodesk.Revit.DB.ImageType
    '''

    imageLinks, imageImport = SortImageLinkTypesByImportOrLinked(doc)
    return imageLinks


def GetAllImageLinkTypeImportedInModel(doc):
    '''
    Gets all image link types which are imported (not an external reference) in a model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A list of image types and instances (?)
    :rtype: list Autodesk.Revit.DB.ImageType
    '''

    imageLinks, imageImport = SortImageLinkTypesByImportOrLinked(doc)
    return imageImport


def GetImageTypeInModel(doc):
    '''
    Gets all image types in a model.
    Filters by category.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A filtered element collector of image types.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    return rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_RasterImages).WhereElementIsElementType()

def GetImageInstancesInModel(doc):
    '''
    Gets all image instances placed in a model.
    Filters by category.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A filtered element collector of image instances.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    return rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_RasterImages).WhereElementIsNotElementType()