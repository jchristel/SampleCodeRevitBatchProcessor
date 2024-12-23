from duHast.Revit.Views.templates import get_all_unused_view_template_ids
from duHast.Revit.Views.filters import get_all_unused_view_filters

from duHast.Revit.Views.schedules import get_schedules_not_on_sheets
from duHast.Revit.Views.views import get_views_not_on_sheet
from duHast.Revit.Views.legends import get_view_legends_not_placed
from duHast.Revit.Common.delete import delete_by_element_ids

from duHast.Utilities.Objects.result import Result

from Autodesk.Revit.DB import Element


def _get_elements_for_ui_from_element_ids(doc, element_ids):
    """
    Returns all elements of ids past in  in 2 variables:

    - 0 is element names ( list of strings)
    - 1 is a dictionary where the key is the element name and value is the actual element

    :param doc: The current Revit document.
    :type doc: Autodesk.Revit.DB.Document
    :param element_ids: A list of element ids to get the elements from for the UI.
    :type element_ids: [Autodesk.Revit.DB.ElementId]

    :return: A tuple of element names and elements by names.
    :rtype: ([str], {str: Autodesk.Revit.DB.Element})
    """

    # set up return values
    element_names = []
    elements_by_name = {}

    # get all elements from their ids
    elements = []

    for element_id in element_ids:
        element = doc.GetElement(element_id)
        elements.append(element)

    for element in elements:
        key = Element.Name.GetValue(element)
        element_names.append(key)
        if key in elements_by_name:
            print("Warning element {} exists twice in the model!".format(key))
        elements_by_name[key] = element

    return element_names, elements_by_name


def _get_elements_for_ui_from_views(views):
    """
    Returns all elements of ids past in  in 2 variables:

    - 0 is element names ( list of strings)
    - 1 is a dictionary where the key is the element name and value is the actual element

    :param views: A list of views to get to be displayed in the UI.
    :type views: [Autodesk.Revit.DB.View]

    :return: A tuple of view names and views by names.
    :rtype: ([str], {str: Autodesk.Revit.DB.View})

    """

    # set up return values
    element_names = []
    elements_by_name = {}

    for element in views:
        key = "{}_{}".format(Element.Name.GetValue(element), element.ViewType)
        element_names.append(key)
        if key in elements_by_name:
            print("Warning element {} exists twice in the model!".format(key))
        elements_by_name[key] = element

    return element_names, elements_by_name


def _get_user_selection(doc, forms, title, element_names, elements_by_names):
    """
    Gets the user to select elements from a list of elements.

    :param doc: The current Revit document.
    :type doc: Autodesk.Revit.DB.Document
    :param forms: pyRevit forms
    :type forms: pyRevit forms module
    :param title: The title of the selection dialog.
    :type title: str
    :param element_names: A list of element names to be displayed in the UI.
    :type element_names: [str]
    :param elements_by_names: A dictionary of element names and elements.
    :type elements_by_names: {str: Autodesk.Revit.DB.Element}

    :return: A list of selected elements.
    :rtype: [Autodesk.Revit.DB.Element]
    """

    elements_selected = None

    # check if we got any?
    if len(element_names) == 0:
        return elements_selected

    # get the user to select the source ( returns a string)
    selection = forms.SelectFromList.show(
        sorted(element_names), button_name=title, multiselect=True
    )

    if selection == None:
        return elements_selected
    else:
        elements_selected = []
        for filter_name in selection:
            elements_selected.append(elements_by_names[filter_name])
        return elements_selected


