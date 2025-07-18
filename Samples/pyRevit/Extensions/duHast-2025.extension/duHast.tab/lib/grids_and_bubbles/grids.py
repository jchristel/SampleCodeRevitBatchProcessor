# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2025, Jan Christel
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

from duHast.Revit.Grids.grids_appearance import (
    hide_both_bubbles,
    change_grids_2D,
    show_bubble_end,
    toggle_bubble_end,
)
from duHast.Revit.Grids.grids_extend_to_view_crop import (
    extend_linear_grids_to_crop_box_of_view,
)
from duHast.Revit.Grids.grids import get_grids_in_view
from duHast.Utilities.Objects.result import Result

from duHast.Revit.UI.custom_selection_user import get_user_selection


from Autodesk.Revit.DB import DatumEnds


def switch_all_bubbles_off_in_view(doc):
    """
    Switches all grid bubbles off in the active view.

    :param doc: The current Revit document.
    :type doc: Autodesk.Revit.DB.Document
    """

    # get the active view
    active_view = doc.ActiveView

    # get all grids
    grids = get_grids_in_view(doc, active_view)

    # attempt to switch off all bubbles in view
    result = hide_both_bubbles(doc=doc, grids=grids, view=active_view)

    # let the user know how things went
    if result.status:
        print("Switching off all grid bubbles in view: \n{}".format(result.message))
    else:
        print("Failed to switch off grid bubbles: \n{}".format(result.message))

    print("Finished!")


def switch_0_end_bubbles_on_in_view(doc):
    """
    Switches off 0 end ( the start ) bubble of all grids visible in a view.

    :param doc: The current Revit document.
    :type doc: Autodesk.Revit.DB.Document

    :return:
        Result class instance.

        - result.status (bool) True if grid bubbles where switched on in active views without an exception, otherwise False.
        - result.message contains log messages.
        - result.result will be an empty list.

        On exception:

        - result.status (bool) will be False.
        - result.message will contain exception message.
    :rtype: :class:`.Result`
    """

    # set up a status instance
    return_value = Result()

    # get the active view
    active_view = doc.ActiveView

    # get all grids
    grids = get_grids_in_view(doc, active_view)

    # set up a counter to check whether anything was switched on
    counter = 0
    # loop over grids and toggle off 0 end
    for grid in grids:
        counter += 1
        result_show = show_bubble_end(
            doc=doc,
            grid=grid,
            view=active_view,
            end_identifier=DatumEnds.End0,
            show_bubble=True,
        )
        return_value.update(result_show)

    if counter == 0:
        print("No grids visible in view: {}".format(active_view.Name))
    else:
        print(
            "Switching on grid bubbles to start in view: \n{}".format(
                return_value.message
            )
        )

    print("Finished!")
    return return_value


def switch_1_end_bubbles_on_in_view(doc):
    """
    Switches off 1 end ( the end ) bubble of all grids visible in a view

    :param doc: The current Revit document.
    :type doc: Autodesk.Revit.DB.Document

    :return:
        Result class instance.

        - result.status (bool) True if grid bubbles where switched on in active views without an exception, otherwise False.
        - result.message contains log messages.
        - result.result will be an empty list.

        On exception:

        - result.status (bool) will be False.
        - result.message will contain exception message.
    :rtype: :class:`.Result`
    """

    # set up a status instance
    return_value = Result()

    # get the active view
    active_view = doc.ActiveView

    # get all grids
    grids = get_grids_in_view(doc, active_view)

    # set up a counter to check whether anything was switched on
    counter = 0
    # loop over grids and toggle off 0 end
    for grid in grids:
        counter += 1
        result_show = show_bubble_end(
            doc=doc,
            grid=grid,
            view=active_view,
            end_identifier=DatumEnds.End1,
            show_bubble=True,
        )
        return_value.update(result_show)

    if counter == 0:
        print("No grids visible in view: {}".format(active_view.Name))
    else:
        print(
            "Switching on grid bubbles to end in view: \n{}".format(
                return_value.message
            )
        )

    print("Finished!")
    return return_value


def selection_filter_grids(elem):
    """
    Returns True if the element is of category grids

    :param elem: A revit element
    :type elem: Autodesk.Revit.DB.Element
    :return: True if the element is of category grids, otherwise False
    :rtype: bool
    """

    categories = ["Grids"]
    if elem.Category.Name in categories:
        return True
    else:
        return False


