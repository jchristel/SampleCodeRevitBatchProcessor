"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Helper functions to create room tags.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

#
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
#

from duHast.Utilities.Objects.result import Result

from Autodesk.Revit.DB import LinkElementId, UV


def create_room_tag_without_transaction_wrapper(doc, view, room, tag_type_id=None, head_point=None, add_leader=False):
    """
    Tags a room in a plan view.

    The tag is made on the room's own point (Revit can refuse one made away from its room) and then
    its head is moved to where it is wanted.

    Changing the model: this needs to run inside a transaction.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param view: The plan view the tag belongs to.
    :type view: Autodesk.Revit.DB.ViewPlan
    :param room: The room to tag.
    :type room: Autodesk.Revit.DB.Architecture.Room
    :param tag_type_id: The room tag type, defaults to None (Revit's default).
    :type tag_type_id: Autodesk.Revit.DB.ElementId, optional
    :param head_point: Where the tag head goes, in feet, defaults to None (on the room's point).
    :type head_point: Autodesk.Revit.DB.XYZ, optional
    :param add_leader: Whether the tag has a leader back to the room, defaults to False.
    :type add_leader: bool, optional

    :return: Result class instance. .result holds the tag when it was created.
    :rtype: :class:`.Result`
    """

    return_value = Result()
    try:
        point = room.Location.Point
        tag = doc.Create.NewRoomTag(LinkElementId(room.Id), UV(point.X, point.Y), view.Id)
        if tag_type_id is not None and tag.GetTypeId() != tag_type_id:
            tag.ChangeTypeId(tag_type_id)
        try:
            if add_leader:
                tag.HasLeader = True
            if head_point is not None:
                tag.TagHeadPosition = head_point
        except Exception as e:
            return_value.append_message("The room tag is made on the room, its head kept Revit's place: {}".format(e))
        return_value.result.append(tag)
        return_value.append_message("Room tag created.")
    except Exception as e:
        return_value.update_sep(False, "Failed to create the room tag with exception: {}".format(e))
    return return_value
