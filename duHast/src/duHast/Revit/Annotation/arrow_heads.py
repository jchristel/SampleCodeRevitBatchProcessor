"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A number of functions around Revit Arrow heads.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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


# --------------------------------------------- Arrow heads  ------------------

#: list of built in parameters attached to dimensions containing arrow head ids
import Autodesk.Revit.DB as rdb

from duHast.Revit.Common import parameter_get_utils as rParaGet

#:  list of built in parameters attached to
#:
#:    - text
#:    - independent tags
#:    - Annotation symbols
#:
#: containing arrow head ids
ARROWHEAD_PARAS_DIM = [
    rdb.BuiltInParameter.DIM_STYLE_CENTERLINE_TICK_MARK,
    rdb.BuiltInParameter.DIM_STYLE_INTERIOR_TICK_MARK,
    rdb.BuiltInParameter.DIM_STYLE_LEADER_TICK_MARK,
    rdb.BuiltInParameter.DIM_LEADER_ARROWHEAD,
    rdb.BuiltInParameter.WITNS_LINE_TICK_MARK,
]


#: parameter containing the arrowhead id in text types
ARROWHEAD_PARAS_TEXT = [rdb.BuiltInParameter.LEADER_ARROWHEAD]


#: list of built in parameters attached to spot dims containing arrow head ids
#: and symbols used
ARROWHEAD_PARAS_SPOT_DIMS = [
    rdb.BuiltInParameter.SPOT_ELEV_LEADER_ARROWHEAD,
    rdb.BuiltInParameter.SPOT_ELEV_SYMBOL,
]


#: list of built in parameters attached to stair path types containing arrow head ids
ARROWHEAD_PARAS_STAIRS_PATH = [rdb.BuiltInParameter.ARROWHEAD_TYPE]


def get_arrow_head_ids_from_type(doc, type_getter, parameter_list):
    """
    Gets all arrow head symbol ids used in dim types in a model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param type_getter: Function getting dimension types in the model.
    :type type_getter: func(doc) returns dim types.
    :param parameter_list: Names of parameters to be checked on dim types.
    :type parameter_list: list of str
    :return: List of element ids representing arrow head symbols
    :rtype: list of Autodesk.Revit.DB.ElementId
    """

    used_ids = []
    types = type_getter(doc)
    for t in types:
        for p_int in parameter_list:
            id = rParaGet.get_built_in_parameter_value(t, p_int)
            if (
                id not in used_ids
                and id != rdb.ElementId.InvalidElementId
                and id != None
            ):
                used_ids.append(id)
            break
    return used_ids


def get_arrow_types_in_model(doc):
    """
    Gets all arrow head types in the model.
    TODO: This uses a plain english name comparison to get arrow head types...may not work in non english versions of Revit!
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element types representing arrow heads.
    :rtype: list of Autodesk.Revit.DB.ElementType
    """

    types = []
    similar_types = []
    col = rdb.FilteredElementCollector(doc).OfClass(rdb.ElementType)
    for c in col:
        if c.FamilyName == "Arrowhead":
            similar_types = c.GetSimilarTypes()
            # filter out any types not in similar list...not sure what these are...
            if c.Id in similar_types:
                types.append(c)
    return types


def get_arrow_type_ids_in_model(doc):
    """
    Gets all arrow type ids in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids representing arrow types
    :rtype: list of Autodesk.Revit.DB.ElementId
    """

    arrow_types = get_arrow_types_in_model(doc)
    ids = []
    for at in arrow_types:
        if at.Id not in ids:
            ids.append(at.Id)
    return ids
