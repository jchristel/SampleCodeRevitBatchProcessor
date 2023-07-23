"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A number of functions around Revit independent tags elements tagged properties.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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

HOST_ELEMENT_ID = "host_element_id"
LINK_ELEMENT_ID = "link_element_id"
LINK_INSTANCE_ID = "link_instance_id"


def get_tagged_elements(doc, tag):
    """
    Returns tagged element(s) depending on revit version.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param tag: The tag element
    :type tag: Autodesk.Revit.DB.IndependentTag

    :return: A list of dictionaries representing the tagged object(s).

        Dictionary has three keys:HOST_ELEMENT_ID,LINK_ELEMENT_ID,LINK_INSTANCE_ID
        If an exception occurs it will return a dictionary with same keys but None values.

    :rtype: [{str:Autodesk.Revit.DB.ElementId}]
    """

    # get the revit version:
    revit_version = get_revit_version_number(doc)
    data = None
    if revit_version <= 2021:
        data = get_tagged_elements_2021(tag)
    elif revit_version >= 2022:
        data = get_tagged_elements_2022(tag)
    return data


def get_tagged_elements_2021(tag):
    """
    Get tagged element Id in revit versions up to revit 2022

    :param tag: The tag element
    :type tag: Autodesk.Revit.DB.IndependentTag

    :return: A list with a single dictionary representing the tagged object.

        Dictionary has three keys:HOST_ELEMENT_ID,LINK_ELEMENT_ID,LINK_INSTANCE_ID
        If an exception occurs it will return a dictionary with same keys but None values.

    :rtype: [{str:Autodesk.Revit.DB.ElementId}]
    """

    data = []

    try:
        id = tag.TaggedElementId
        id_data = {}
        if id.HostElementId != rdb.ElementId.InvalidElementId:
            id_data[HOST_ELEMENT_ID] = id.HostElementId
            id_data[LINK_ELEMENT_ID] = rdb.ElementId.InvalidElementId
            id_data[LINK_INSTANCE_ID] = rdb.ElementId.InvalidElementId
        elif id.LinkedElementId != rdb.ElementId.InvalidElementId:
            id_data[HOST_ELEMENT_ID] = rdb.ElementId.InvalidElementId
            id_data[LINK_ELEMENT_ID] = id.LinkedElementId
            id_data[LINK_INSTANCE_ID] = rdb.ElementId.InvalidElementId
        else:
            id_data[HOST_ELEMENT_ID] = rdb.ElementId.InvalidElementId
            id_data[LINK_ELEMENT_ID] = rdb.ElementId.InvalidElementId
            id_data[LINK_INSTANCE_ID] = id.LinkInstanceId
        data.append(id_data)
    except:
        id_data = {}
        id_data[HOST_ELEMENT_ID] = None
        id_data[LINK_ELEMENT_ID] = None
        id_data[LINK_INSTANCE_ID] = None
        data.append(id_data)
    return data


def get_tagged_elements_2022(tag):
    """
    Get elbow properties in revit versions from revit 2023 onwards

    :param tag: The tag element
    :type tag: Autodesk.Revit.DB.IndependentTag

    :return: A list of dictionaries representing the tagged object(s).

        Dictionary has three keys:HOST_ELEMENT_ID,LINK_ELEMENT_ID,LINK_INSTANCE_ID
        If an exception occurs it will return a dictionary with same keys but None values.

    :rtype: [{str:Autodesk.Revit.DB.ElementId},]
    """

    data = []
    try:
        ids = tag.GetTaggedElementIds()
        for id in ids:
            id_data = {}
            try:
                if id.HostElementId != rdb.ElementId.InvalidElementId:
                    id_data[HOST_ELEMENT_ID] = id.HostElementId
                    id_data[LINK_ELEMENT_ID] = rdb.ElementId.InvalidElementId
                    id_data[LINK_INSTANCE_ID] = rdb.ElementId.InvalidElementId
                elif id.LinkedElementId != rdb.ElementId.InvalidElementId:
                    id_data[HOST_ELEMENT_ID] = rdb.ElementId.InvalidElementId
                    id_data[LINK_ELEMENT_ID] = id.LinkedElementId
                    id_data[LINK_INSTANCE_ID] = rdb.ElementId.InvalidElementId
                else:
                    id_data[HOST_ELEMENT_ID] = rdb.ElementId.InvalidElementId
                    id_data[LINK_ELEMENT_ID] = rdb.ElementId.InvalidElementId
                    id_data[LINK_INSTANCE_ID] = id.LinkInstanceId
            except:
                id_data[HOST_ELEMENT_ID] = None
                id_data[LINK_ELEMENT_ID] = None
                id_data[LINK_INSTANCE_ID] = None
            data.append(id_data)
    except:
        data.append(rdb.ElementId.InvalidElementId)
    return data
