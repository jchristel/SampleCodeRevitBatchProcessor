"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a Revit railings utility functions. 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2023, Jan Christel
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

from duHast.Revit.Railings.railings import (
    get_all_railing_types_by_category,
    get_railing_types_by_class,
)


def build_railing_type_dictionary(collector, dic):
    """
    Returns the dictionary past in with keys and or values added retrieved from collector past in.
    TODO: similar function exists in Walls module. Consider more generic function.
    :param collector: A filtered element collector containing railing type elements of family symbols
    :type collector: Autodesk.Revit.DB.FilteredElementCollector
    :param dic: dictionary containing key: railing type family name, value: list of ids
    :type dic: Dictionary {str:[Autodesk.Revit.DB.ElementId]}
    :return: A dictionary where key is the family name and values are ids of types belonging to that family.
    :rtype: Dictionary {str:[Autodesk.Revit.DB.ElementId]}
    """

    for c in collector:
        if dic.has_key(c.FamilyName):
            if c.Id not in dic[c.FamilyName]:
                dic[c.FamilyName].append(c.Id)
        else:
            dic[c.FamilyName] = [c.Id]
    return dic


def sort_railing_types_by_family_name(doc):
    """
    Returns a dictionary where key is the family name and values are ids of types belonging to that family.
    TODO: similar function exists in Walls module. Consider more generic function.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A dictionary where key is the family name and values are ids of types belonging to that family.
    :rtype: Dictionary {str:[Autodesk.Revit.DB.ElementId]}
    """

    # get all Railing Type Elements
    wts = get_railing_types_by_class(doc)
    # get all Railing types including in place railing families
    wts_two = get_all_railing_types_by_category(doc)
    used_wts = {}
    used_wts = build_railing_type_dictionary(wts, used_wts)
    used_wts = build_railing_type_dictionary(wts_two, used_wts)
    return used_wts
