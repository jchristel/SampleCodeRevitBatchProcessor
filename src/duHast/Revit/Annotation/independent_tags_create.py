"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Helper functions to create independent tags.
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

from Autodesk.Revit.DB import (
    IndependentTag,
    LeaderEndCondition,
    Reference,
    TagMode,
    TagOrientation,
)


def create_independent_tag_without_transaction_wrapper(
    doc,
    view,
    element,
    head_point,
    tag_type_id=None,
    orientation=TagOrientation.Horizontal,
    add_leader=False,
    elbow_point=None,
    end_point=None,
):
    """
    Tags an element in a view.

    The tag is made on the element at the head point and then, when a type is wanted, changed to it
    (so a multi category tag family works whatever the element's category is). A free leader end,
    and an elbow, are set when given; a leader which will not take them keeps Revit's.

    Changing the model: this needs to run inside a transaction.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param view: The view the tag belongs to.
    :type view: Autodesk.Revit.DB.View
    :param element: The element to tag.
    :type element: Autodesk.Revit.DB.Element
    :param head_point: Where the tag head goes, in feet.
    :type head_point: Autodesk.Revit.DB.XYZ
    :param tag_type_id: The tag type to use, defaults to None (Revit's default for the category).
    :type tag_type_id: Autodesk.Revit.DB.ElementId, optional
    :param orientation: Horizontal or vertical, defaults to horizontal.
    :type orientation: Autodesk.Revit.DB.TagOrientation, optional
    :param add_leader: Whether the tag has a leader, defaults to False.
    :type add_leader: bool, optional
    :param elbow_point: Where the leader bends, defaults to None.
    :type elbow_point: Autodesk.Revit.DB.XYZ, optional
    :param end_point: Where a free leader ends, defaults to None.
    :type end_point: Autodesk.Revit.DB.XYZ, optional

    :return: Result class instance. .result holds the tag when it was created.
    :rtype: :class:`.Result`
    """

    return_value = Result()
    try:
        reference = Reference(element)
        tag = IndependentTag.Create(
            doc, view.Id, reference, add_leader, TagMode.TM_ADDBY_CATEGORY, orientation, head_point
        )
        if tag_type_id is not None and tag.GetTypeId() != tag_type_id:
            tag.ChangeTypeId(tag_type_id)
        if add_leader and end_point is not None:
            try:
                tag.LeaderEndCondition = LeaderEndCondition.Free
                tag.SetLeaderEnd(reference, end_point)
                if elbow_point is not None:
                    tag.SetLeaderElbow(reference, elbow_point)
            except Exception as e:
                return_value.append_message("The tag is made, its leader kept Revit's end: {}".format(e))
        return_value.result.append(tag)
        return_value.append_message("Tag created.")
    except Exception as e:
        return_value.update_sep(False, "Failed to create the tag with exception: {}".format(e))
    return return_value
