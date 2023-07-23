"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains utility function(s) for Revit link reports. 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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

from duHast.Revit.Common import parameter_get_utils as rParaGet
from duHast.Revit.Links.links import (
    get_all_revit_link_instances,
    get_revit_link_type_from_instance,
)


def get_revit_link_type_data(doc, revit_link_type):
    """
    Gets Revit Link Type data for reporting.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param revit_link_type: The link type of which to get the data from.
    :type revit_link_type: Autodesk.Revit.DB.RevitLinkType
    :return: A list of string
    :rtype: list str
    """

    # default values
    model_path = "unknown"
    is_loaded = False
    is_from_local_path = False
    path_type = "unknown"
    is_loaded = revit_link_type.IsLoaded(doc, revit_link_type.Id)
    is_from_local_path = revit_link_type.IsFromLocalPath()
    ex_file_ref = revit_link_type.GetExternalFileReference()
    # get the workset of the link type (this can bew different to the workset of the link instance)
    ws_parameter = revit_link_type.get_Parameter(
        rdb.BuiltInParameter.ELEM_PARTITION_PARAM
    )
    if ex_file_ref.IsValidExternalFileReference(ex_file_ref):
        model_path = rdb.ModelPathUtils.ConvertModelPathToUserVisiblePath(
            ex_file_ref.GetPath()
        )
        path_type = ex_file_ref.PathType.ToString()

    data = [
        rdb.Element.Name.GetValue(revit_link_type),
        str(is_loaded),
        str(ws_parameter.AsValueString()),
        str(is_from_local_path),
        path_type,
        model_path,
    ]

    return data


def get_revit_link_report_data(doc, revit_file_path):
    """
    Gets link data ready for being printed to file.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param revit_file_path: The file hostname, which is added to data returned.
    :type revit_file_path: str
    :return: list of list of revit link properties.
    :rtype: list of list of str
    """

    data = []
    collector = get_all_revit_link_instances(doc)
    for c in collector:
        # get the workset
        ws_parameter = c.get_Parameter(rdb.BuiltInParameter.ELEM_PARTITION_PARAM)
        # get the design option
        do_parameter = c.get_Parameter(rdb.BuiltInParameter.DESIGN_OPTION_ID)
        # get whether link is shared or not (only works when link is loaded)
        if "<Not Shared>" in c.Name:
            l_s = False
        else:
            l_s = True
        # get shared location name ( needs to be in try catch in case file is unloaded)
        link_location_name = "unknown"
        try:
            link_location_name = c.GetLinkDocument().ActiveProjectLocation.Name
        except Exception:
            pass
        link_type = get_revit_link_type_from_instance(doc, c)
        link_type_data = get_revit_link_type_data(doc, link_type)
        # add other data
        link_type_data = (
            [revit_file_path]
            + [str(c.Id)]
            + link_type_data
            + [str(l_s)]
            + [link_location_name]
            + [rParaGet.get_parameter_value(ws_parameter)]
            + [rParaGet.get_parameter_value(do_parameter)]
        )
        data.append(link_type_data)
    return data
