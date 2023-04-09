'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A number of functions around Revit annotation objects.
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

import clr
import System

# import common library modules
from duHast.APISamples.Annotation import RevitArrowHeads as rArrow

# import Autodesk
import Autodesk.Revit.DB as rdb
import Autodesk.Revit.DB.Architecture as rdbA

# ----------------------------------------------

def GetAllAnnoSymbolTypes(doc):
    '''
    Gets all annotation symbol types, area tag types, room tag types in the model

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: list of types
    :rtype: list
    '''

    types = []
    col = rdb.FilteredElementCollector(doc).OfClass(rdb.FamilySymbol)
    for c in col:
        if (c.GetType() == rdb.AnnotationSymbolType or c.GetType == rdb.AreaTagType or c.GetType() == rdbA.RoomTagType):
            types.append(c)
    return types

def GetAnnoSymbolArrowHeadIds(doc):
    '''
    Gets all arrow head ids used in annotation symbol types, area tag types, room tag types in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of element ids representing arrow head symbols
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    usedIds = rArrow.GetArrowHeadIdsFromType(doc, GetAllAnnoSymbolTypes, rArrow.ARROWHEAD_PARAS_TEXT)
    return usedIds















