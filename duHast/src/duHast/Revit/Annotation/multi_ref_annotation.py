'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to multi reference annotation. 
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
from duHast.APISamples.Common import common as com


def get_all_multi_ref_annotation_types(doc):
    '''
    Gets all multi reference annotation types in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A filtered element collector of MultiReferenceAnnotationType
    :rtype: Autodesk.Revit.DB.FilteredElementCollector of MultiReferenceAnnotationType
    '''

    return rdb.FilteredElementCollector(doc).OfClass(rdb.MultiReferenceAnnotationType)

def get_all_multi_ref_annotation_type_ids(doc):
    '''
    Gets all multi reference annotation type ids in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids representing multi reference Annotation Types
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    ids = []
    col = rdb.FilteredElementCollector(doc).OfClass(rdb.MultiReferenceAnnotationType)
    ids = com.get_ids_from_element_collector(col)
    return ids


def get_all_multi_ref_annotation_elements(doc):
    '''
    Gets all multi reference annotation elements in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A filtered element collector of MultiReferenceAnnotation
    :rtype: Autodesk.Revit.DB.FilteredElementCollector of MultiReferenceAnnotation
    '''

    return rdb.FilteredElementCollector(doc).OfClass(rdb.MultiReferenceAnnotation)

def get_all_similar_multi_reference_anno_types(doc):
    '''
    Gets all multi reference annotation types using get similar types in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: list in format [[multi refType, [element ids of similar multi ref types, ...]]]
    :rtype: List [[Autodesk.Revit.DB.ElementType, Autodesk.Revit.DB.ElementId, Autodesk.Revit.DB.ElementId,...],]
    '''

    multi_reference_anno_types = com.get_similar_type_families_by_type(doc, get_all_multi_ref_annotation_types)
    return multi_reference_anno_types