def _toggle_grid_by_selection(doc, uiapp, end_identifier):
    """
    Toggles the visibility of grid bubbles of selected grids at specified end.

    :param doc: The current Revit document.
    :type doc: Autodesk.Revit.DB.Document
    :param uiapp: The current Revit application.
    :type uiapp: Autodesk.Revit.UI.UIApplication
    :param end_identifier: The end identifier to toggle.
    :type end_identifier: Autodesk.Revit.DB.DatumEnds

    :return:
        Result class instance.

        - result.status (bool) True if grid bubbles of selected grids where toggled in active views without an exception, otherwise False.
        - result.message contains log messages.
        - result.result will be an empty list.

        On exception:

        - result.status (bool) will be False.
        - result.message will contain exception message.
    :rtype: :class:`.Result`
    """

    # set up a status instance
    return_value = Result()

    # get user to select grids
    grids_selected_result = get_user_selection(
        doc=doc,
        uidoc=uiapp.ActiveUIDocument,
        ui_text="Select Grids",
        selection_filter=selection_filter_grids,
    )

    # get the active view
    active_view = doc.ActiveView

    # check if grids where selected
    if grids_selected_result.status == False:
        return_value.update(grids_selected_result)
        print("Failed to select grids: {}".format(grids_selected_result.message))
        return return_value

    # get the actual grids selected
    grids_selected = grids_selected_result.result[0]
    if len(grids_selected) == 0:
        print("No grids where selected. Exiting.")
        return

    # loop over all grids selected and toggle away
    for grid in grids_selected:
        result_toggle = toggle_bubble_end(
            doc=doc, grid=grid, view=active_view, end_identifier=end_identifier
        )
        return_value.update(result_toggle)

    # let the user know how things went
    if return_value.status:
        print(
            "Toggled grid bubbles for all selected grids in view: \n{}".format(
                return_value.message
            )
        )
    else:
        print(
            "Failed to toggle grid bubbles for all selected grids in view:: \n{}".format(
                return_value.message
            )
        )

    return return_value


def toggle_grids_at_0_end_by_selection(doc, uiapp):
    """
    Toggles the visibility of grid bubbles of selected grids at zero end.

    :param doc: The current Revit document.
    :type doc: Autodesk.Revit.DB.Document
    :param uiapp: The current Revit application.
    :type uiapp: Autodesk.Revit.UI.UIApplication

    :return:
        Result class instance.

        - result.status (bool) True if grid bubbles of selected grids on 0 end where toggled in active views without an exception, otherwise False.
        - result.message contains log messages.
        - result.result will be an empty list.

        On exception:

        - result.status (bool) will be False.
        - result.message will contain exception message.
    :rtype: :class:`.Result`
    """

    # toggle away
    toggle_end_status = _toggle_grid_by_selection(
        doc=doc, uiapp=uiapp, end_identifier=DatumEnds.End0
    )

    return toggle_end_status


def toggle_grids_at_1_end_by_selection(doc, uiapp):
    """
    Toggles the visibility of grid bubbles of selected grids at one end.

    :param doc: The current Revit document.
    :type doc: Autodesk.Revit.DB.Document
    :param uiapp: The current Revit application.
    :type uiapp: Autodesk.Revit.UI.UI

    :return:
        Result class instance.

        - result.status (bool) True if grid bubbles of selected grids one 1 end where toggled in active views without an exception, otherwise False.
        - result.message contains log messages.
        - result.result will be an empty list.

        On exception:

        - result.status (bool) will be False.
        - result.message will contain exception message.
    :rtype: :class:`.Result`
    """

    # toggle away
    toggle_end_status = _toggle_grid_by_selection(
        doc=doc, uiapp=uiapp, end_identifier=DatumEnds.End1
    )

    return toggle_end_status


def set_grids_in_view_to_2d(doc):
    """
    Sets all ends of grids visible in a view to 2D

    :param doc: The current Revit document.
    :type doc: Autodesk.Revit.DB.Document

    :return: None
    """

    # get the active view
    active_view = doc.ActiveView

    # get all grids
    grids = get_grids_in_view(doc, active_view)

    # attempt to set grids to 2D in view
    return_value = change_grids_2D(doc=doc, grids=grids, view=active_view)

    # let the user know how things went
    if return_value.status:
        print("Switching all grids to 2D in view: \n{}".format(return_value.message))
    else:
        print("Failed to switch all grids to 2D: \n{}".format(return_value.message))

    print("Finished!")


def extend_grids_to_view_crop(doc):
    """
    Extends linear grids to the view crop.

    Requires the view to be of type Floor Plan, Ceiling Plan or Area Plan and the crop to be enabled.

    :param doc: The current Revit document.
    :type doc: Autodesk.Revit.DB.Document

    :return:
        Result class instance.

        - result.status (bool) True if grid where extended to the view crop in active views without an exception, otherwise False.
        - result.message contains log messages.
        - result.result will be an empty list.

        On exception:

        - result.status (bool) will be False.
        - result.message will contain exception message.
    :rtype: :class:`.Result`
    """

    # set up a status instance
    return_value = Result()

    # get the active view
    active_view = doc.ActiveView

    # attempt to extend linear grids
    return_value = extend_linear_grids_to_crop_box_of_view(doc=doc, view=active_view)

    # let the user know how things went
    if return_value.status:
        print("Extend all grids to view crop: \n{}".format(return_value.message))
    else:
        print(
            "Failed to extend all grids to view crop: \n{}".format(return_value.message)
        )

    print("Finished!")
    return return_value
