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
    get_elbow_properties,
    ELBOW_LOCATION,
    LEADER_END,
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
        data = []
        try:
            if custom_element_filter != None:
                if custom_element_filter.check_element(doc, tag_instance.Id):
                    # this can throw an exception...wrap in try catch
                    tag_text = "??"
                    try:
                        tag_text = tag_instance.TagText
                    except:
                        pass
                    elbow_properties = {}
                    # get elbow properties
                    if tag_instance.HasLeader:
                        elbows = get_elbow_properties(doc, tag_instance)
                        elbow_properties[ELBOW_LOCATION] = (
                            get_point_as_string(value)
                            for value in elbows[ELBOW_LOCATION]
                        )
                        elbow_properties[LEADER_END] = (
                            get_point_as_string(value) for value in elbows[LEADER_END]
                        )
                    else:
                        elbow_properties[ELBOW_LOCATION] = ""
                        elbow_properties[LEADER_END] = ""

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
                        tag_instance.LeaderEndCondition,  # attached or free
                        elbow_properties[ELBOW_LOCATION],  # elbow(s) locations
                        elbow_properties[LEADER_END],  # leader end(s) locations
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
                        tag_instance.TagOrientation,  # horizontal ,vertical, model
                    ]

                    # add data for later versions of revit
                    if revit_version >= 2023:
                        row.append(tag_instance.LeadersPresentationMode)
                        row.append(str(tag_instance.MergeElbows))
                    data.append(row)
        except:
            data.append([revit_file_path, str(tag_instance.Id)])
    return data
