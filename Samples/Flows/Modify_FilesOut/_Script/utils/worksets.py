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
# Copyright (c) 2020  Jan Christel
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

# --------------------------
# Imports
# --------------------------

import clr

from duHast.Revit.Grids.grids import get_grids_in_model
from duHast.Revit.Levels.levels import get_levels_in_model
from duHast.Revit.Common.worksets import modify_element_workset
from duHast.Utilities.Objects import result as res

import Autodesk.Revit.DB as rdb


def modify(doc, grid_data, revit_file_name):
    """
    Updates worksets of reference planes, levels, grids, scope boxes

    :param doc: _description_
    :type doc: _type_
    :param grid_data: _description_
    :type grid_data: _type_
    :return: _description_
    :rtype: _type_
    """

    found_match = False
    return_value = res.Result()
    for file_name, default_workset_name in grid_data:
        if revit_file_name.startswith(file_name):
            found_match = True
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

            break
    if found_match == False:
        return_value.update_sep(
            False,
            "No grid data provided for current Revit file ".format(revit_file_name),
        )
    return return_value
