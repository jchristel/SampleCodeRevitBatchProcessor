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


def get_elbow_properties(doc, tag):
    """
    Returns elbow properties depending on revit version.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param tag: The tag element
    :type tag: Autodesk.Revit.DB.IndependentTag

    :return: a dictionary with 2 keys: ELBOW_LOCATION and LEADER_END. Each of those are lists of XYZ points
    :rtype: {str:[Autodesk.Revit.DB.XYZ]}
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

    :return: a dictionary with 2 keys: ELBOW_LOCATION and LEADER_END. Each of those are lists of XYZ points
    :rtype: {str:[Autodesk.Revit.DB.XYZ]}
    """

    data = {}
    try:
        if(tag.HasElbow):
            data[ELBOW_LOCATION] = [tag.LeaderElbow]
            if(tag.LeaderEndCondition == rdb.LeaderEndCondition.Free):
                data[LEADER_END] = [tag.LeaderEnd]
            else:
                data[LEADER_END]=[None]
        else:
            data[ELBOW_LOCATION] = [None]
            data[LEADER_END] = [None]
    except:
        data[ELBOW_LOCATION] = [None]
        data[LEADER_END] = [None]
    return data


def get_elbow_properties_2022(tag):
    """
    Get elbow properties in revit versions from revit 2023 onwards

    :param tag: The tag element
    :type tag: Autodesk.Revit.DB.IndependentTag

    :return: a dictionary with 2 keys: ELBOW_LOCATION and LEADER_END. Each of those are lists of XYZ points
    :rtype: {str:[Autodesk.Revit.DB.XYZ]}
    """
    
    data = {}
    data[ELBOW_LOCATION] = []
    data[LEADER_END] = []
    tagged_references = tag.GetTaggedReferences()
    for tag_ref in tagged_references:
        try:
            if(tag.HasLeaderElbow(tag_ref)):
                data[ELBOW_LOCATION].append(tag.GetLeaderElbow(tag_ref))
                if(tag.LeaderEndCondition == rdb.LeaderEndCondition.Free):
                    data[LEADER_END].append(tag.GetLeaderEnd(tag_ref))
                else:
                    data[LEADER_END].append(None)
            else:
                data[ELBOW_LOCATION].append(None)
                data[LEADER_END].append(None)
        except:
            data[ELBOW_LOCATION].append(None)
            data[LEADER_END].append(None)
    return data