def purge_unused_view_templates(doc, output, forms):
    """
    Purges all unused view templates from a selection from the model.

    :param doc: The current Revit document.
    :type doc: Autodesk.Revit.DB.Document
    :param output: pyRevit output
    :type output: pyRevit output module
    :param forms: pyRevit forms
    :type forms: pyRevit forms module

    :return:
        Result class instance.

        - result.status (bool) True if view templates where purged without an exception, otherwise False.
        - result.message contains log messages.
        - result.result will be an empty list.

        On exception:

        - result.status (bool) will be False.
        - result.message will contain exception message.
    :rtype: :class:`.Result`
    """

    # set up a status tracker
    return_value = Result()

    # get unused template ids
    unused_template_ids = get_all_unused_view_template_ids(doc=doc)

    # get stuff for UI
    element_names, elements_by_names = _get_elements_for_ui_from_element_ids(
        doc=doc, element_ids=unused_template_ids
    )

    # get the user to select which templates to delete:
    selected_templates = _get_user_selection(
        doc=doc,
        forms=forms,
        title="Select templates to purge.",
        element_names=element_names,
        elements_by_names=elements_by_names,
    )

    if selected_templates == None:
        print(
            "No view template selected or no suitable view templates in file. Exiting."
        )
        return_value.update_sep(
            False, "No view template selected or no suitable view templates in file."
        )
        return return_value

    # delete templates by their ids
    ids_to_delete = []
    for selected_template in selected_templates:
        ids_to_delete.append(selected_template.Id)

    status_delete = delete_by_element_ids(
        doc=doc,
        ids=ids_to_delete,
        transaction_name="Purged view templates",
        element_name="view template(s)",
    )
    return_value.update(status_delete)

    print(status_delete.message)

    print("Finished.")
    return return_value


def purge_unused_view_filters(doc, output, forms):
    """
    Purges all unused view filters from a selection from the model.

    :param doc: The current Revit document.
    :type doc: Autodesk.Revit.DB.Document
    :param output: pyRevit output
    :type output: pyRevit output module
    :param forms: pyRevit forms
    :type forms: pyRevit forms module

    :return:
        Result class instance.

        - result.status (bool) True if view filters where purged without an exception, otherwise False.
        - result.message contains log messages.
        - result.result will be an empty list.

        On exception:

        - result.status (bool) will be False.
        - result.message will contain exception message.
    :rtype: :class:`.Result`
    """

    # set up a status tracker
    return_value = Result()

    # get unused filter ids
    unused_filter_ids = get_all_unused_view_filters(doc=doc)

    # get stuff for UI
    element_names, elements_by_names = _get_elements_for_ui_from_element_ids(
        doc=doc, element_ids=unused_filter_ids
    )

    # get the user to select which templates to delete:
    selected_filters = _get_user_selection(
        doc=doc,
        forms=forms,
        title="Select filters to purge.",
        element_names=element_names,
        elements_by_names=elements_by_names,
    )

    if selected_filters == None:
        print("No filters selected or no suitable filters in file. Exiting.")
        return_value.update_sep(
            False, "No filters selected or no suitable filters in file."
        )
        return return_value

    # delete templates by their ids
    ids_to_delete = []
    for selected_filter in selected_filters:
        ids_to_delete.append(selected_filter.Id)

    status_delete = delete_by_element_ids(
        doc=doc,
        ids=ids_to_delete,
        transaction_name="Purged filters",
        element_name="filter(s)",
    )
    return_value.update(status_delete)

    print(status_delete.message)

    print("Finished.")
    return return_value


def purge_unused_schedules(doc, output, forms):
    """
    Purges all schedules not placed on sheets from a selection from the model.

    :param doc: The current Revit document.
    :type doc: Autodesk.Revit.DB.Document
    :param output: pyRevit output
    :type output: pyRevit output module
    :param forms: pyRevit forms
    :type forms: pyRevit forms module

    :return:
        Result class instance.

        - result.status (bool) True if schedules where purged without an exception, otherwise False.
        - result.message contains log messages.
        - result.result will be an empty list.

        On exception:

        - result.status (bool) will be False.
        - result.message will contain exception message.
    :rtype: :class:`.Result`
    """

    # set up a status tracker
    return_value = Result()

    # get unused schedules
    schedules_not_on_sheets = get_schedules_not_on_sheets(doc=doc)

    # get stuff for UI
    element_names, elements_by_names = _get_elements_for_ui_from_views(
        views=schedules_not_on_sheets
    )

    # get the user to select which templates to delete:
    selected_schedules = _get_user_selection(
        doc=doc,
        forms=forms,
        title="Select schedules to purge.",
        element_names=element_names,
        elements_by_names=elements_by_names,
    )

    if selected_schedules == None:
        print("No schedules selected or no suitable schedules in file. Exiting.")
        return_value.update_sep(
            False, "No schedules selected or no suitable schedules in file."
        )
        return return_value

    # delete templates by their ids
    ids_to_delete = []
    for selected_schedule in selected_schedules:
        ids_to_delete.append(selected_schedule.Id)

    status_delete = delete_by_element_ids(
        doc=doc,
        ids=ids_to_delete,
        transaction_name="Purged schedules",
        element_name="schedule(s)",
    )
    return_value.update(status_delete)

    print(status_delete.message)

    print("Finished.")
    return return_value


