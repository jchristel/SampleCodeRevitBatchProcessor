"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to Revit rooms. 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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

import clr

clr.AddReference("System.Core")
from System import Linq

clr.ImportExtensions(Linq)
import System

# import Autodesk
import Autodesk.Revit.DB as rdb

# --------------------------------------------- utility functions ------------------


def get_all_rooms(doc):
    """
    Gets a list of rooms from the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: All the rooms in the model as a list.
    :rtype: List Autodesk.Revit.DB.Architecture.Room
    """

    return (
        rdb.FilteredElementCollector(doc)
        .OfCategory(rdb.BuiltInCategory.OST_Rooms)
        .ToList()
    )


def get_unplaced_rooms(doc):
    """
    Gets a list of unplaced rooms from the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: All the unplaced rooms in the model as a list.
    :rtype: List Autodesk.Revit.DB.Architecture.Room
    """

    coll = rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_Rooms)
    unplaced = []
    for r in coll:
        if r.Location == None:
            unplaced.append(r)
    return unplaced


def get_not_enclosed_rooms(doc):
    """
    Gets a list of not enclosed rooms from the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: All the unenclosed rooms in the model as a list.
    :rtype: List Autodesk.Revit.DB.Architecture.Room
    """

    coll = rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_Rooms)
    unplaced = []
    boundary_option = rdb.SpatialElementBoundaryOptions()
    for r in coll:
        boundary_segments = r.GetBoundarySegments(boundary_option)
        if (
            r.Area == 0.0
            and r.Location != None
            and (boundary_segments == None or len(boundary_segments)) == 0
        ):
            unplaced.append(r)
    return unplaced


def get_redundant_rooms(doc):
    """
    Gets a list of redundant rooms from the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: All the redundant rooms in the model as a list.
    :rtype: List Autodesk.Revit.DB.Architecture.Room
    """

    coll = rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_Rooms)
    unplaced = []
    boundary_option = rdb.SpatialElementBoundaryOptions()
    for r in coll:
        boundary_segments = r.GetBoundarySegments(boundary_option)
        if r.Area == 0.0 and (boundary_segments != None and len(boundary_segments) > 0):
            unplaced.append(r)
    return unplaced
