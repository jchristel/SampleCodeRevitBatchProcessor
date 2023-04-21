'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A number of functions around Revit Arrow heads.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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
    rdb.BuiltInParameter.WITNS_LINE_TICK_MARK
]


#: parameter containing the arrowhead id in text types
ARROWHEAD_PARAS_TEXT = [
    rdb.BuiltInParameter.LEADER_ARROWHEAD
]


#: list of built in parameters attached to spot dims containing arrow head ids
#: and symbols used
ARROWHEAD_PARAS_SPOT_DIMS = [
    rdb.BuiltInParameter.SPOT_ELEV_LEADER_ARROWHEAD,
    rdb.BuiltInParameter.SPOT_ELEV_SYMBOL
]


#: list of built in parameters attached to stair path types containing arrow head ids
ARROWHEAD_PARAS_STAIRS_PATH = [
    rdb.BuiltInParameter.ARROWHEAD_TYPE
]


def get_arrow_head_ids_from_type(doc, type_getter, parameter_list):
    '''
    Gets all arrow head symbol ids used in dim types in a model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param type_getter: Function getting dimension types in the model.
    :type type_getter: func(doc) returns dim types.
    :param parameter_list: Names of parameters to be checked on dim types.
    :type parameter_list: list of str
    :return: List of element ids representing arrow head symbols
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    used_ids = []
    types = type_getter(doc)
    for t in types:
        for p_int in parameter_list:
            id = rParaGet.get_built_in_parameter_value(t, p_int)
            if(id not in used_ids and id != rdb.ElementId.InvalidElementId and id != None):
                used_ids.append(id)
            break
    return used_ids


def get_arrow_types_in_model(doc):
    '''
    Gets all arrow head types in the model.
    TODO: This uses a plain english name comparison to get arrow head types...may not work in non english versions of Revit!
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element types representing arrow heads.
    :rtype: list of Autodesk.Revit.DB.ElementType
    '''

    types = []
    similar_types = []
    col = rdb.FilteredElementCollector(doc).OfClass(rdb.ElementType)
    for c in col:
        if (c.FamilyName == 'Arrowhead'):
            similar_types = c.GetSimilarTypes()
            # filter out any types not in similar list...not sure what these are...
            if(c.Id in similar_types):
                types.append(c)
    return types


def get_arrow_type_ids_in_model(doc):
    '''
    Gets all arrow type ids in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids representing arrow types
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    arrow_types = get_arrow_types_in_model(doc)
    ids = []
    for at in arrow_types:
            if(at.Id not in ids):
                ids.append(at.Id)
    return ids