def purge_unused_legends(doc, output, forms):
    """
    Purges all legends not placed on sheets from a selection from the model.

    :param doc: The current Revit document.
    :type doc: Autodesk.Revit.DB.Document
    :param output: pyRevit output
    :type output: pyRevit output module
    :param forms: pyRevit forms
    :type forms: pyRevit forms module

    :return:
        Result class instance.

        - result.status (bool) True if legends where purged without an exception, otherwise False.
        - result.message contains log messages.
        - result.result will be an empty list.

        On exception:

        - result.status (bool) will be False.
        - result.message will contain exception message.
    :rtype: :class:`.Result`
    """

    # set up a status tracker
    return_value = Result()

    # get unused legends
    legends_not_on_sheets = get_view_legends_not_placed(doc=doc)

    # get stuff for UI
    element_names, elements_by_names = _get_elements_for_ui_from_views(
        views=legends_not_on_sheets
    )

    # get the user to select which templates to delete:
    selected_legends = _get_user_selection(
        doc=doc,
        forms=forms,
        title="Select legends to purge.",
        element_names=element_names,
        elements_by_names=elements_by_names,
    )

    if selected_legends == None:
        print("No legends selected or no suitable legends in file. Exiting.")
        return_value.update_sep(
            False, "No legends selected or no suitable legends in file. Exiting."
        )
        return return_value

    # delete templates by their ids
    ids_to_delete = []
    for selected_legend in selected_legends:
        ids_to_delete.append(selected_legend.Id)

    status_delete = delete_by_element_ids(
        doc=doc,
        ids=ids_to_delete,
        transaction_name="Purged legends",
        element_name="legend(s)",
    )
    return_value.update(status_delete)

    print(status_delete.message)

    print("Finished.")
    return return_value


def purge_unplaced_views(doc, output, forms):
    """
    Purges all views not placed on sheets from a selection from the model.

    :param doc: The current Revit document.
    :type doc: Autodesk.Revit.DB.Document
    :param output: pyRevit output
    :type output: pyRevit output module
    :param forms: pyRevit forms
    :type forms: pyRevit forms module

    :return:
        Result class instance.

        - result.status (bool) True if views where purged without an exception, otherwise False.
        - result.message contains log messages.
        - result.result will be an empty list.

        On exception:

        - result.status (bool) will be False.
        - result.message will contain exception message.
    :rtype: :class:`.Result`
    """

    # set up a status tracker
    return_value = Result()

    # get unused legends
    views_not_on_sheets = get_views_not_on_sheet(doc=doc)

    # get stuff for UI
    element_names, elements_by_names = _get_elements_for_ui_from_views(
        views=views_not_on_sheets
    )

    # get the user to select which templates to delete:
    selected_legends = _get_user_selection(
        doc=doc,
        forms=forms,
        title="Select views to purge.",
        element_names=element_names,
        elements_by_names=elements_by_names,
    )

    if selected_legends == None:
        print("No views selected or no suitable views in file. Exiting.")
        return_value.update_sep(
            False, "No views selected or no suitable views in file. Exiting."
        )
        return return_value

    # delete templates by their ids
    ids_to_delete = []
    for selected_legend in selected_legends:
        ids_to_delete.append(selected_legend.Id)

    status_delete = delete_by_element_ids(
        doc=doc,
        ids=ids_to_delete,
        transaction_name="Purged views",
        element_name="view(s)",
    )
    return_value.update(status_delete)

    print(status_delete.message)

    print("Finished.")
    return return_value
