'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to Revit rooms. 
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

clr.AddReference("System.Core")
from System import Linq
clr.ImportExtensions(Linq)
import System

# import Autodesk
import Autodesk.Revit.DB as rdb

# --------------------------------------------- utility functions ------------------

def get_all_rooms(doc):
    '''
    Gets a list of rooms from the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: All the rooms in the model as a list.
    :rtype: List Autodesk.Revit.DB.Architecture.Room
    '''

    return rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_Rooms).ToList()

def get_unplaced_rooms(doc):
    '''
    Gets a list of unplaced rooms from the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: All the unplaced rooms in the model as a list.
    :rtype: List Autodesk.Revit.DB.Architecture.Room
    '''

    coll = rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_Rooms)
    unplaced = []
    for r in coll:
        if(r.Location == None):
            unplaced.append(r)
    return unplaced

def get_not_enclosed_rooms(doc):
    '''
    Gets a list of not enclosed rooms from the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: All the unenclosed rooms in the model as a list.
    :rtype: List Autodesk.Revit.DB.Architecture.Room
    '''

    coll = rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_Rooms)
    unplaced = []
    boundaryOption = rdb.SpatialElementBoundaryOptions()
    for r in coll:
        boundarySegments = r.GetBoundarySegments(boundaryOption)
        if(r.Area == 0.0 and r.Location != None and (boundarySegments == None or len(boundarySegments)) == 0):
            unplaced.append(r)
    return unplaced

def get_redundant_rooms(doc):
    '''
    Gets a list of redundant rooms from the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: All the redundant rooms in the model as a list.
    :rtype: List Autodesk.Revit.DB.Architecture.Room
    '''

    coll = rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_Rooms)
    unplaced = []
    boundaryOption = rdb.SpatialElementBoundaryOptions()
    for r in coll:
        boundarySegments = r.GetBoundarySegments(boundaryOption)
        if(r.Area == 0.0 and(boundarySegments != None and len(boundarySegments) > 0)):
            unplaced.append(r)
    return unplaced