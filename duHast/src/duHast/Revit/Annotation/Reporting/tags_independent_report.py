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

from duHast.Revit.Annotation.independent_tags import (
    get_all_independent_tags,
    ELBOW_LOCATION,
    LEADER_END,
)

from duHast.Revit.Annotation.independent_tags_elbow_properties import get_elbow_properties
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
                    elbow_properties_as_strings = {ELBOW_LOCATION: [], LEADER_END: []}
                    # get elbow properties
                    if tag_instance.HasLeader:
                        elbows = get_elbow_properties(doc, tag_instance)
                        for elbow_location in elbows[ELBOW_LOCATION]:
                            if elbow_location != None:
                                elbow_properties_as_strings[ELBOW_LOCATION].append(
                                    get_point_as_string(elbow_location)
                                )
                            else:
                                elbow_properties_as_strings[ELBOW_LOCATION].append(
                                    "None"
                                )

                        for leader_end in elbows[LEADER_END]:
                            if leader_end != None:
                                elbow_properties_as_strings[LEADER_END].append(
                                    get_point_as_string(leader_end)
                                )
                            else:
                                elbow_properties_as_strings[LEADER_END].append("None")
                    else:
                        elbow_properties_as_strings[ELBOW_LOCATION] = ["None"]
                        elbow_properties_as_strings[LEADER_END] = ["None"]

                    # leader end condition (need to check if there is a leader)
                    leader_end_condition = str(None)
                    if tag_instance.HasLeader:
                        leader_end_condition = str(tag_instance.LeaderEndCondition)

                    # base line revit data
                    row = [
                        revit_file_path,
                        str(tag_instance.Id),
                        str(tag_instance.HasLeader),  # leader flag
                        str(tag_instance.IsOrphaned),  # is orphaned tag?
                        str(tag_instance.IsMaterialTag),  # is a material tag
                        str(
                            tag_instance.IsMulticategoryTag
                        ),  # is is multi category tag
                        leader_end_condition,  # attached or free
                        ",".join(
                            elbow_properties_as_strings[ELBOW_LOCATION]
                        ),  # elbow(s) locations
                        ",".join(
                            elbow_properties_as_strings[LEADER_END]
                        ),  # leader end(s) locations
                        str(tag_instance.MultiReferenceAnnotationId),
                        tag_text,  # tag text
                        encode_ascii(
                            rdb.Element.Name.GetValue(
                                doc.GetElement(tag_instance.TaggedLocalElementId)
                            )
                        ),  # tagged element name
                        get_point_as_string(
                            tag_instance.TagHeadPosition
                        ),  # tag location
                        str(tag_instance.RotationAngle),  # rotation tag
                        str(tag_instance.TagOrientation),  # horizontal ,vertical, model
                    ]

                    # add data for later versions of revit
                    if revit_version >= 2023:
                        row.append(tag_instance.LeadersPresentationMode)
                        row.append(str(tag_instance.MergeElbows))
                    data.append(row)
        except Exception as e:
            data.append([revit_file_path, str(tag_instance.Id), str(e)])
    return data
