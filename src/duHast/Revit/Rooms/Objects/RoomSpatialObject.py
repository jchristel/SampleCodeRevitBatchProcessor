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

from Autodesk.Revit.DB import (
    SpatialElementBoundaryOptions,
    SpatialElementBoundaryLocation,
    XYZ,
)
from duHast.Revit.Rooms.Objects.RoomBaseObject import RoomBaseObj
from duHast.Revit.Rooms.Geometry.room_spatial_elements import (
    get_room_segments,
    get_only_wall_segments_as_walls,
    get_only_wall_segments_as_curves,
)


class RoomSpatialObj(RoomBaseObj):
    def __init__(
        self, rvt_doc, room, boundary_location=SpatialElementBoundaryLocation.Finish
    ):
        super(RoomSpatialObj, self).__init__(rvt_doc, room)
        RoomBaseObj.__init__(self, rvt_doc, room)
        spat_opts = SpatialElementBoundaryOptions()
        spat_opts.SpatialElementBoundaryLocation = boundary_location
        self.segments = get_room_segments(room, spat_opts)
        self.room_walls = get_only_wall_segments_as_walls(rvt_doc, self.segments)
        self.wall_segs = get_only_wall_segments_as_curves(rvt_doc, self.segments)

        self.bbox = None
        # get the room bounding box
        if room.Location is not None:
            self.bbox = room.get_BoundingBox(None)
        
        # get the room bounding box centre
        self.bbox_centre = None
        if self.bbox:
            centre_x = self.bbox.Min.X + ((self.bbox.Max.X - self.bbox.Min.X) / 2)
            centre_y = self.bbox.Min.Y + ((self.bbox.Max.Y - self.bbox.Min.Y) / 2)
            centre_z = self.bbox.Min.Z

            self.bbox_centre = XYZ(centre_x, centre_y, centre_z)



