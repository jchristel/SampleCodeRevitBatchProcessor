"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Revit propagate grids extend visibility, and graphics to other views.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

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
#


import clr

clr.AddReference("System.Core")
from System import Linq

clr.ImportExtensions(Linq)

from collections import namedtuple

from duHast.Revit.Grids import grids as rGrids
from duHast.Revit.Common import transaction as rTran
from duHast.Utilities.Objects import result as res
from duHast.Revit.Grids.grids import get_grid_curves_from_view, get_grid_plane_z_value
from duHast.UI.Objects.ProgressBase import ProgressBase

from Autodesk.Revit.DB import (
    DatumEnds,
    DatumExtentType,
    ElementId,
    Line,
    Transaction,
    XYZ,
)

# output indent
SPACER = "..."

# tuples containing grid data
grid_properties = namedtuple(
    "grid_properties",
    "is_grid_in_scope datum_extent_type_zero datum_extent_type_one grid_curve, end_zero_bubble, end_one_bubble, is_grid_hidden",
)


def get_active_view_grid_data(active_view, grids_in_model):
    """
    returns a dictionary where grid id is the key and values are a list of properties:

    - inScope (bool)
    - isVisible (bool)
    - end zero, end One: Extent type for both ends ( 2D vs 3D) (None if not in scope)
    - curve: the curve (line) describing the grid extent in view (None if not in scope)
    - end bubble one end bubble zero: bool describing which bubble isi visible in view (None if not in scope)

    :param active_view: The active view.
    :type active_view: Autodesk.Revit.DB.View
    :param grids_in_model: Grids in the model.
    :type grids_in_model: [Autodesk.Revit.DB.Grid]

    :return:
        Result class instance.

        - result.status: True.
        - result.message will contain the names of the grids not in scope only.
        - result.result contains a named tuple: grid_properties:

            {
                bool, is the grid in scope (inside the crop region)
                # Datum Extent type at End 0,
                # Datum Extend type at End 1,
                curve, describing the start and end point of grid
                bool, #bubble visible at zero end
                bool, # bubble visible at 1 end
                bool # is the grid visible
            }

        On exception

        - result.status (bool) will be True (exception is ignored)
        - result.message will contain the message grid not in scope for view

    :rtype: :class:`.Result`
    """

    return_value = res.Result()

    grid_visibility_data = {}
    for grid in grids_in_model:
        try:
            # a grid can either be:
            # not in scope (outside the view crop zone)
            # hidden in view
            # visible in view
            grid_curve = get_grid_curves_from_view(grid=grid, view=active_view)
            # check whether grid is in scope (has a curve object for a given view)
            if grid_curve == None:
                grid_visibility_data[grid.Id] = grid_properties(
                    False, None, None, None, None, None, False
                )
            else:
                # store grid properties
                grid_visibility_data[grid.Id] = grid_properties(
                    True,
                    grid.GetDatumExtentTypeInView(DatumEnds.End0, active_view),
                    grid.GetDatumExtentTypeInView(DatumEnds.End1, active_view),
                    grid_curve,
                    grid.IsBubbleVisibleInView(DatumEnds.End0, active_view),
                    grid.IsBubbleVisibleInView(DatumEnds.End1, active_view),
                    grid.IsHidden(active_view),
                )
        except Exception as e:
            return_value.append_message(
                "{}{}Grid {} through exception in view: {} exception: {}. Setting grid to not in scope for view.".format(
                    SPACER, SPACER, grid.Name, active_view.Name, e
                )
            )
            grid_visibility_data[id] = grid_properties(
                False, None, None, None, None, None, False
            )
    return_value.result.append(grid_visibility_data)
    return return_value


