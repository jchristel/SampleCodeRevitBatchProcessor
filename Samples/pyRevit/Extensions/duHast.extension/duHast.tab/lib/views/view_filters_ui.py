from duHast.Revit.Views.filters import get_all_filters


def _get_filters_for_ui(doc):
    """
    Returns all view filters in the model in 2 variables:

    - 0 is filter names ( list of strings)
    - 1 is a dictionary where the key is the filter name and value is the actual view template

    :param doc: The current model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: filter names, filters by name
    :rtype: [str, {str: :class:`.ViewFilter`}]
    """

    # set up return values
    filter_names = []
    filters_by_name = {}

    # get all view templates
    filters = get_all_filters(doc=doc)
    for filter in filters:
        key = filter.Name
        filter_names.append(key)
        if key in filters_by_name:
            print("Warning filter {} exists twice in the model!".format(key))
        filters_by_name[key] = filter

    return filter_names, filters_by_name


def _get_selected_filters(doc, forms):
    """
    returns the view filters by user selection

    :param doc: The current model document.
    :type doc: Autodesk.Revit.DB.Document
    :param forms: pyRevit forms module
    :type forms: module

    :return: selected view filters
    :rtype: [Autodesk.Revit.DB.ParameterFilterElement]
    """
    
    filters_selected = None

    # get view templates in the model which allow graphical overrides
    filter_names, filters_by_names = _get_filters_for_ui(doc)

    # check if we got any?
    if len(filter_names) == 0:
        return filters_selected

    # get the user to select the source ( returns a string)
    selection = forms.SelectFromList.show(
        sorted(filter_names), button_name="Select Filters", multiselect=True
    )

    if selection == None:
        return filters_selected
    else:
        filters_selected = []
        for filter_name in selection:
            filters_selected.append(filters_by_names[filter_name])
        return filters_selected
