"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to Revit visibility graphics settings. 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2023, Jan Christel
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

from duHast.Utilities.Objects import result as res

from duHast.Utilities.files_json import read_json_data_from_file

from duHast.Revit.Views.filters import apply_filter_to_view
from duHast.Revit.Views.Objects.view_graphics_settings import ViewGraphicsSettings
from duHast.Revit.Views.Reporting.views_data_report import PROP_VIEW_DATA
from duHast.Revit.Views.templates import get_view_templates
from duHast.Revit.Views.Utility.convert_revit_override_to_data import get_view_settings
from duHast.Revit.Views.Utility.convert_data_to_override_storage import (
    convert_to_category_override_storage_objects,
    convert_to_filter_override_storage_objects,
)
from duHast.Revit.Views.visibility_graphics_filters import apply_filter_override_to_view
from duHast.Revit.Views.visibility_graphics_categories import (
    apply_graphic_override_to_view,
)

from duHast.Revit.LinePattern.line_patterns import build_patterns_dictionary_by_name
from duHast.Revit.LinePattern.fill_patterns import pattern_ids_by_name
from duHast.Revit.Common.Objects.Data.pattern_settings_base import PatternSettingBase

from Autodesk.Revit.DB import Element, LinePatternElement


def import_graphic_overrides(file_path, call_back):
    """
    Reads JSON data from a file and converts it into a dictionary of ViewGraphicsSettings objects.

    Args:
        file_path (str): The fully qualified file path of the JSON file.
        call_back (function): A callback function to update the progress of the data import.

    Returns:
        dict: A dictionary of ViewGraphicsSettings objects, where the view name is the key and the ViewGraphicsSettings object is the value.
    """
    return_value = res.Result()
    # print("ini: {}".format(return_value))
    view_overrides_data = {}
    json_data = read_json_data_from_file(file_path)
    counter = 1
    if PROP_VIEW_DATA in json_data:
        for json_override in json_data[PROP_VIEW_DATA]:
            view_override = ViewGraphicsSettings(j=json_override)
            view_overrides_data[view_override.view_name] = view_override
            return_value.append_message(
                "reading template: {} :: {} of {}".format(
                    view_override.view_name, counter, len(json_data[PROP_VIEW_DATA])
                )
            )
            counter = counter + 1
            # call back update
            if call_back:
                call_back(counter, len(json_data[PROP_VIEW_DATA]))
    else:
        return_value.update_sep(
            False, "File {} contains no view data.".format(file_path)
        )
    return_value.result.append(view_overrides_data)
    return return_value


def _check_pattern_in_model(pattern_from_model, pattern_data):
    """
    Check whether the line or fill patterns used in the given pattern data exist in the Revit model.

    Args:
        pattern_from_model (dict): A dictionary containing the line or fill patterns in the Revit model.
        pattern_data (dict): A dictionary containing the line or fill patterns to be checked.

    Returns:
        Result: A Result object containing the results of the pattern check.
    """

    return_value = res.Result()
    no_match = []

    for key, value in pattern_data.items():
        # ignore any pattern with -1 as id...its the default for no pattern assigned
        if value.id != -1:
            if key not in pattern_from_model:
                return_value.update_sep(
                    False, "{}......does not exist in model.".format(key)
                )
                no_match.append(key)
            else:
                return_value.update_sep(True, "{}......exists in model.".format(key))
        else:
            return_value.update_sep(True, "{}......ignored -1".format(key))

    if not return_value.status:
        return_value.result.append(no_match)

    return return_value


def check_line_patterns_are_in_model(doc, line_pattern_data):
    """
    Check whether the line patterns used in the `line_pattern_data` exist in the Revit model.

    Args:
        doc (Revit Document): The Revit document object.
        line_pattern_data (dictionary): A dictionary containing line pattern data.

    Returns:
        Result: A Result object containing the results of the line pattern check.
    """
    return_value = res.Result()
    all_line_pattern_in_model = build_patterns_dictionary_by_name(doc=doc)
    # append solid line pattern as it is  a special case inn the api
    all_line_pattern_in_model[PatternSettingBase.SOLID_PATTERN] = [
        LinePatternElement.GetSolidPatternId()
    ]
    # check line pattern in model against line pattern in data
    return_value.update(
        _check_pattern_in_model(
            pattern_from_model=all_line_pattern_in_model, pattern_data=line_pattern_data
        )
    )
    return return_value


