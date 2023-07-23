"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a Revit generic annotation utility functions. 
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

from duHast.Revit.Annotation.generic_annotation import (
    get_all_generic_annotation_types_by_category,
)


def build_generic_annotation_types_dictionary(collector, dic):
    """
    Returns the dictionary past in with keys and or values added retrieved from collector past in.
    :param collector: Filtered element collector containing GenericAnnotation type elements of family symbols.
    :type collector: Autodesk.Revit.DB.FilteredElementCollector
    :param dic: Dictionary, the key is the family name and the value a list of element ids representing annotation types.
    :type dic: dic: key str, values list of Autodesk.Revit.DB.ElementId
    :return: Past in expanded by values from collector. Dictionary the key is the Family name and the value a list of element ids.
    :rtype: dic: key str, values list of Autodesk.Revit.DB.ElementId
    """

    for c in collector:
        if dic.has_key(c.FamilyName):
            if c.Id not in dic[c.FamilyName]:
                dic[c.FamilyName].append(c.Id)
        else:
            dic[c.FamilyName] = [c.Id]
    return dic


def sort_generic_annotation_types_by_family_name(doc):
    """
    Returns the dictionary keys is autodesk.revit.db element type as string and values are elements of that type.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param collector: A filtered element collector containing elements.
    :type collector: Autodesk.Revit.DB.FilteredElementCollector

    :return: Dictionary where key is the element type as string and value is a list of all elements belonging to the element type.
    :rtype: dic{str:list[Autodesk.Revit.DB.Element]}
    """

    wts_two = get_all_generic_annotation_types_by_category(doc)
    usedWts = {}
    usedWts = build_generic_annotation_types_dictionary(wts_two, usedWts)
    return usedWts
