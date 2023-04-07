'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Revit materials helper functions.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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

# import Autodesk
import Autodesk.Revit.DB as rdb

# --------------------------------------------- utility functions ------------------

def GetAllMaterials(doc): 
    '''
    Gets all materials in a model.

    Filter by class.

    :param doc: _description_
    :type doc: _type_

    :return: A filtered element collector of materials
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    collector = rdb.FilteredElementCollector(doc).OfClass(rdb.Material)
    return collector

def GetMaterialById(doc, id):
    '''
    Gets a material element based on a material id.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param id: The id of material to be returned.
    :type id: Autodesk.Revit.DB.ElementId

    :return: A material if matching id was found. Otherwise nothing gets returned!
    :rtype: Autodesk.Revit.DB.Material
    '''

    mats = GetAllMaterials(doc)
    for m in mats:
        if m.Id.IntegerValue == id.IntegerValue:
            return m

def GetMaterialNameById(doc, id):
    '''
    Gets a material name based on a material id.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param id: Id of material of which the name is to be returned.
    :type id: Autodesk.Revit.DB.ElementId

    :return: The material name if matching id was found or the default value: '<By Category>'
    :rtype: str
    '''

    name = '<By Category>'
    mats = GetAllMaterials(doc)
    for m in mats:
        if m.Id.IntegerValue == id.IntegerValue:
            mName = rdb.Element.Name.GetValue(m)
            name = '' if mName == None else mName
    return name