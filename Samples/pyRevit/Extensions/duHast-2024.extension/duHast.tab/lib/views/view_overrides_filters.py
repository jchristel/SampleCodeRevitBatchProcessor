from duHast.Utilities.Objects.result import Result


from duHast.Revit.Views.filters import get_filter_ids_from_view_by_filter
from duHast.Revit.Views.visibility_graphics_filters import (
    get_filters_from_model,
    update_filter_override_from_view,
    apply_filter_override_to_view,
    remove_filter_from_view,
)

from duHast.pyRevit.console_output import print_header

from views.views_ui import (
    _get_source_views,
    _get_target_views,
)

from views.view_filters_ui import _get_selected_filters

from Autodesk.Revit.DB import Element

def _get_filters_to_propagate(doc, forms, source_view_template):
    """
    Get the user to select filters of which to apply the overrides to other templates

    :param doc: The current model document.
    :type doc: Autodesk.Revit.DB.Document
    :param forms: pyRevit forms module
    :type forms: module
    :param source_view_template: The view template from which the filters are to be propagated.
    :type source_view_template: Autodesk.Revit.DB.View

    :return: selected filters
    :rtype: [Autodesk.Revit.DB.ParameterFilterElement]
    """

    # get all filters applied to template
    filter_id_in_source_template = get_filter_ids_from_view_by_filter(
        view=source_view_template, unique_list=[]
    )
    if len(filter_id_in_source_template) == 0:
        print("No filters applied to selected view template.")
        return None

    filter_names = []
    filters_by_names = {}
    # get user to select filters they want to use
    for filter_id in filter_id_in_source_template:
        filter = doc.GetElement(filter_id)
        filter_name = Element.Name.GetValue(filter)
        filter_names.append(filter_name)
        filters_by_names[filter_name] = filter

    # get the user to select the source ( returns a string)
    selection = forms.SelectFromList.show(
        sorted(filter_names),
        button_name="Select Filter Override To Propagate",
        multiselect=True,
    )

    # check if anything was selected
    if selection == None or len(selection) == 0:
        return None

    # get the actual filter override objects from the names selected
    filters_selected = []
    for filter_name in selection:
        filters_selected.append(filters_by_names[filter_name])

    return filters_selected


def _apply_filter_overrides(
    doc, source_view, target_views, filters, add_filter_if_not_present
):
    """
    Apply selected filter overrides from one template to many other templates

    :param doc: The current model document.
    :type doc: Autodesk.Revit.DB.Document
    :param source_view: The view template from which the filters are to be propagated.
    :type source_view: Autodesk.Revit.DB.View
    :param target_views: The view templates to which the filters are to be propagated.
    :type target_views: list
    :param filters: The filters to be propagated.
    :type filters: [Autodesk.Revit.DB.ParameterFilterElement]
    :param add_filter_if_not_present: If True, add filter if not present in target view
    :type add_filter_if_not_present: bool

    :return:
        Result class instance.

        - result.status (bool) will be True if successful.
        - result.message will contain the log messages.
        - result.result will be an empty list.

        On exception:

        - result.status (bool) will be False.
        - result.message will contain exception message.

    :rtype: :class:`.Result`:return:
    """

    # set up a status tracker
    return_value = Result()

    # get all filters in model as filter override storage objects
    # as a dictionary: str:RevitFilterOverride
    all_filter_overrides = get_filters_from_model(doc=doc)

    selected_filter_overrides = []
    # filter out the ones we are after:
    for selected_filter in filters:
        for filter_override_name, filter_override in all_filter_overrides.items():
            if selected_filter.Id == filter_override.filter_id:
                selected_filter_overrides.append(filter_override)

    # print("got overrides: {}".format(len(selected_filter_overrides)))

    # update filter override with source view settings
    for selected_filter in selected_filter_overrides:
        # print("before:",selected_filter)
        selected_filter = update_filter_override_from_view(
            view=source_view, filter_storage_instance=selected_filter
        )
        # print("after:",selected_filter)

    # apply filter overrides to target templates
    for target in target_views:
        print_header("Applying filter(s) to view template: {}".format(target.Name))
        result = apply_filter_override_to_view(
            doc=doc,
            view=target,
            filter_storage_instances=selected_filter_overrides,
            add_filter_if_not_present=add_filter_if_not_present,
        )
        return_value.update(result)
        print(result.message)

    return return_value


def apply_filter_overrides_to_views(doc, add_filter_if_not_present, forms):
    """
    Apply selected filter overrides from one template to many other templates

    :param doc: The current model document.
    :type doc: Autodesk.Revit.DB.Document
    :param add_filter_if_not_present: If True, add filter if not present in target view
    :type add_filter_if_not_present: bool
    :param forms: pyRevit forms module
    :type forms: module

    :return:
        Result class instance.

        - result.status (bool) will be True if successful.
        - result.message will contain the log messages.
        - result.result will be an empty list.

        On exception:

        - result.status (bool) will be False.
        - result.message will contain exception message.

    :rtype: :class:`.Result`:return:
    """

    # set up a status tracker
    return_value = Result()

    # get the source view template
    source_view_template =_get_source_views(doc, forms)
    if source_view_template == None:
        print(
            "No view template selected or no suitable view templates in file. Exiting."
        )
        return_value.update_sep(
            False, "No view template selected or no suitable view templates in file."
        )
        return return_value

    # get the target view templates
    target_view_templates =_get_target_views(
        doc, forms, source_view_template.Name
    )
    if len(target_view_templates) == 0:
        print(
            "No target view template(s) selected or no suitable view templates in file. Exiting."
        )
        return_value.update_sep(
            False,
            "No target view template(s) selected or no suitable view templates in file.",
        )
        return return_value

    # get the filters applied in the selected source template:
    source_filter_overrides = _get_filters_to_propagate(
        doc=doc, forms=forms, source_view_template=source_view_template
    )

    if source_filter_overrides == None or len(source_filter_overrides) == 0:
        print("No source filters selected.")
        return_value.update_sep(False, "No source filters selected.")
        return return_value

    if source_filter_overrides == None:
        print("No filters to propagate of overrides of selected. Exiting.")
        return_value.update_sep(
            False, "No filters to propagate overrides of selected. \nExiting."
        )
        return return_value

    # apply overrides to other views
    apply_status = _apply_filter_overrides(
        doc=doc,
        source_view=source_view_template,
        target_views=target_view_templates,
        filters=source_filter_overrides,
        add_filter_if_not_present=add_filter_if_not_present,
    )

    return_value.update(apply_status)

    print("Finished")
    return return_value