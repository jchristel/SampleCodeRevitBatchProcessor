"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A number of functions around Revit independent tags elbow properties.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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
from duHast.Revit.Common.revit_version import get_revit_version_number
from duHast.Revit.Common.Geometry.geometry import get_point_as_doubles

ELBOW_LOCATION = "elbow_location"
LEADER_END = "leader_end"
LEADER_REFERENCE = "leader_reference"
LEADER_ELEMENT_REFERENCE_ID = "leader_element_reference_id"
LEADER_LINKED_ELEMENT_REFERENCE_ID = "leader_linked_element_reference_id"


def get_elbow_properties(doc, tag, points_as_double=False):
    """
    Returns elbow properties depending on revit version.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param tag: The tag element
    :type tag: Autodesk.Revit.DB.IndependentTag

    :return: A list of dictionaries with 3 keys: ELBOW_LOCATION, LEADER_END and LEADER_REFERENCE.
    :rtype: [{str:Autodesk.Revit.DB.XYZ, str:Autodesk.Revit.DB.XYZ, str:Autodesk.Revit.DB Reference }]
    """

    # get the revit version:
    revit_version = get_revit_version_number(doc)
    data = None
    if revit_version <= 2021:
        data = get_elbow_properties_2021(tag, points_as_double)
    elif revit_version >= 2022:
        data = get_elbow_properties_2022(tag, points_as_double)
    return data


def get_elbow_properties_2021(tag, points_as_double):
    """
    Get elbow properties in revit versions up to revit 2022

    :param tag: The tag element
    :type tag: Autodesk.Revit.DB.IndependentTag

    :return: A list of a single dictionaries with 3 keys: ELBOW_LOCATION, LEADER_END and LEADER_REFERENCE.
    :rtype: [{str:Autodesk.Revit.DB.XYZ, str:Autodesk.Revit.DB.XYZ, str:Autodesk.Revit.DB Reference }]
    """

    data = []
    elbow_properties = {}
    try:
        if tag.HasElbow:
            elbow_properties[LEADER_REFERENCE] = {
                LEADER_ELEMENT_REFERENCE_ID: None,
                LEADER_LINKED_ELEMENT_REFERENCE_ID: None,
            }
            if points_as_double:
                elbow_properties[ELBOW_LOCATION] = get_point_as_doubles(tag.LeaderElbow)
            else:
                elbow_properties[ELBOW_LOCATION] = tag.LeaderElbow
            if tag.LeaderEndCondition == rdb.LeaderEndCondition.Free:
                if points_as_double:
                    elbow_properties[LEADER_END] = get_point_as_doubles(tag.LeaderEnd)
                else:
                    elbow_properties[LEADER_END] = tag.LeaderEnd
            else:
                elbow_properties[LEADER_END] = None
        else:
            elbow_properties[ELBOW_LOCATION] = None
            elbow_properties[LEADER_END] = None
    except:
        elbow_properties[ELBOW_LOCATION] = None
        elbow_properties[LEADER_END] = None

    data.append(elbow_properties)
    return data


def get_elbow_properties_2022(tag, points_as_double):
    """
    Get elbow properties in revit versions from revit 2023 onwards

    :param tag: The tag element
    :type tag: Autodesk.Revit.DB.IndependentTag

    :return: A list of dictionaries with 3 keys: ELBOW_LOCATION, LEADER_END and LEADER_REFERENCE.
    :rtype: [{str:Autodesk.Revit.DB.XYZ, str:Autodesk.Revit.DB.XYZ, str:Autodesk.Revit.DB Reference }]
    """

    data = []
    tagged_references = tag.GetTaggedReferences()
    for tag_ref in tagged_references:
        elbow_properties = {}
        # store references to linked element or the element in same model which got tagged only
        elbow_properties[LEADER_REFERENCE] = {
            LEADER_ELEMENT_REFERENCE_ID: tag_ref.ElementId.IntegerValue,
            LEADER_LINKED_ELEMENT_REFERENCE_ID: tag_ref.LinkedElementId.IntegerValue,
        }
        try:
            if tag.HasLeaderElbow(tag_ref):
                if points_as_double:
                    elbow_properties[ELBOW_LOCATION] = get_point_as_doubles(
                        tag.GetLeaderElbow(tag_ref)
                    )
                else:
                    elbow_properties[ELBOW_LOCATION] = tag.GetLeaderElbow(tag_ref)
                if tag.LeaderEndCondition == rdb.LeaderEndCondition.Free:
                    if points_as_double:
                        elbow_properties[LEADER_END] = get_point_as_doubles(
                            tag.GetLeaderEnd(tag_ref)
                        )
                    else:
                        elbow_properties[LEADER_END] = tag.GetLeaderEnd(tag_ref)
                else:
                    elbow_properties[LEADER_END] = None
            else:
                elbow_properties[ELBOW_LOCATION] = None
                elbow_properties[LEADER_END] = None
        except:
            elbow_properties[ELBOW_LOCATION] = None
            elbow_properties[LEADER_END] = None
        data.append(elbow_properties)
    return data
