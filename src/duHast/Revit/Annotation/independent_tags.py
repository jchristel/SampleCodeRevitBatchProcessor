"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A number of functions around Revit independent tags.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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


from Autodesk.Revit.DB import (
    BuiltInParameter,
    ElementId,
    FilteredElementCollector,
    IndependentTag,
)
from duHast.Revit.Common.parameter_get_utils import (
    get_built_in_parameter_value,
    get_parameter_value_as_element_id,
)

# from duHast.Revit.Common.revit_version import get_revit_version_number


def get_all_independent_tags(doc):
    """
    Gets all independent tag instances in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A filtered element collector of independent tag elements
    :rtype: Autodesk.Revit.DB.FilteredElementCollector of independent tag elements
    """

    return FilteredElementCollector(doc).OfClass(IndependentTag)


def get_independent_tag_type_arrow_head_ids(doc):
    """
    Gets all arrow head symbol ids used in independent tag types in a model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids representing arrow head symbols
    :rtype: list of Autodesk.Revit.DB.ElementId
    """

    used_ids = []
    tags = get_all_independent_tags(doc)
    for t in tags:
        t_type_id = t.GetTypeId()
        t_type_element = doc.GetElement(t_type_id)
        id = get_built_in_parameter_value(
            t_type_element,
            BuiltInParameter.LEADER_ARROWHEAD,
            get_parameter_value_as_element_id,
        )
        if id not in used_ids and id != ElementId.InvalidElementId and id != None:
            used_ids.append(id)
    return used_ids
