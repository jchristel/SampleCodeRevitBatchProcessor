"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a Revit detail items utility functions. 
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


def build_detail_type_ids_dictionary(collector):
    """
    Returns the dictionary keys is autodesk.revit.db element type as string and values are available type ids.

    :param collector: A filtered element collector containing detail component types.
    :type collector: Autodesk.Revit.DB.FilteredElementCollector

    :return: Dictionary where key is the element type as string and value is a list of all type ids belonging to the element type.
    :rtype: dic{str:list[Autodesk.Revit.DB.ElementId]}
    """

    dic = {}
    for c in collector:
        if str(c.GetType()) in dic:
            if c.Id not in dic[str(c.GetType())]:
                dic[str(c.GetType())].append(c.Id)
        else:
            dic[str(c.GetType())] = [c.Id]
    return dic


def build_dependent_elements_dictionary(doc, collector):
    """
    Returns the dictionary keys is autodesk.revit.db element type as string and values are elements of that type.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param collector: A filtered element collector containing elements.
    :type collector: Autodesk.Revit.DB.FilteredElementCollector

    :return: Dictionary where key is the element type as string and value is a list of all elements belonging to the element type.
    :rtype: dic{str:list[Autodesk.Revit.DB.Element]}
    """

    dic = {}
    for c in collector:
        el = doc.GetElement(c)
        if str(el.GetType()) in dic:
            if c not in dic[str(el.GetType())]:
                dic[str(el.GetType())].append(c)
        else:
            dic[str(el.GetType())] = [c]
    return dic