def check_fill_patterns_are_in_model(doc, fill_pattern_data):
    """
    Check whether all fill patterns used in the fill_pattern_data exist in the Revit model.

    Args:
        doc (Revit Document): The Revit document object.
        fill_pattern_data (dict): A dictionary containing fill pattern data.

    Returns:
        Result: A Result object containing the results of the fill pattern check.
    """
    return_value = res.Result()
    all_fill_pattern_in_model = pattern_ids_by_name(doc=doc)
    # check fill pattern in model against fill pattern data
    return_value.update(
        _check_pattern_in_model(
            pattern_from_model=all_fill_pattern_in_model, pattern_data=fill_pattern_data
        )
    )
    return return_value


def check_all_line_and_fill_pattern_in_model(doc, view_overrides_data):
    """
    Check whether all line patterns and fill patterns used in the view_overrides_data exist in the model.

    Args:
        doc (Revit Document): The Revit document object.
        view_overrides_data (dict): A dictionary containing view overrides data.

    Returns:
        Result: A Result object containing the results of the line pattern and fill pattern checks.
    """
    return_value = res.Result()
    for key, view_override in view_overrides_data.items():
        return_value.append_message(
            "Checking fill patterns from template: {} from file against patterns from model.".format(
                view_override.view_name
            )
        )
        # check whether all line patterns and fill pattern exist in model
        return_value.update(
            check_line_patterns_are_in_model(
                doc=doc,
                line_pattern_data=view_override.get_all_used_line_patterns(),
            )
        )
        return_value.append_message(
            "Checking line patterns from template: {} from file against fill patterns from model.".format(
                view_override.view_name
            )
        )
        return_value.update(
            check_fill_patterns_are_in_model(
                doc=doc,
                fill_pattern_data=view_override.get_all_used_fill_patterns(),
            )
        )
    return return_value


def get_matching_templates(doc, view_overrides_data):
    """
    Returns a dictionary containing the view templates that match the view names specified in the view_overrides_data dictionary.

    Args:
        doc (Autodesk.Revit.DB.Document): The current Revit model document.
        view_overrides_data (dict): A dictionary containing view override data. The keys are view names and the values are objects of type ViewOverrideData.

    Returns:
        dict: A dictionary containing the view templates that match the view names specified in the view_overrides_data dictionary. The keys are view names and the values are tuples containing the view template and the corresponding view override data.
    """
    matching_templates = {}
    view_templates_in_model = get_view_templates(doc)
    for key, view_override in view_overrides_data.items():
        for template in view_templates_in_model:
            if Element.Name.GetValue(template) == view_override.view_name:
                matching_templates[view_override.view_name] = (template, view_override)
                break

    return matching_templates


def _add_filters_to_view(doc, view, filter_data):
    """
    Adds filters to a view in Autodesk Revit.

    Args:
        doc (Autodesk.Revit.DB.Document): The document object representing the Revit model.
        view (Autodesk.Revit.DB.View): The view object to which the filters should be added.
        filter_data (list): A list of filter objects that should be added to the view.

    Returns:
        duHast.Utilities.Objects.result.Result: The result object containing the outcome of adding the filters to the view.
        The `status` attribute of the result object indicates whether the filters were added successfully or not.
        The `message` attribute of the result object contains any additional messages related to the application of the filters.
        The `result` attribute of the result object is a list of filters that were successfully added to the view.
    """
    return_value = res.Result()
    filters_exist_in_view = []
    for filter in filter_data:
        status_filter = apply_filter_to_view(doc=doc, view=view, filter=filter.filter)
        return_value.update(status_filter)
        if status_filter.status:
            filters_exist_in_view.append(filter)
    return_value.result.append(filters_exist_in_view)
    return return_value