def change_grid_extends_in_views(
    doc, grids_in_model, grid_template_data, views_to_change_grid_elements, callback
):
    """
    Changes grids  in a number views to match the extend, visibility, bubble visibility of grids in template view

    :param doc: Current model document.
    :type doc: Autodesk.Revit.DB.Document
    :param grids_in_model: Grids in the model
    :type grids_in_model:  [Autodesk.Revit.DB.Grid]
    :param grid_template_data: A dictionary describing the appearance of each grid in the template view
    :type grid_template_data:  A named tuple: grid_properties
        bool, is the grid in scope (inside the crop region)
        # Datum Extent type at End 0,
        # Datum Extend type at End 1,
        curve, describing the start and end point of grid
        bool, # bubble visible at zero end
        bool, # bubble visible at 1 end
        bool # is the grid visible
    :param views_to_change_grid_elements: A list of views in which to update the grid graphics
    :type views_to_change_grid_elements: [Autodesk.Revit.DB.View]
    :param callback: A progress call back function
    :type views_to_change_grid_elements: :class:`.ProgressBase`
    """
    return_value = res.Result()

    # some type checking
    if isinstance(callback, ProgressBase) == False and callback is not None:
        return_value.update_sep(
            False,
            "Callback needs to inherit from ProgressBase or must be None. Got {} instead".format(
                type(callback)
            ),
        )
        return return_value

    try:
        view_counter = 0
        # loop over views and update grids based on template data
        for view in views_to_change_grid_elements:

            # update any progress call back
            if callback:
                callback.update(view_counter, len(views_to_change_grid_elements))

            return_value.append_message("Processing view: {}".format(view.Name))
            # get the grid z plane for the view
            new_grid_z_plane = get_grid_plane_z_value(grids_in_model, view)

            # loop over grid data
            for grid_id, item in grid_template_data.items():
                grid_element = doc.GetElement(grid_id)
                try:
                    # setup action to be performed in transaction
                    def action():
                        action_return_value = res.Result()
                        # check if grid is in scope of view
                        if item.is_grid_in_scope == True:
                            # check if grid vibility needs to be changed
                            if item.is_grid_hidden == True:
                                # check if grid is currently visible in view and needs to be hidden
                                if grid_element.IsHidden(view) == False:
                                    hide_ids = [grid_id]
                                    # hide the grid
                                    try:
                                        # need to convert into .net list
                                        view.HideElements(hide_ids.ToList[ElementId]())
                                        action_return_value.append_message(
                                            SPACER
                                            + "Hiding grid: {} in view: {}".format(
                                                grid_element.Name, view.Name
                                            )
                                        )
                                    except Exception as e:
                                        action_return_value.update_sep(
                                            False,
                                            "Hide grid, an exception ocurred: {}".format(
                                                e
                                            ),
                                        )
                                else:
                                    action_return_value.append_message(
                                        SPACER
                                        + "Grid: {} already hidden in view: {} No action required.".format(
                                            grid_element.Name, view.Name
                                        )
                                    )
                            else:
                                # check if grid is currently hidden in view and needs to be shown
                                try:
                                    if grid_element.IsHidden(view):
                                        un_hide_ids = [grid_id]
                                        view.UnhideElements(
                                            un_hide_ids.ToList[ElementId]()
                                        )
                                        action_return_value.append_message(
                                            SPACER
                                            + "Unhide grid: {} in view: {}".format(
                                                grid_element.Name, view.Name
                                            )
                                        )
                                except Exception as e:
                                    action_return_value.update_sep(
                                        False,
                                        "Unhide grid, an exception ocurred: {}".format(
                                            e
                                        ),
                                    )

                                # update other properties
                                action_return_value.append_message(
                                    SPACER
                                    + "Changing grid: {} properties in view: {}".format(
                                        grid_element.Name, view.Name
                                    )
                                )
                                # get the nested old curve from list
                                old_grid_curve = item.grid_curve[0]

                                # set extend types to match
                                grid_element.SetDatumExtentType(
                                    DatumEnds.End0, view, item.datum_extent_type_zero
                                )
                                grid_element.SetDatumExtentType(
                                    DatumEnds.End1, view, item.datum_extent_type_one
                                )

                                # set bubble visibility
                                if item.end_zero_bubble == True:
                                    grid_element.ShowBubbleInView(DatumEnds.End0, view)
                                else:
                                    grid_element.HideBubbleInView(DatumEnds.End0, view)
                                if item.end_one_bubble == True:
                                    grid_element.ShowBubbleInView(DatumEnds.End1, view)
                                else:
                                    grid_element.HideBubbleInView(DatumEnds.End1, view)

                                # set grid extend
                                start_point = XYZ(
                                    old_grid_curve.GetEndPoint(0).X,
                                    old_grid_curve.GetEndPoint(0).Y,
                                    new_grid_z_plane,
                                )
                                end_point = XYZ(
                                    old_grid_curve.GetEndPoint(1).X,
                                    old_grid_curve.GetEndPoint(1).Y,
                                    new_grid_z_plane,
                                )
                                new_grid_curve = Line.CreateBound(
                                    start_point, end_point
                                )

                                grid_element.SetCurveInView(
                                    DatumExtentType.ViewSpecific, view, new_grid_curve
                                )
                        else:
                            # grid is not in scope of this view
                            action_return_value.append_message(
                                SPACER
                                + "Grid: {} not in scope of view : {}".format(
                                    grid_element.Name, view.Name
                                )
                            )
                        return action_return_value

                    transaction = Transaction(doc, "Changing grid extends.")
                    result = rTran.in_transaction(transaction, action)
                    return_value.update(result)
                except Exception as e:
                    return_value.update_sep(
                        False,
                        "An exception ocurred when changing grid appearance: {}".format(
                            e
                        ),
                    )

            # check if cancelled
            if callback and callback.is_cancelled():
                return_value.append_message("User cancelled.")
                break

    except Exception as e:
        return_value.update_sep(
            False, "An exception occurred while changing grid extends: {}".format(e)
        )

    return return_value


