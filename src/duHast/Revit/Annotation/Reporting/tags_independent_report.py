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
# BSD License
# Copyright 2023, Jan Christel
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

import json

from duHast.Revit.Annotation.independent_tags import get_all_independent_tags
from duHast.Revit.Annotation.independent_tags_elbow_properties import (
    get_elbow_properties,
)
from duHast.Revit.Annotation.independent_tags_tagged_elements import get_tagged_elements

from duHast.Revit.Annotation.Reporting import (
    gen_annotations_instance_report_header as props,
)

from duHast.Revit.Common.Geometry.points import get_point_as_doubles
from duHast.Revit.Common.revit_version import get_revit_version_number


from Autodesk.Revit.DB import ElementId


def _convert_tagged_element_ids_to_int(data):
    """
    Converts list of dictionaries containing element ids as values to integer values so it can be converted to json

    :param data: A list of dictionaries where values are Element ids
    :type data: [{str:Autodesk.Revit.DB.ElementId}]
    :return: A list of dictionaries where values are int
    :rtype: [{str:int}]
    """

    for tag_dic in data:
        for id_entry in tag_dic:
            if type(tag_dic[id_entry]) == ElementId:
                tag_dic[id_entry] = tag_dic[id_entry].IntegerValue
    return data


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
        row = {}
        try:
            if custom_element_filter != None:
                if custom_element_filter.check_element(doc, tag_instance.Id):
                    # this can throw an exception...wrap in try catch
                    tag_text = "<empty>"
                    try:
                        tag_text = tag_instance.TagText
                    except:
                        pass

                    # get tagged element ids
                    tagged_element_ids = get_tagged_elements(doc=doc, tag=tag_instance)
                    # convert ids to integer value ( to be able to output them to json)
                    tagged_element_data = _convert_tagged_element_ids_to_int(
                        tagged_element_ids
                    )
                    # get elbow properties
                    elbow_properties = None
                    # get elbow properties
                    if tag_instance.HasLeader:
                        elbow_properties = get_elbow_properties(
                            doc=doc, tag=tag_instance, points_as_double=True
                        )

                    # leader end condition (need to check if there is a leader)
                    leader_end_condition = str(None)
                    if tag_instance.HasLeader:
                        leader_end_condition = str(tag_instance.LeaderEndCondition)

                    # base line revit data
                    row = {
                        props.HOST_FILE: revit_file_path,
                        props.TAG_ID: tag_instance.Id.IntegerValue,
                        props.TAG_HAS_LEADER: tag_instance.HasLeader,  # leader flag
                        props.TAG_IS_ORPHANED: tag_instance.IsOrphaned,  # is orphaned tag?
                        props.TAG_IS_MATERIAL_TAG: tag_instance.IsMaterialTag,  # is a material tag
                        props.IS_MULTICATEGORY_TAG: tag_instance.IsMulticategoryTag,  # is is multi category tag
                        props.LEADER_END_CONDITION: leader_end_condition,  # attached or free
                        props.LEADER_PROPERTIES: elbow_properties,  # elbow properties
                        props.MULTI_REFERENCE_ANNOTATION_ID: tag_instance.MultiReferenceAnnotationId.IntegerValue,
                        props.TAG_TEXT: tag_text,  # tag text
                        props.TAGGED_ELEMENT_IDS: tagged_element_data,  # tagged element ids as integers
                        props.TAG_HEAD_LOCATION: get_point_as_doubles(
                            tag_instance.TagHeadPosition
                        ),  # tag location
                        props.TAG_ROTATION_ANGLE: tag_instance.RotationAngle,  # rotation tag
                        props.TAG_ORIENTATION: str(
                            tag_instance.TagOrientation
                        ),  # horizontal ,vertical, model
                    }

                    # add data for later versions of revit
                    if revit_version >= 2023:
                        row[props.TAG_PRESENTATION_MODE] = str(
                            tag_instance.LeadersPresentationMode
                        )
                        row[props.MERGE_ELBOWS] = tag_instance.MergeElbows
                    data.append(row)
        except Exception as e:
            data.append(
                {
                    props.HOST_FILE: revit_file_path,
                    props.TAG_ID: str(tag_instance.Id),
                    "exception": str(e),
                }
            )
    return data


def read_tag_independent_data_from_file(revit_file_path):
    """
    Reads an independent tags report file into a list of dictionaries

    :param revit_file_path: Fully qualified file path of report file.
    :type revit_file_path: str
    :return: List of dictionaries where each dictionary contains tag data
    :rtype: [{}]
    """

    data = {}
    try:
        # Opening JSON file
        f = open(revit_file_path)
        # returns JSON object as
        # a dictionary
        data = json.load(f)
    except Exception as e:
        pass
    return data
