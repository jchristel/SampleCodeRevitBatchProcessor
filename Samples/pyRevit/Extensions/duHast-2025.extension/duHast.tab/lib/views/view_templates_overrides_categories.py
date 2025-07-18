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
from duHast.Revit.Views.visibility_graphics_categories import (
    get_category_overrides_from_view,
    apply_graphic_override_to_view,
    get_categories_and_subcategories_from_model,
)


from views.view_templates_ui import (
    _get_source_view_template,
    _get_target_view_templates,
)


def _get_categories_to_propagate(categories, forms):
    """
    returns the categories to propagate by user selection

    :param categories: categories to select from
    :type categories: dict
    :param forms: pyRevit forms module
    :type forms: module
    :return: selected categories
    :rtype: [:class:`.RevitCategoryOverride`]
    """

    ui_names = []
    for category_name, category_item in categories.items():
        ui_names.append(category_name)

    # get the user to select the source ( returns a string)
    selection = forms.SelectFromList.show(
        sorted(ui_names),
        button_name="Select View Template Categories To Propagate",
        multiselect=True,
    )

    categories_selected = []
    for category_name in selection:
        categories_selected.append(categories[category_name])
    return categories_selected


def apply_graphic_overrides_to_views(doc, forms):
    """
    Apply selected graphic overrides from one template to many other templates

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
    source_view_template = _get_source_view_template(doc, forms)
    if source_view_template == None:
        print(
            "No view template selected or no suitable view templates in file. Exiting."
        )
        return_value.update_sep(
            False, "No view template selected or no suitable view templates in file."
        )
        return return_value

    # get the target view templates
    target_view_templates = _get_target_view_templates(
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

    # get all categories available in model
    model_category_overrides = get_categories_and_subcategories_from_model(doc)

    # get user to select which overrides to propagate
    selected_categories = _get_categories_to_propagate(model_category_overrides, forms)

    # get source view category overrides of selected categories
    category_overrides_source_view = get_category_overrides_from_view(
        view=source_view_template, category_storage_instances=selected_categories
    )

    counter = 0
    # set up a pyrevit progress bar
    with forms.ProgressBar(
        title="applying graphic overrides: {value} of {max_value}", cancellable=True
    ) as pb:
        # apply overrides
        for target_view_template in target_view_templates:
            # update progress bar
            pb.update_progress(counter, len(target_view_templates))

            # apply overrides
            result_update = apply_graphic_override_to_view(
                doc=doc,
                view=target_view_template,
                category_storage_instances=category_overrides_source_view,
            )
            return_value.update(result_update)

            # check for cancel
            if pb.cancelled:
                return_value.update_sep(False, "User cancelled.")
                # get out of loop
                break

            # update progress
            counter = counter + 1

    print(return_value.message)

    return return_value
