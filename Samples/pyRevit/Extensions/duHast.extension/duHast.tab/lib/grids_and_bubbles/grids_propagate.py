from duHast.Revit.Views.views import get_views_of_type
from duHast.Revit.Grids.grids_propagate_visbility_and_extends import (
    propagate_grids_extends_and_visibility,
)
from duHast.Revit.Grids.grids_extend_to_view_crop import _check_active_view_type
from duHast.Utilities.Objects.result import Result
from duHast.pyRevit.Objects.ProgressPyRevit import ProgressPyRevit

from Autodesk.Revit.DB import ViewType


def _get_views_for_ui(doc):
    """
    get views from the model of supported types

    - 0 is list of view names ( list of strings)
    - 1 is a dictionary where the key is the view name name and value is the actual view

    :param doc: The document containing views to be considered.
    :type doc: Autodesk.Revit.DB.Document

    :return: A tuple of view names and view elements by names.
    :rtype: ([str], {str: Autodesk.Revit.DB.View})

    """

    all_views = []

    # get plan views
    views_plan = get_views_of_type(doc=doc, view_type=ViewType.FloorPlan)
    all_views.extend(views_plan)

    # get Reflected Ceiling Plans
    views_rcp = get_views_of_type(doc=doc, view_type=ViewType.CeilingPlan)
    all_views.extend(views_rcp)

    # get area plans
    views_area = get_views_of_type(doc=doc, view_type=ViewType.AreaPlan)
    all_views.extend(views_area)

    # set up return values
    ui_view_list = []
    ui_view_list_to_view = {}

    # convert retrieved views into dictionary:
    for view in all_views:
        key = "{} ({})".format(view.Name, view.ViewType)
        ui_view_list.append(key)
        ui_view_list_to_view[key] = view

    return ui_view_list_to_view, ui_view_list


def _get_target_views(doc, forms):
    """
    Get user to select views to propagate grids to.

    This function retrieves all views of supported types from the given document
    and presents a selection interface to the user. The user can choose multiple
    views from this list. The function then returns the selected view elements.

    :param doc: The document containing views to be considered.
    :type doc: Document
    :param forms: A pyRevit forms object that includes a method for presenting selection UI.
    :type forms: pyRevit.Forms 1

    :return: A list of selected view elements.
    :rtype: [Autodesk.Revit.DB.View]
    """

    views_selected = []

    # get all views of supported types in the model
    views, views_for_ui = _get_views_for_ui(doc)

    # get the use to select the target views
    selection = forms.SelectFromList.show(
        sorted(views_for_ui),
        button_name="Select Views To Propagate To",
        multiselect=True,
    )

    if len(selection) == 0:
        return views_selected
    else:
        # get the actual views elements
        for view_name in selection:
            views_selected.append(views[view_name])

    return views_selected


def propagate_grids_to_views(doc, forms):
    """
    Propagates grids visibility from the active view to a number of views selected by the user.

    :param doc: The current Revit document.
    :type doc: Autodesk.Revit.DB.Document
    :param forms: pyRevit forms
    :type forms: pyRevit forms module

    :return:
        Result class instance.

        - result.status (bool) True if grids where propagated to target views without an exception, otherwise False.
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

    # check if view type is supported
    if _check_active_view_type(view=active_view) == False:
        return_value.update_sep(
            False, "Unsupported active view type: {}".format(active_view.ViewType)
        )
        print(
            "Active view type is not supported by this script: {}".format(
                active_view.ViewType
            )
        )
        print("View needs to be of type: Floor Plan, Ceiling Plan or Area Plan")
        return return_value

    # get the target views from user
    target_views = _get_target_views(doc, forms)

    # check if any target views got selected
    if len(target_views) == 0:
        return_value.update_sep(False, "User did not select any target views")
        print("No target views selected")
        return return_value

    # set up a pyRevit progress bar
    with forms.ProgressBar(
        title="Propagating grids visibility: {value} of {max_value}", cancellable=True
    ) as pb:

        # set up a call back for pyRevit progressbar
        progress_callback = ProgressPyRevit(form=pb)

        # propagate grids visibility in those target views
        return_value = propagate_grids_extends_and_visibility(
            doc=doc,
            views_to_change_grid_elements=target_views,
            callback=progress_callback,
        )

        # let the user know how things went
        if return_value.status:
            print("{}".format(return_value.message))
        else:
            print("Failed to apply grids to views: \n{}".format(return_value.message))

    print("Finished!")
    return return_value
