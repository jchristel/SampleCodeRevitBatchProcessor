"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to multi reference annotation. 
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


def get_all_multi_ref_annotation_types(doc):
    """
    Gets all multi reference annotation types in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A filtered element collector of MultiReferenceAnnotationType
    :rtype: Autodesk.Revit.DB.FilteredElementCollector of MultiReferenceAnnotationType
    """

    return rdb.FilteredElementCollector(doc).OfClass(rdb.MultiReferenceAnnotationType)


def get_all_multi_ref_annotation_type_ids(doc):
    """
    Gets all multi reference annotation type ids in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids representing multi reference Annotation Types
    :rtype: list of Autodesk.Revit.DB.ElementId
    """

    ids = []
    col = rdb.FilteredElementCollector(doc).OfClass(rdb.MultiReferenceAnnotationType)
    ids = com.get_ids_from_element_collector(col)
    return ids


def get_all_multi_ref_annotation_elements(doc):
    """
    Gets all multi reference annotation elements in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A filtered element collector of MultiReferenceAnnotation
    :rtype: Autodesk.Revit.DB.FilteredElementCollector of MultiReferenceAnnotation
    """

    return rdb.FilteredElementCollector(doc).OfClass(rdb.MultiReferenceAnnotation)


def get_all_similar_multi_reference_anno_types(doc):
    """
    Gets all multi reference annotation types using get similar types in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: list in format [[multi refType, [element ids of similar multi ref types, ...]]]
    :rtype: List [[Autodesk.Revit.DB.ElementType, Autodesk.Revit.DB.ElementId, Autodesk.Revit.DB.ElementId,...],]
    """

    multi_reference_anno_types = com.get_similar_type_families_by_type(
        doc, get_all_multi_ref_annotation_types
    )
    return multi_reference_anno_types
