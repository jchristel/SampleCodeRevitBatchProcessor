"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Revit API utility functions for the spatial properties of room elements.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

#!/usr/bin/python
# -*- coding: utf-8 -*-
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2024, Jan Christel
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

from duHast.Revit.Rooms.Objects.RoomBaseObject import RoomBaseObj
from duHast.Revit.Rooms.Objects.RoomSpatialObject import RoomSpatialObj
from Autodesk.Revit.DB import (
    Line,
    SpatialElementBoundaryLocation,
    XYZ,
)

from duHast.Utilities.unit_conversion import convert_imperial_feet_to_metric_mm
from duHast.Revit.Common.Geometry.curve import are_lines_parallel, are_lines_perpendicular

class RoomSpatialForView(RoomBaseObj):
    def __init__(
        self, rvt_doc, room, boundary_location=SpatialElementBoundaryLocation.Finish
    ):
        # initialize the base class
        super(RoomSpatialForView, self).__init__(rvt_doc, room, boundary_location=boundary_location)

        # Use the helper method to calculate spatial data
        (self.segments, self.room_walls, self.wall_segs, 
         self.bbox, self.bbox_centre) = self._calculate_spatial_data(rvt_doc, room, boundary_location)


    @staticmethod
    def _calculate_spatial_data(rvt_doc, room, boundary_location):
        """
        Helper method to compute spatial data for a room.

        This is done because I cant directly inherit from RoomSpatialObj due to exception:
        IronPython.Runtime.Exceptions.TypeErrorException: metaclass conflict: the metaclass of a derived class must be a (non-strict) subclass of the metaclasses of all its bases
        which is caused by .net metaclass conflict.

        """

        # Create a dummy room spatial object to get some spatial data
        dummy_room = RoomSpatialObj(rvt_doc, room, boundary_location=boundary_location)

        return dummy_room.segments, dummy_room.room_walls, dummy_room.wall_segs, dummy_room.bbox, dummy_room.bbox_centre
    

    def is_room_rectalinear(self):
        """
        Check if the room is rectalinear. ( all room bounding segements are either parallel or perpendicular to each other )

        :return: True if the room is rectalinear, False otherwise.
        :rtype: bool
        """

        #  IList<IList<Autodesk.Revit.DB.BoundarySegment>> segments = room.GetBoundarySegments(new SpatialElementBoundaryOptions());
        # get all room bounding segments ( this is a list of list of BoundarySegment objects )
        room_bounding_segemnts = self.segments

        # proceed only if room is bound:
        if room_bounding_segemnts is None:
            return False
        
        
        # check if all room bounding segments are either parallel or perpendicular to each other
        # if so, return True else return False

        # loop over outer loop segments only ( representing the outer room boundary and not any inner islands ) and check if parallel or perpendicular to the previous segment
        room_bounding_segemnts_outer_loop = room_bounding_segemnts[0]
        #print ("Room bounding segments loops: ", len(room_bounding_segemnts))
        #print("Room bounding segments outer loop: ", len(room_bounding_segemnts_outer_loop))
        for i in range(1, len(room_bounding_segemnts_outer_loop)):
            # get the current segment
            current_segment_curve = room_bounding_segemnts_outer_loop[i].GetCurve()
            #print("...Current segment curve: ", current_segment_curve)
            #print("...Current segment type: ", type(room_bounding_segemnts_outer_loop[i]))
            # get the previous segment
            previous_segment_curve = room_bounding_segemnts_outer_loop[i-1].GetCurve()
            #print("...Previous segment curve: ",previous_segment_curve)
            #print("...Previous segment type: ", type(room_bounding_segemnts_outer_loop[i-1]))

            # make sure both curves are lines ( no arcs or other curves )
            if (isinstance(current_segment_curve, Line) and isinstance(previous_segment_curve, Line)):
                # check if the current segment is parallel or perpendicular to the previous segment
                if(not(are_lines_parallel(current_segment_curve, previous_segment_curve) or are_lines_perpendicular(current_segment_curve, previous_segment_curve))):
                    # if not, the room is not rectalinear
                    #print("......Current segment is parallel {} \n{}{}" .format(are_lines_parallel(current_segment_curve, previous_segment_curve), current_segment_curve.Direction.Normalize(), previous_segment_curve.Direction.Normalize()))
                    #print("......Current segment is perpendicular {} \n{}" .format(are_lines_perpendicular(current_segment_curve, previous_segment_curve), current_segment_curve.Direction.Normalize().DotProduct(previous_segment_curve.Direction.Normalize())))
                    
                    print("...length of current segment: ", convert_imperial_feet_to_metric_mm(current_segment_curve.Length))
                    
                    return False
            else:
                # only lines are supported
                #print("Only lines are supported for checking if room is rectalinear")
                return False
            
        # if all segments are either parallel or perpendicular to each other, the room is rectalinear
        return True
    

    def is_room_aligned_to_its_bounding_box(self):
        """
        Check if the room is aligned to the bounding box. ( all room bounding segements are either parallel or perpendicular to the bounding box )

        :return: True if the room is aligned to the bounding box, False otherwise.
        :rtype: bool
        """

        # check if room is bound:
        if self.bbox == None:
            return False
        
        # check if room is rectalinear
        if not(self.is_room_rectalinear()):
            # check if any random room bounding segments is parallel or perpendicular to the bounding box
            return False
        

        # check if any arbritary room bounding segment is parallel or perpendicular to any bounding box edge
        if(self.segments is not None and len(self.segments) > 0):
            # get the first room bounding segment
            room_bounding_segemnts_outer_loop = self.segments[0]
            first_segment_curve = room_bounding_segemnts_outer_loop[0].GetCurve()
            # check if the first segment is parallel or perpendicular to any bounding box edge
            # get a bounding box edge from min XYZ and max XYZ
            # by using Line.CreateBound
            bbox_edge = Line.CreateBound(self.bbox.Min, XYZ(self.bbox.Max.X, self.bbox.Min.Y, self.bbox.Min.Z))
            # check if the first segment is parallel or perpendicular to the bounding box edge
            if(are_lines_parallel(first_segment_curve, bbox_edge) or are_lines_perpendicular(first_segment_curve, bbox_edge)):
                return True
            else:
                return False
        else:
            return False
