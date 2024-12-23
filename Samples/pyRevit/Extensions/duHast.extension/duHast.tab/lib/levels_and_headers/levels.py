from duHast.Revit.Levels.levels_appearance import (
    hide_both_heads,
    change_levels_2D,
    show_head_end,
    toggle_head_end,
)
from duHast.Revit.Levels.levels import get_levels_in_view
from duHast.Utilities.Objects.result import Result

from duHast.Revit.UI.custom_selection_user import get_user_selection

from Autodesk.Revit.DB import DatumEnds


def switch_all_headers_off_in_view(doc):
    """
    Switches all level headers off in the active view.

    :param doc: The current Revit document.
    :type doc: Autodesk.Revit.DB.Document

    :return: None
    """

    # get the active view
    active_view = doc.ActiveView

    # get all levels
    levels = get_levels_in_view(doc, active_view)

    # attempt to switch off all headers in view
    result = hide_both_heads(doc=doc, levels=levels, view=active_view)

    # let the user know how things went
    if result.status:
        print("Switching off all level headers in view: \n{}".format(result.message))
    else:
        print("Failed to switch off level headers: \n{}".format(result.message))

    print("Finished!")


def switch_0_end_headers_on_in_view(doc):
    """
    Switches off 0 end ( the start ) bubble of all levels visible in a view.

    :param doc: The current Revit document.
    :type doc: Autodesk.Revit.DB.Document

    :return: None
    """

    # set up a status instance
    return_value = Result()

    # get the active view
    active_view = doc.ActiveView

    # get all levels
    levels = get_levels_in_view(doc, active_view)

    # set up a counter to check whether anything was switched on
    counter = 0
    # loop over levels and toggle off 0 end
    for level in levels:
        counter += 1
        result_show = show_head_end(
            doc=doc,
            level=level,
            view=active_view,
            end_identifier=DatumEnds.End0,
            show_head=True,
        )
        return_value.update(result_show)

    if counter == 0:
        print("No levels visible in view: {}".format(active_view.Name))
    else:
        print(
            "Switching on level headers to start in view: \n{}".format(
                return_value.message
            )
        )

    print("Finished!")


def switch_1_end_headers_on_in_view(doc):
    """
    Switches off 1 end ( the end ) bubble of all levels visible in a view.

    :param doc: The current Revit document.
    :type doc: Autodesk.Revit.DB.Document

    :return: None
    """

    # set up a status instance
    return_value = Result()

    # get the active view
    active_view = doc.ActiveView

    # get all levels
    levels = get_levels_in_view(doc, active_view)

    # set up a counter to check whether anything was switched on
    counter = 0
    # loop over levels and toggle off 0 end
    for level in levels:
        counter += 1
        result_show = show_head_end(
            doc=doc,
            level=level,
            view=active_view,
            end_identifier=DatumEnds.End1,
            show_head=True,
        )
        return_value.update(result_show)

    if counter == 0:
        print("No levels visible in view: {}".format(active_view.Name))
    else:
        print(
            "Switching on level headers to end in view: \n{}".format(
                return_value.message
            )
        )

    print("Finished!")


def selection_filter_levels(elem):
    """
    Returns True if the element is of category levels

    :param elem: A revit element
    :type elem: Autodesk.Revit.DB.Element

    :return: True if the element is of category levels, otherwise False
    :rtype: bool
    """

    categories = ["Levels"]
    if elem.Category.Name in categories:
        return True
    else:
        return False


