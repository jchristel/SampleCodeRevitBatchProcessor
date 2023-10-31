"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Revit fill patterns helper functions. 
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

from Autodesk.Revit.DB import FilteredElementCollector, FillPatternElement


def get_all_fill_pattern(doc):
    """
    Gets all fill pattern elements in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A filtered element collector of all fill pattern elements.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    """

    return FilteredElementCollector(doc).OfClass(FillPatternElement)


def pattern_ids_by_name(doc):
    """
    Returns a dictionary where fill pattern name is key, values are all ids of line patterns with the exact same name.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A dictionary where fill pattern name is key, values are all ids of line patterns with the exact same name
    :rtype: dictionary(key str, value list of Autodesk.Revit.DB.ElementId)
    """

    pattern_dic = {}
    all_fill_pattern = get_all_fill_pattern(doc=doc)
    for fill_pattern in all_fill_pattern:
        pattern_name = fill_pattern.GetFillPattern().Name
        if pattern_name in pattern_dic:
            pattern_dic[pattern_name].append(fill_pattern.Id)
        else:
            pattern_dic[pattern_name] = [fill_pattern.Id]
    return pattern_dic
