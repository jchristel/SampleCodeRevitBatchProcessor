'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a Revit walls utility functions. 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''
#
#License:
#
#
# Revit Batch Processor Sample Code
#
# Copyright (c) 2021  Jan Christel
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


def BuildWallTypeDictionary(collector, dic):
    '''
    Returns the dictionary past in with keys and or values added retrieved from collector past in.
    Keys are built in wall family type names.
    :param collector: A filtered element collector containing wall types.
    :type collector: Autodesk.Revit.DB.FilteredElementCollector
    :param dic: A dictionary containing key: wall type family name, value: list of ids belonging to that type.
    :type dic: dictionary (key str, value list of Autodesk.Revit.DB.ElementId)
    :return: A dictionary containing key: built in wall type family name, value: list of ids belonging to that type.
    :rtype: dictionary (key str, value list of Autodesk.Revit.DB.ElementId)
    '''

    for c in collector:
        if(dic.has_key(c.FamilyName)):
            # todo : check WallKind Enum???
            if(c.Id not in dic[c.FamilyName]):
                dic[c.FamilyName].append(c.Id)
        else:
            dic[c.FamilyName] = [c.Id]
    return dic

def GetWallTypesByClass(doc):
    '''
    This will return a filtered element collector of all wall types by class in the model
    It will therefore not return any in place wall types since revit treats those as families...
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A filtered element collector containing wall types.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    return  rdb.FilteredElementCollector(doc).OfClass(rdb.WallType)

# --------------------------------------------- utility functions ------------------

def GetAllWallTypes(doc):
    '''
    Gets all wall types in a model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A filtered element collector containing wall types.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    collector = rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_Walls).WhereElementIsElementType()
    return collector

def SortWallTypesByFamilyName(doc):
    '''
    Returns a dictionary of all wall types in the model where key is the build in wall family name, values are ids of associated wall types.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A dictionary containing key: built in wall type family name, value: list of ids belonging to that type.
    :rtype: dictionary (key str, value list of Autodesk.Revit.DB.ElementId)
    '''

    # get all Wall Type Elements
    wts = GetWallTypesByClass(doc)
    # get all wall types including in place wall families
    wts_two = GetAllWallTypes(doc)
    usedWts = {}
    usedWts = BuildWallTypeDictionary(wts, usedWts)
    usedWts = BuildWallTypeDictionary(wts_two, usedWts)
    return usedWts