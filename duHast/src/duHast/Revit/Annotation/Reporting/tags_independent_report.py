"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a Revit tag instances report function. 
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

import json

from duHast.Revit.Annotation.independent_tags import get_all_independent_tags
from duHast.Revit.Annotation.independent_tags_elbow_properties import (
    get_elbow_properties,
    ELBOW_LOCATION,
    LEADER_END,
    LEADER_REFERENCE,
)

from duHast.Revit.Annotation.Reporting import (
    gen_annotations_instance_report_header as props,
)

from duHast.Revit.Common.Geometry.geometry import get_point_as_string
from duHast.Utilities.utility import encode_ascii
from duHast.Revit.Common.revit_version import get_revit_version_number

import Autodesk.Revit.DB as rdb


def get_tag_instances_report_data(doc, revit_file_path, custom_element_filter):
    """
    Gets tag instances data to be written to report file.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param revit_file_path: The file hostname, which is added to data returned.
    :type revit_file_path: str
    :param custom_element_filter: allows to filter tags by specific tag properties
    :type custom_element_filter: class:`.RevitCustomElementFilter`

    :return: list of list of sheet properties.
    :rtype: list of list of str
    """

    data = []
    revit_version = get_revit_version_number(doc)
    tag_instances = get_all_independent_tags(doc)
    for tag_instance in tag_instances:
        row = []
        try:
            if custom_element_filter != None:
                if custom_element_filter.check_element(doc, tag_instance.Id):
                    # this can throw an exception...wrap in try catch
                    tag_text = "<empty>"
                    try:
                        tag_text = tag_instance.TagText
                    except:
                        pass

                    # convert elbow properties to string
                    # default (no elbows)
                    elbows = [
                        {LEADER_REFERENCE: None},
                        {ELBOW_LOCATION: None},
                        {LEADER_END: None},
                    ]
                    elbow_properties_as_json_strings = ""
                    # get elbow properties
                    if tag_instance.HasLeader:
                        elbows = get_elbow_properties(doc, tag_instance)
                    # convert to json for report
                    elbow_properties_as_json_strings = json.dumps(elbows)

                    # leader end condition (need to check if there is a leader)
                    leader_end_condition = str(None)
                    if tag_instance.HasLeader:
                        leader_end_condition = str(tag_instance.LeaderEndCondition)

                    # base line revit data
                    row = {
                        props.HOST_FILE: revit_file_path,
                        props.TAG_ID: str(tag_instance.Id),
                        props.TAG_HAS_LEADER: str(
                            tag_instance.HasLeader
                        ),  # leader flag
                        props.TAG_IS_ORPHANED: str(
                            tag_instance.IsOrphaned
                        ),  # is orphaned tag?
                        props.TAG_IS_MATERIAL_TAG: str(
                            tag_instance.IsMaterialTag
                        ),  # is a material tag
                        props.IS_MULTICATEGORY_TAG: str(
                            tag_instance.IsMulticategoryTag
                        ),  # is is multi category tag
                        props.LEADER_END_CONDITION: leader_end_condition,  # attached or free
                        props.LEADER_PROPERTIES: elbow_properties_as_json_strings,  # elbow properties
                        props.MULTI_REFERENCE_ANNOTATION_ID: str(
                            tag_instance.MultiReferenceAnnotationId
                        ),
                        props.TAG_TEXT: tag_text,  # tag text
                        props.TAGGED_ELEMENT_NAME: encode_ascii(
                            rdb.Element.Name.GetValue(
                                doc.GetElement(tag_instance.TaggedLocalElementId)
                            )
                        ),  # tagged element name
                        props.TAG_HEAD_LOCATION: get_point_as_string(
                            tag_instance.TagHeadPosition
                        ),  # tag location
                        props.TAG_ROTATION_ANGLE: str(
                            tag_instance.RotationAngle
                        ),  # rotation tag
                        props.TAG_ORIENTATION: str(
                            tag_instance.TagOrientation
                        ),  # horizontal ,vertical, model
                    }

                    # add data for later versions of revit
                    if revit_version >= 2023:
                        row[
                            props.TAG_PRESENTATION_MODE
                        ]: tag_instance.LeadersPresentationMode
                        row[props.MERGE_ELBOWS : str(tag_instance.MergeElbows)]
                    data.append(json.dumps(row))
        except Exception as e:
            data.append(
                {props.HOST_FILE: revit_file_path, props.TAG_ID: str(tag_instance.Id)}
            )
    return data
