"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of functions around Revit filled regions.
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

# import common library modules
from duHast.Revit.DetailItems.Utility import (
    detail_items_type_sorting as rDetailItemTypeSort,
)
from duHast.Revit.DetailItems.detail_items import get_all_detail_types_by_category, FILLED_REGION_TYPE
from duHast.Revit.Common.transaction import in_transaction
from duHast.Utilities.Objects.result import Result


# import Autodesk
from Autodesk.Revit.DB import (
    FilledRegion,
    FilteredElementCollector,
    Transaction,
)


def get_filled_regions_in_model(doc):
    """
    Gets all filled region instances in a model.

    Filters by class.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A list containing floor instances.
    :rtype: list Autodesk.Revit.DB.FilledRegion
    """

    return FilteredElementCollector(doc).OfClass(FilledRegion)


def get_all_filled_region_type_ids_available(doc):
    """
    Gets all filled region types ids in model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A list of element ids representing filled region types.
    :rtype: list Autodesk.Revit.DB.ElementIds
    """

    dic = rDetailItemTypeSort.build_detail_type_ids_dictionary(
        get_all_detail_types_by_category(doc)
    )
    if FILLED_REGION_TYPE in dic:
        return dic[FILLED_REGION_TYPE]
    else:
        return []



# --------------------------------------------- geometry ------------------

def get_filled_region_curve_loops(filled_region):
    """
    Gets the curve loops of a filled region.
    :param filled_region: A filled region instance.
    :type filled_region: Autodesk.Revit.DB.FilledRegion

    :return: A list of curve loops.
    :rtype: list Autodesk.Revit.DB.CurveLoop
    """

    # get the loops of a filled region's geometry
    curve_loops = filled_region.GetBoundaries()

    return curve_loops


def create_filled_region_by_view(doc, view, curve_loops, filled_region_type):
    """
    Creates a filled region in the specified view.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param view: The view to create the filled region in.
    :type view: Autodesk.Revit.DB.View
    :param curve_loops: The curve loops to use for the filled region.
    :type curve_loops: list Autodesk.Revit.DB.CurveLoop
    :param filled_region_type: The type of filled region to create.
    :type filled_region_type: Autodesk.Revit.DB.ElementId

    :return: The created filled region instance.
    :rtype: Autodesk.Revit.DB.FilledRegion
    """


    # set up a status tracker
    return_value = Result()

    # set up an action creating a filled region
    def action():
         # set up a status tracker
        action_return_value = Result()
        try:
            # create the filled region
            filled_region = FilledRegion.Create(doc, filled_region_type, view.Id, curve_loops)
            action_return_value.append_message("Filled region created successfully.")
        except Exception as e:
            action_return_value.update_sep(False, "Failed to create filled region with error: ".format(e))
        return action_return_value


    transaction = Transaction(doc, "Drawing filled region")
    return_value = in_transaction(transaction, action)


    return return_value