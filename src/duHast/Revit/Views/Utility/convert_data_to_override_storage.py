"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Data category and filter override instances to storage object helper functions.
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

from duHast.Revit.Views.Objects.category_override_storage import RevitCategoryOverride
from duHast.Revit.Views.Objects.filter_override_storage import RevitFilterOverride
from duHast.Revit.Categories.categories_model import get_category_by_names
from duHast.Revit.Views.filters import get_filter_by_name
from duHast.Revit.Views.Utility.convert_data_to_revit_override import (
    convert_to_revit_graphic_override,
)


def convert_to_category_override_storage(doc, category_data_instance):
    """
    Retrieves the corresponding category object from the Revit document based on the category names provided in the category data instance.

    Args:
        doc (Revit Document): The Revit document object.
        category_data_instance (CategoryData): An instance of the CategoryData class representing the category and subcategory names, and visibility information.

    Returns:
        RevitCategoryOverride or None: The created RevitCategoryOverride object if a match is found, otherwise None.
    """
    return_value = None
    # get the category
    category_in_model = get_category_by_names(
        doc=doc,
        main_category_name=category_data_instance.main_category_name,
        sub_category_name=category_data_instance.sub_category_name,
    )
    # get the revit override
    revit_override = convert_to_revit_graphic_override(
        doc=doc, data_override=category_data_instance, is_filter_override=False
    )

    if category_in_model:
        return_value = RevitCategoryOverride(
            main_category_name=category_data_instance.main_category_name,
            sub_category_name=category_data_instance.sub_category_name,
            category=category_in_model,
            category_id=category_in_model.Id,
            revit_override=revit_override,
            is_category_hidden=not category_data_instance.is_visible,  # need to be inverted :(((
        )
    return return_value


def convert_to_category_override_storage_objects(doc, category_data_objects):
    """
    Converts a list of category data objects into category override storage objects.

    Args:
        doc (Revit Document): The Revit document object.
        category_data_objects (list): A list of category data objects.

    Returns:
        list: A list of category override storage objects representing the converted category data objects.
    """
    return_value = []
    for cat_instance in category_data_objects:
        converted = convert_to_category_override_storage(
            doc=doc, category_data_instance=cat_instance
        )
        if converted:
            return_value.append(converted)
    return return_value


def convert_to_filter_override_storage(doc, filter_data_instance):
    """
    Converts a filter data instance into a `RevitFilterOverride` object.

    Args:
        doc (Revit Document): The current Revit model document.
        filter_data_instance (FilterDataInstance): The filter data instance to be converted.

    Returns:
        RevitFilterOverride: The converted filter override object, or None if the filter does not exist in the model.
    """
    return_value = None
    # get the filter
    filter_in_model = get_filter_by_name(
        doc=doc, filter_name=filter_data_instance.filter_name
    )

    # get the revit override
    revit_override = convert_to_revit_graphic_override(
        doc=doc, data_override=filter_data_instance, is_filter_override=True
    )

    if filter_in_model:
        return_value = RevitFilterOverride(
            filter_name=filter_data_instance.filter_name,
            filter_id=filter_in_model.Id,
            filter=filter_in_model,
            revit_override=revit_override,
            is_filter_visible=filter_data_instance.is_visible,
            is_filter_enabled=filter_data_instance.is_enabled,
        )

    return return_value


def convert_to_filter_override_storage_objects(doc, filter_data_objects):
    """
    Converts a list of filter data objects into a list of RevitFilterOverride objects.

    Args:
        doc (Revit Document): The current Revit model document.
        filter_data_objects (list): A list of filter data objects to be converted.

    Returns:
        list: A list of RevitFilterOverride objects that represent the converted filter data objects.
    """
    return_value = []
    for filter_instance in filter_data_objects:
        converted = convert_to_filter_override_storage(
            doc=doc, filter_data_instance=filter_instance
        )
        if converted:
            return_value.append(converted)
    return return_value
