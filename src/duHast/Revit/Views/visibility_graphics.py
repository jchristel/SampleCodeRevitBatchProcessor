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

from duHast.Revit.Views.Reporting.views_data_report import PROP_VIEW_DATA
from duHast.Revit.Views.Objects.view_graphics_settings import ViewGraphicsSettings
from duHast.Revit.Views.templates import get_view_templates

from duHast.Revit.LinePattern.line_patterns import build_patterns_dictionary_by_name
from duHast.Revit.LinePattern.fill_patterns import pattern_ids_by_name

from Autodesk.Revit.DB import Element

def import_graphic_overrides(file_path, call_back):
    return_value = res.Result()
    view_overrides_data = {}
    json_data = read_json_data_from_file(file_path)
    counter = 1
    if PROP_VIEW_DATA in json_data:
        for json_override in json_data[PROP_VIEW_DATA]:
            view_override = ViewGraphicsSettings(j=json_override)
            view_overrides_data[view_override.view_name] = view_override
            return_value.append_message
            (
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
    return_value.result = view_overrides_data
    return view_overrides_data


def _check_pattern_in_model(pattern_from_model, pattern_data):
    """
    _summary_

    :param pattern_from_model: dictionary where key is the pattern name.
    :type pattern_from_model: _type_
    :param pattern_data: _description_
    :type pattern_data: _type_
    :return: _description_
    :rtype: _type_
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
    Check if all used patterns are in the model
    """
    return_value = res.Result()
    all_line_pattern_in_model = build_patterns_dictionary_by_name(doc=doc)
    # check line pattern in model against line pattern in data
    return_value.update(
        _check_pattern_in_model(
            pattern_from_model=all_line_pattern_in_model, pattern_data=line_pattern_data
        )
    )
    return return_value


def check_fill_patterns_are_in_model(doc, fill_pattern_data):
    """
    Check if all used patterns are in the model
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
    return_value = res.Result()
    for key, view_override in view_overrides_data.items():
        # check whether all line patterns and fill pattern exist in model
        return_value.update(
            check_line_patterns_are_in_model(
                doc=doc,
                line_pattern_data=view_override.get_all_used_line_patterns(),
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
    matching_templates = []
    view_templates_in_model = get_view_templates(doc)
    for key, view_override in view_overrides_data.items():
        for template in view_templates_in_model:
            if(Element.Name.GetValue(template) == view_override.view_name):
                matching_templates.append(template)
                break

    return matching_templates


def apply_overrides_from_file(doc, file_path):
    return_value = res.Result()
    try:
        # load data from file
        view_overrides_data_status = import_graphic_overrides(file_path=file_path)
        # check if any data was retrieved
        if view_overrides_data_status.status:
            view_overrides_data = view_overrides_data_status.result
            # check whether all line patterns and fill pattern exist in model
            pattern_status = check_all_line_and_fill_pattern_in_model(
                doc=doc, view_overrides_data=view_overrides_data
            )
            return_value.update(pattern_status)
            if(pattern_status.status):
                # find matching templates
                matching_templates = get_matching_templates(doc=doc, view_overrides_data=view_overrides_data)
                if(len(matching_templates)>0):
                    pass
                    # apply overrides
                else:
                    return_value.append_message("No matching view templates found in file.")
            else:
                pass
                # build list of missing patterns and raise error
        else:
            raise ValueError(view_overrides_data_status.message)

    except Exception as e:
        return_value.update_sep(
            False, "Failed to apply overrides with exception: {}".format(e)
        )
    return return_value
