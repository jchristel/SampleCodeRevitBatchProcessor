"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A number of functions around Revit independent tags.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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


import Autodesk.Revit.DB as rdb
from collections import namedtuple

from duHast.Utilities.Objects import result as res
from duHast.Revit.Common.transaction import in_transaction

from duHast.Revit.Common.revit_version import get_revit_version_number
from duHast.Utilities.files_json import read_json_data_from_file
from duHast.Revit.Annotation.Reporting.gen_annotations_instance_report_header import (
    TAG_ID,
    TAG_HEAD_LOCATION,
)
from duHast.Utilities.unit_conversion import convert_imperial_feet_to_metric_mm

# tuples containing move tag data
move_tag = namedtuple("move_tag", "tag new_location old_location")


def update_tag_location(doc, tag_data):
    """
    Moves all tags in dictionary to new location within one transaction

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param tag_data: A dictionary containing tag data of tag to be moved
    :type tag_data: {int:namedtuple move_tag}

    :return:
        Result class instance.

        - result.status. True if all tags where moved successfully, otherwise False.
        - result.message will contain ids of tags moved in format:'Moved tag: ' + id
        - result.result list of tags

        On exception:

        - result.status (bool) will be False.
        - result.message will contain an exception message.
        - result.result will be empty

    :rtype: :class:`.Result`
    """

    def action():
        action_return_value = res.Result()
        try:
            for move_data in tag_data:
                try:
                    move_data.tag.Location.Move(
                        move_data.new_location - move_data.old_location
                    )
                    action_return_value.update_sep(
                        True, "Moved tag: {}".format(move_data.tag.Id)
                    )
                    action_return_value.result.append(move_data.tag)
                except Exception as e:
                    action_return_value.update_sep(
                        False,
                        "Failed to move tag: {} with exception: {}".format(
                            move_data.tag.Id, e
                        ),
                    )
        except Exception as e:
            action_return_value.update_sep(
                False,
                "Failed to move tag with exception: {}".format(e),
            )
        return action_return_value

    # set up an transaction
    transaction = rdb.Transaction(doc, "Moving tags: {}".format(len(tag_data)))
    # execute transaction in transaction wrapper method
    result_moving_tags = in_transaction(transaction, action)
    return result_moving_tags


def update_tag_locations_from_report(doc, report_file_path, distance_threshold=50):
    """
    Reads a tag instance report and updates the location of tags in model with matching id if they have moved further then a given threshold distance.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param report_file_path: The fully qualified file path of the report file.
    :type report_file_path: str
    :param distance_threshold: The threshold distance, in mm, a tag has to move before it gets moved to a new location, defaults to 50. The distance is calculated by subtracting the current tag location from the one recorded in the report.
    :type distance_threshold: int, optional

    :return:
        Result class instance.

        - result.status. True if all tags where moved successfully, or no tags had to be moved, otherwise False.
        - result.message will contain ids of tags moved in format:'Moved tag: ' + id
        - result.result list of tags

        On exception:

        - result.status (bool) will be False.
        - result.message will contain an exception message.
        - result.result will be empty

    :rtype: :class:`.Result`
    """

    return_value = res.Result()
    # read data from files
    tag_data_list = read_json_data_from_file(report_file_path)
    tag_updates = []
    for tag_data in tag_data_list:
        # get the id of the tag
        id_data = tag_data[TAG_ID]
        try:
            # get the actual tag element in model
            tag_in_model = doc.GetElement(rdb.ElementId(id_data))
            # in case tag no longer exists
            if tag_in_model != None:
                head_location_data = tag_data[TAG_HEAD_LOCATION]
                head_location_data_as_xyz = rdb.XYZ(
                    head_location_data[0], head_location_data[1], head_location_data[2]
                )
                # check distance to current location
                tag_distance = abs(
                    convert_imperial_feet_to_metric_mm(
                        head_location_data_as_xyz.DistanceTo(
                            tag_in_model.TagHeadPosition
                        )
                    )
                )
                if tag_distance > distance_threshold:
                    # build a list of tags to move in one transaction
                    tag_updates.append(
                        move_tag(
                            tag=tag_in_model,
                            new_location=head_location_data_as_xyz,
                            old_location=tag_in_model.TagHeadPosition,
                        )
                    )
        except Exception as e:
            return_value.update_sep(
                False, "An exception occurred when gathering tag data: {}".format(e)
            )
    # check if any tags need updating their position:
    if len(tag_updates) > 0:
        return_value.update(update_tag_location(doc, tag_updates))
    else:
        return_value.update_sep(True, "No tags required moving")
    return return_value
