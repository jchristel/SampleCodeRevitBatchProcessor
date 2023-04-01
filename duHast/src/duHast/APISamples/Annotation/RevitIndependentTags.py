'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A number of functions around Revit independent tags.
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


import Autodesk.Revit.DB as rdb

from duHast.APISamples.Common import RevitElementParameterGetUtils as rParaGet


def GetAllIndependentTags(doc):
    '''
    Gets all independent tag types in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A filtered element collector of independent tag elements
    :rtype: Autodesk.Revit.DB.FilteredElementCollector of independent tag elements
    '''

    return rdb.FilteredElementCollector(doc).OfClass(rdb.IndependentTag)

def GetIndependentTagTypeArrowHeadIds(doc):
    '''
    Gets all arrow head symbol ids used in independent tag types in a model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids representing arrow head symbols
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    usedIds = []
    tags = GetAllIndependentTags(doc)
    for t in tags:
        tTypeId = t.GetTypeId()
        tTypeElement = doc.GetElement(tTypeId)
        id = rParaGet.get_built_in_parameter_value(tTypeElement, rdb.BuiltInParameter.LEADER_ARROWHEAD)
        if(id not in usedIds and id != rdb.ElementId.InvalidElementId and id != None):
            usedIds.append(id)
    return usedIds