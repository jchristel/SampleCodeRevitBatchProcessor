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
from duHast.Revit.Common import parameter_get_utils as rParaGet
from duHast.Revit.Common.revit_version import get_revit_version_number

def get_all_independent_tags(doc):
    """
    Gets all independent tag types in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A filtered element collector of independent tag elements
    :rtype: Autodesk.Revit.DB.FilteredElementCollector of independent tag elements
    """

    return rdb.FilteredElementCollector(doc).OfClass(rdb.IndependentTag)


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
        id = rParaGet.get_built_in_parameter_value(
            t_type_element, rdb.BuiltInParameter.LEADER_ARROWHEAD
        )
        if id not in used_ids and id != rdb.ElementId.InvalidElementId and id != None:
            used_ids.append(id)
    return used_ids