def apply_override_to_view(doc, view, view_override):
    """
    Apply graphic and filter overrides to a Revit view.

    Args:
        doc (Revit Document): The current Revit document.
        view (Revit View): The view to apply the overrides to.
        view_override (ViewOverride): An object containing the desired graphic and filter overrides.

    Returns:
        Result: A result object containing the status of the override application, any error messages, and additional information.
    """
    return_value = res.Result()
    return_value.append_message("Modifying view: {}".format(view.Name))
    target_view_data = get_view_settings(doc=doc, view=view)
    # find overrides requiring updates
    category_overrides_to_update = view_override.get_differing_category_overrides(
        other_view_graphic_settings=target_view_data
    )
    # if import has different filters to target update existing filter overrides only
    filter_overrides_to_update = view_override.get_differing_filter_overrides(
        other_view_graphic_settings=target_view_data
    )
    # update target template
    # category overrides
    if len(category_overrides_to_update) > 0:
        return_value.append_message(
            "Found category overrides to update: {}".format(
                len(category_overrides_to_update)
            )
        )
        # convert to override storage objects for ease of applying to view
        category_overrides_to_apply = convert_to_category_override_storage_objects(
            doc=doc, category_data_objects=category_overrides_to_update
        )
        # apply overrides to view
        result_apply_cat_overrides = apply_graphic_override_to_view(
            doc=doc,
            view=view,
            category_storage_instances=category_overrides_to_apply,
        )
        return_value.update(result_apply_cat_overrides)
    else:
        return_value.append_message("No category overrides needed updating")

    # filter overrides
    if len(filter_overrides_to_update) > 0:
        return_value.append_message(
            "Found filter overrides to update: {}".format(
                len(filter_overrides_to_update)
            )
        )

        # convert filter override to filter override storage object
        filter_overrides_to_apply = convert_to_filter_override_storage_objects(
            doc=doc, filter_data_objects=filter_overrides_to_update
        )
        # check if filter is applied to template if not add them in
        # this is not required since the filters to apply check only returns filters which are
        # applied to the source (from disk) and destination (in model) views
        filter_overrides_to_apply_status = _add_filters_to_view(
            doc=doc,
            view=view,
            filter_data=filter_overrides_to_apply,
        )
        return_value.update_sep(
            filter_overrides_to_apply_status.status,
            filter_overrides_to_apply_status.message,
        )
        if filter_overrides_to_apply_status.status:
            # apply filter override
            result_apply_filter_overrides = apply_filter_override_to_view(
                doc=doc,
                view=view,
                filter_storage_instances=filter_overrides_to_apply_status.result[0],
            )
            return_value.update(result_apply_filter_overrides)
    else:
        return_value.append_message("No filter overrides needed updating")
    return return_value


def apply_overrides_to_views(doc, view_data):
    """
    Applies graphic and filter overrides to multiple views in a Revit document.

    Args:
        doc (Revit Document): The current Revit document.
        view_data (dict): A dictionary where the keys are the names of the views and the values are lists containing the Revit view object and the view override object.

    Returns:
        Result: A result object containing the status of the override application, any error messages, and additional information.
    """

    return_value = res.Result()
    for key, value in view_data.items():
        status_apply = apply_override_to_view(doc, value[0], value[1])
        return_value.update(status_apply)
    return return_value


def apply_overrides_from_file(doc, file_path):
    """
    Applies graphic and filter overrides to multiple views in a Revit document based on data imported from a JSON file.

    :param doc: The current Revit document.
    :type doc: Revit Document
    :param file_path: The fully qualified file path of the JSON file containing the view override data.
    :type file_path: str

    :returns: A result object containing the status of the override application, any error messages, and additional information.
    :rtype: Result

    :example:

    Example Usage:
    >>> result = apply_overrides_from_file(doc, file_path)
    >>> if result.status:
    ...     print("Overrides applied successfully.")
    >>> else:
    ...     print("Failed to apply overrides:", result.message)
    """

    return_value = res.Result()
    try:
        # load data from file
        view_overrides_data_status = import_graphic_overrides(
            file_path=file_path, call_back=None
        )
        return_value.update(view_overrides_data_status)
        # check if any data was retrieved
        if view_overrides_data_status.status:
            view_overrides_data = view_overrides_data_status.result[0]
            # check whether all line patterns and fill pattern exist in model
            pattern_status = check_all_line_and_fill_pattern_in_model(
                doc=doc, view_overrides_data=view_overrides_data
            )
            return_value.update(pattern_status)
            if pattern_status.status:
                # find matching templates
                matching_templates = get_matching_templates(
                    doc=doc, view_overrides_data=view_overrides_data
                )
                if len(matching_templates) > 0:
                    apply_overrides = apply_overrides_to_views(
                        doc=doc, view_data=matching_templates
                    )
                    return_value.update(apply_overrides)
                else:
                    return_value.append_message(
                        "No matching view templates found in file."
                    )
            else:
                # Flatten the list of lists into a single list
                flattened_list = [
                    item for sublist in pattern_status.result for item in sublist
                ]
                # build list of missing patterns and raise error
                raise ValueError(
                    "Aborted: The following patterns are missing from the file: {}".format(
                        ",".join(flattened_list)
                    )
                )
        else:
            raise ValueError(view_overrides_data_status.message)

    except Exception as e:
        return_value.update_sep(
            False, "Failed to apply overrides with exception: {}".format(e)
        )
    return return_value
