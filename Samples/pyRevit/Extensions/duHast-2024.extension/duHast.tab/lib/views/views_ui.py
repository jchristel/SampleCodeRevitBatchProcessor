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



from duHast.Utilities.Objects.result import Result

from duHast.Revit.Views.views import (
    get_views_in_model
)



def get_views_in_model_not_template(doc):
    """
    Gets all views in a model which are not templates and not driven by a template.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: list of views
    :rtype: list of Autodesk.Revit.DB.View
    """

    def filter_not_template(view):
        return view.IsTemplate == False

    return get_views_in_model(doc=doc, filter=filter_not_template)





def _get_views_for_ui(doc):
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

    # get all views
    view_templates =get_views_in_model_not_template(doc=doc)
    for vt in view_templates:
        key = vt.Name
        view_template_names.append(key)
        view_templates_by_name[key] = vt

    return view_template_names, view_templates_by_name


def _get_source_views(doc, forms):
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
    view_template_name, view_templates_by_name = _get_views_for_ui(doc)

    # check if we got any?
    if len(view_template_name) == 0:
        return source_view_template

    # get the user to select the source ( returns a string)
    selection = forms.SelectFromList.show(
        sorted(view_template_name),
        button_name="Select Views To Propagate From",
        multiselect=False,
    )

    if selection == None:
        return source_view_template
    else:
        return view_templates_by_name[selection]




def _get_target_views(doc, forms, source_view_template_name):
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
    view_template_names, view_templates_by_name = _get_views_for_ui(doc)

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
        button_name="Select Views To Propagate To",
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
