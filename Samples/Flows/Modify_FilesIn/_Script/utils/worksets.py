"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a worksets related helper functions.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- move some objects to a specified worksets

"""

#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2024, Jan Christel
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


# --------------------------
# Imports
# --------------------------

import clr

from duHast.Revit.Grids.grids import get_grids_in_model
from duHast.Revit.Levels.levels import get_levels_in_model
from duHast.Revit.Common.worksets import modify_element_workset
from duHast.Utilities.Objects import result as res

import Autodesk.Revit.DB as rdb


def modify(doc, default_workset_name):
    """
    Updates worksets of reference planes, levels, grids, scope boxes

    :param doc: revit document
    :type doc: Document
    :param default_workset_name: default workset name
    :type default_workset_name: str
    :return: result
    :rtype: Result
    """

    found_match = False
    return_value = res.Result()

    # fix uyp grids
    collector_grids = get_grids_in_model(doc)
    grids_result = modify_element_workset(
        doc, default_workset_name, collector_grids, "grids"
    )
    return_value.update(grids_result)

    # fix up levels
    collector_levels = get_levels_in_model(doc)
    levels_result = modify_element_workset(
        doc, default_workset_name, collector_levels, "levels"
    )
    return_value.update(levels_result)

    # fix up scope boxes
    collector_scope_boxes = rdb.FilteredElementCollector(doc).OfCategory(
        rdb.BuiltInCategory.OST_VolumeOfInterest
    )
    scope_boxes_result = modify_element_workset(
        doc, default_workset_name, collector_scope_boxes, "scope boxes"
    )
    return_value.update(scope_boxes_result)

    # fix up ref planes
    collector_reference_planes = rdb.FilteredElementCollector(doc).OfClass(
        rdb.ReferencePlane
    )
    reference_planes_result = modify_element_workset(
        doc,
        default_workset_name,
        collector_reference_planes,
        "reference planes",
    )
    return_value.update(reference_planes_result)

    return return_value
