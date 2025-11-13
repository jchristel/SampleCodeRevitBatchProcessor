from duHast.Utilities.Objects.result import Result
from duHast.Revit.Views.templates import (
    get_view_template_which_allow_graphical_overrides,
)


def _get_view_templates_for_ui(doc):
    """
    Returns all view templates in the model which allow graphic overrides in 2 variables:

    - 0 is view template names ( list of strings)
    - 1 is a dictionary where the key is the view template name and value is the actual view template

    :param doc: The current model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: view_template_names, view_templates_by_name
    :rtype: [str], {str: Autodesk.Revit.DB.View}
    """

    # set up return values
    view_template_names = []
    view_templates_by_name = {}

    # get all view templates
    view_templates = get_view_template_which_allow_graphical_overrides(doc=doc)
    for vt in view_templates:
        key = vt.Name
        view_template_names.append(key)
        view_templates_by_name[key] = vt

    return view_template_names, view_templates_by_name


def _get_source_view_template(doc, forms,button_name="Select View Template To Propagate From"):
    """
    returns the source view template by user selection

    :param doc: The current model document.
    :type doc: Autodesk.Revit.DB.Document
    :param forms: pyRevit forms module
    :type forms: module

    :return: source_view_template
    :rtype: Autodesk.Revit.DB.View
    """

    source_view_template = None

    # get view templates in the model which allow graphical overrides
    view_template_name, view_templates_by_name = _get_view_templates_for_ui(doc)

    # check if we got any?
    if len(view_template_name) == 0:
        return source_view_template

    # get the user to select the source ( returns a string)
    selection = forms.SelectFromList.show(
        sorted(view_template_name),
        button_name=button_name,
        multiselect=False,
    )

    if selection == None:
        return source_view_template
    else:
        return view_templates_by_name[selection]


def _get_target_view_templates(doc, forms, source_view_template_name, button_name="Select View Template To Propagate To"):
    """
    returns the target view template by user selection

    :param doc: The current model document.
    :type doc: Autodesk.Revit.DB.Document
    :param forms: pyRevit forms module
    :type forms: module
    :param source_view_template_name: The name of the source view template to exclude from the list of target view templates.
    :type source_view_template_name: str

    :return: target_view_templates
    :rtype: [Autodesk.Revit.DB.View]
    """

    target_view_templates = []

    # get view templates in the model which allow graphical overrides
    view_template_names, view_templates_by_name = _get_view_templates_for_ui(doc)

    # check if we got any?
    if len(view_template_names) == 0:
        return target_view_templates

    # remove source view template name
    if (
        source_view_template_name != None
        and source_view_template_name in view_template_names
    ):
        view_template_names.remove(source_view_template_name)

    # get the user to select the source ( returns a string)
    selection = forms.SelectFromList.show(
        sorted(view_template_names),
        button_name=button_name,
        multiselect=True,
    )

    # print (selection, type(selection))

    if selection is None or len(selection) == 0:
        return target_view_templates
    else:
        for target_view_template_name in selection:
            target_view_templates.append(
                view_templates_by_name[target_view_template_name]
            )
        return target_view_templates