def propagate_grids_extends_and_visibility(
    doc, views_to_change_grid_elements, callback=None
):
    """
    Propagates grid extends and visibility from the active view to all other views selected in UI.

    :param doc: Current model document.
    :type doc: Autodesk.Revit.DB.Document
    :param viewsToChangeGridElements: A list of views in which to update the grid graphics
    :type viewsToChangeGridElements: [Autodesk.Revit.DB.View]
    :param callback: A progress call back function
    :type views_to_change_grid_elements: :class:`.ProgressBase`

    :return:
        Result class instance.

        - result.status: True.
        - result.message will contain the names of the grids amended.
        - result.result an empty list

        On exception

        - result.status (bool) will be False
        - result.message will contain the exception message
    """

    return_value = res.Result()

    # some type checking
    if isinstance(callback, ProgressBase) == False and callback is not None:
        return_value.update_sep(
            False,
            "Callback needs to inherit from ProgressBase or must be None. Got {} instead".format(
                type(callback)
            ),
        )
        return return_value
    try:
        # get all grids in model
        grids_in_model = rGrids.get_grids_in_model(doc)
        if len(grids_in_model.ToElementIds()) > 0:
            # get active view grid information
            grid_data_result = get_active_view_grid_data(doc.ActiveView, grids_in_model)

            if grid_data_result.status == False:
                raise ValueError(grid_data_result.message)
            # get the grid template data
            grid_data = grid_data_result.result[0]

            # check if any views where provided
            if (
                views_to_change_grid_elements != None
                and len(views_to_change_grid_elements) > 0
            ):
                return_value.append_message(
                    "Amending grids in {} views:".format(
                        len(views_to_change_grid_elements)
                    )
                )

                # update grid extends
                result_change = change_grid_extends_in_views(
                    doc=doc,
                    grids_in_model=grids_in_model,
                    grid_template_data=grid_data,
                    views_to_change_grid_elements=views_to_change_grid_elements,
                    callback=callback,
                )
                return_value.update(result_change)
            else:
                return_value.append_message(
                    "No view to propagate grids extends to where provided."
                )
        else:
            return_value.append_message("No grids in model found.")
    except Exception as e:
        return_value.update_sep(
            False, "An exception occurred while propagating grid extends: {}".format(e)
        )
    return return_value
