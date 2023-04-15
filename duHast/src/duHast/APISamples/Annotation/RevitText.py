'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to text. 
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
from duHast.APISamples.Annotation import RevitArrowHeads as rArrow


def get_all_text_types(doc):
    '''
    Gets all text types in the model
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A filtered element collector of text element types
    :rtype: Autodesk.Revit.DB.FilteredElementCollector of text element types
    '''

    return rdb.FilteredElementCollector(doc).OfClass(rdb.TextElementType)

def get_all_text_type_ids(doc):
    '''
    Gets all text type ids in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids representing text types
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    ids = []
    col = rdb.FilteredElementCollector(doc).OfClass(rdb.TextElementType)
    ids = com.get_ids_from_element_collector(col)
    return ids


def get_all_text_annotation_elements(doc):
    '''
    Gets all text annotation elements in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A filtered element collector of text elements
    :rtype: Autodesk.Revit.DB.FilteredElementCollector of text elements
    '''

    return rdb.FilteredElementCollector(doc).OfClass(rdb.TextElement)

def get_text_type_arrow_head_ids(doc):
    '''
    Gets all arrow head ids used in text types in a model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids representing arrow head symbols
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''
    usedIds = rArrow.get_arrow_head_ids_from_type(doc, get_all_text_types, rArrow.ARROWHEAD_PARAS_TEXT)
    return usedIds