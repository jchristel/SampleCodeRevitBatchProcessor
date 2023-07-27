"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to Revit walls. 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
#
# License:
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

def get_walls_from_boundary_segments(rvt_doc, bnd_seg_list):
    '''
    Get a flat list of walls from a list of room boundary segments.
    :param rvt_doc: Revit document
    :type rvt_doc: Autodesk.Revit.DB.Document
    :param bnd_seg_list: List of room boundary segments
    :type bnd_seg_list: list
    :return: List of wall elements
    :rtype: list
    '''
    wall_list = []
    #loop over all the segments that make up the room boundary	
    for segment_collection in bnd_seg_list:
        for seg in segment_collection:
            #all the wall elements belonging to a room
            try:
                wall = rvt_doc.GetElement(seg.ElementId)
                wall_list.append(wall)
            except:
                pass
    
    return wall_list