def _toggle_level_by_selection(doc, uiapp, end_identifier):
    """
    Toggles the visibility of level headers of selected levels at specified end.

    :param doc: The current Revit document.
    :type doc: Autodesk.Revit.DB.Document
    :param uiapp: The current Revit UI application.
    :type uiapp: Autodesk.Revit.UI.UIApplication
    :param end_identifier: The end identifier to toggle
    :type end_identifier: Autodesk.Revit.DB.DatumEnds

    :return:
        Result class instance.

        - result.status (bool) True if level header visibility where toggled without an exception, otherwise False.
        - result.message contains log messages.
        - result.result will be an empty list.

        On exception:

        - result.status (bool) will be False.
        - result.message will contain exception message.
    :rtype: :class:`.Result`
    """

    # set up a status instance
    return_value = Result()

    # get user to select levels
    levels_selected_result = get_user_selection(
        doc=doc,
        uidoc=uiapp.ActiveUIDocument,
        ui_text="Select levels",
        selection_filter=selection_filter_levels,
    )

    # get the active view
    active_view = doc.ActiveView

    # check if levels where selected
    if levels_selected_result.status == False:
        return_value.update(levels_selected_result)
        print("Failed to select levels: {}".format(levels_selected_result.message))
        return return_value

    # get the actual levels selected
    levels_selected = levels_selected_result.result[0]
    if len(levels_selected) == 0:
        print("No levels where selected. Exiting.")
        return

    # loop over all levels selected and toggle away
    for level in levels_selected:
        result_toggle = toggle_head_end(
            doc=doc, level=level, view=active_view, end_identifier=end_identifier
        )
        return_value.update(result_toggle)

    # let the user know how things went
    if return_value.status:
        print(
            "Toggled level headers for all selected levels in view: \n{}".format(
                return_value.message
            )
        )
    else:
        print(
            "Failed to toggle level headers for all selected levels in view:: \n{}".format(
                return_value.message
            )
        )

    return return_value


def toggle_levels_at_0_end_by_selection(doc, uiapp):
    """
    Toggles the visibility of level headers of selected levels at zero end.

    :param doc: The current Revit document.
    :type doc: Autodesk.Revit.DB.Document
    :param uiapp: The current Revit UI application.
    :type uiapp: Autodesk.Revit.UI.UIApplication

    :return:
        Result class instance.

        - result.status (bool) True if level header visibility where toggled without an exception, otherwise False.
        - result.message contains log messages.
        - result.result will be an empty list.

        On exception:

        - result.status (bool) will be False.
        - result.message will contain exception message.
    :rtype: :class:`.Result`
    """

    # toggle away
    toggle_end_status = _toggle_level_by_selection(
        doc=doc, uiapp=uiapp, end_identifier=DatumEnds.End0
    )

    return toggle_end_status


def toggle_levels_at_1_end_by_selection(doc, uiapp):
    """
    Toggles the visibility of level headers of selected levels at one end.

    :param doc: The current Revit document.
    :type doc: Autodesk.Revit.DB.Document
    :param uiapp: The current Revit UI application.
    :type uiapp: Autodesk.Revit.UI.UIApplication

    :return:
        Result class instance.

        - result.status (bool) True if level header visibility where toggled without an exception, otherwise False.
        - result.message contains log messages.
        - result.result will be an empty list.

        On exception:

        - result.status (bool) will be False.
        - result.message will contain exception message.
    :rtype: :class:`.Result`
    """

    # toggle away
    toggle_end_status = _toggle_level_by_selection(
        doc=doc, uiapp=uiapp, end_identifier=DatumEnds.End1
    )

    return toggle_end_status


def set_levels_in_view_to_2d(doc):
    """
    Sets all ends of levels visible in a view to 2D

    :param doc: The current Revit document.
    :type doc: Autodesk.Revit.DB.Document

    :return: None
    """

    # get the active view
    active_view = doc.ActiveView

    # get all levels
    levels = get_levels_in_view(doc, active_view)

    # attempt to set levels to 2D in view
    return_value = change_levels_2D(doc=doc, levels=levels, view=active_view)

    # let the user know how things went
    if return_value.status:
        print("Switching all levels to 2D in view: \n{}".format(return_value.message))
    else:
        print("Failed to switch all levels to 2D: \n{}".format(return_value.message))

    print("Finished!")
