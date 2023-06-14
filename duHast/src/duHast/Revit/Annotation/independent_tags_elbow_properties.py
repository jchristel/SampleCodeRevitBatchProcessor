"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A number of functions around Revit independent tags elbow properties.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
#
# License:
#
#
# Revit Batch Processor Sample Code
#
# Copyright (c) 2023  Jan Christel
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


import Autodesk.Revit.DB as rdb
from duHast.Revit.Common.revit_version import get_revit_version_number

ELBOW_LOCATION = "elbow_location"
LEADER_END = "leader_end"
LEADER_REFERENCE = "leader_reference"


def get_elbow_properties(doc, tag):
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
        data = get_elbow_properties_2021(tag)
    elif revit_version >= 2022:
        data = get_elbow_properties_2022(tag)
    return data


def get_elbow_properties_2021(tag):
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
        if(tag.HasElbow):
            elbow_properties[LEADER_REFERENCE]=None
            elbow_properties[ELBOW_LOCATION] = tag.LeaderElbow
            if(tag.LeaderEndCondition == rdb.LeaderEndCondition.Free):
                elbow_properties[LEADER_END] = tag.LeaderEnd
            else:
                elbow_properties[LEADER_END]=None
        else:
            elbow_properties[ELBOW_LOCATION] = None
            elbow_properties[LEADER_END] = None
    except:
        elbow_properties[ELBOW_LOCATION] = None
        elbow_properties[LEADER_END] = None

    data.append(elbow_properties)
    return data


def get_elbow_properties_2022(tag):
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
        elbow_properties[LEADER_REFERENCE]=tag_ref
        try:
            if(tag.HasLeaderElbow(tag_ref)):
                elbow_properties[ELBOW_LOCATION] = tag.GetLeaderElbow(tag_ref)
                if(tag.LeaderEndCondition == rdb.LeaderEndCondition.Free):
                    elbow_properties[LEADER_END]=tag.GetLeaderEnd(tag_ref)
                else:
                    elbow_properties[LEADER_END]=None
            else:
                elbow_properties[ELBOW_LOCATION]=None
                elbow_properties[LEADER_END]=None
        except:
            elbow_properties[ELBOW_LOCATION]=None
            elbow_properties[LEADER_END]=None
        data.append(elbow_properties)
    return data
