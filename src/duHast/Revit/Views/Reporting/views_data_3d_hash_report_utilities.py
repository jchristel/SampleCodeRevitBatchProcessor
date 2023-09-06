"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains utility functions - hash tables from view settings.
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


# defines fixed hash values for ease of identification!
# no override is present
NO_OVERRIDE = 0
# category is switched of or filtered elements are switched off
SWITCHED_OFF = 1
# filter is not enabled
FILTER_NOT_ENABLED = 2
# filter or category does not exist in view or model
DOES_NOT_EXIST = -1


def _get_hash_headers(views_settings):
    """
    Headers are the Revit view template names

    :param views_settings: An instance of view graphic settings class storing Revit view template data.
    :type views_settings: :class:`.ViewGraphicsSettings`
    :return: List of headers representing all view template names in a model.
    :rtype: [str]
    """
    headers = []
    for setting in views_settings:
        headers.append(setting.view_name)
    return headers


def _get_hash_rows_categories(views_settings):
    """
    Rows are the Revit category names

    :param views_settings: An instance of view graphic settings class storing Revit view template data.
    :type views_settings: :class:`.ViewGraphicsSettings`
    :return: List of row headers representing all object categories in a model.
    :rtype: [str]
    """

    rows = []
    for override in views_settings[0].override_by_category:
        rows.append(override.main_category_name + " :: " + override.sub_category_name)
    return rows


def _get_hash_rows_filters(views_settings):
    """
    Rows are all unique filter names

    :param views_settings: An instance of view graphic settings class storing Revit view template data.
    :type views_settings: :class:`.ViewGraphicsSettings`
    """

    rows = []
    for setting in views_settings:
        for override in setting.override_by_filter:
            if override.filter_name not in rows:
                rows.append(override.filter_name)
    return rows


def _get_hash_for_category_overrides(headers, row_headers, views_settings):
    """
    Returns a list with a hash values for each Revit category override in a given view template.

    :param headers: List of headers representing all view template names in a model.
    :type headers: [str]
    :param row_headers: List of row headers representing all object categories in a model.
    :type row_headers: [str]
    :param views_settings: An instance of view graphic settings class storing Revit view template data.
    :type views_settings: :class:`.ViewGraphicsSettings`
    :raises ValueError: _description_
    :return: List of hash values.
    :rtype: [int]
    """

    # loop over header and get the respective view override setting
    # loop over rows and get the hash of the row value
    # return the hash table
    table_hash = {}
    for header_view_name in headers:
        # find the view (template)
        matching_template = next(
            (
                instance
                for instance in views_settings
                if instance.view_name == header_view_name
            ),
            None,
        )
        if matching_template == None:
            raise ValueError(
                "Impossible!!! No match found for view: [{}]".format(header_view_name)
            )

        # get category hashes
        for row in row_headers:
            # split to get main and sub category name
            name_parts = row.split(" :: ", 1)
            # Find a matching instance based on the two properties using a lambda expression and filter function
            matching_category = next(
                (
                    instance
                    for instance in matching_template.override_by_category
                    if instance.main_category_name == name_parts[0]
                    and instance.sub_category_name == name_parts[1]
                ),
                None,
            )

            # set a default value
            hash_value = DOES_NOT_EXIST
            # get the actual hash value if a match was found
            if matching_category:
                # check if an override is present and whether that the category is visible )
                # If that is the case return a hash of all properties

                if matching_category.is_visible == False:
                    # category is not visible
                    hash_value = SWITCHED_OFF
                elif (
                    matching_category.are_overrides_present == False
                    and matching_category.is_visible == True
                ):
                    # category is visible but no override is applied
                    hash_value = NO_OVERRIDE
                else:
                    # category is visible and an override is applied
                    hash_value = hash(matching_category)

            # add to table
            if row in table_hash:
                table_hash[row].append(hash_value)
            else:
                table_hash[row] = [hash_value]

    # convert into a simplified table where:
    # column headers are view names
    # row headers are category names
    simple_table = []
    for key, value in table_hash.items():
        simple_table.append(value)

    return simple_table


def _get_hash_for_filter_overrides(headers, row_headers, views_settings):
    """
    Returns a list with a hash values for each view filter override in a given view template.

    :param headers: List of headers representing all view template names in a model.
    :type headers: [str]
    :param row_headers: List of row headers representing each filter applied in a Revit view template.
    :type row_headers: [str]]
    :param views_settings: An instance of view graphic settings class storing Revit view template data.
    :type views_settings: :class:`.ViewGraphicsSettings`
    :raises ValueError: _description_
    :return: List of hash values.
    :rtype: [int]
    """

    # loop over header and get the respective view override setting
    # loop over rows and get the hash of the row value
    # return the hash table
    table_hash = {}
    for header_view_name in headers:
        # find the view (template)
        matching_template = next(
            (
                instance
                for instance in views_settings
                if instance.view_name == header_view_name
            ),
            None,
        )
        if matching_template == None:
            raise ValueError(
                "Impossible!!! No match found for view [{}]".format(header_view_name)
            )

        # get category hashes
        for row in row_headers:
            # Find a matching instance based on the two properties using a lambda expression and filter function
            matching_filter = next(
                (
                    instance
                    for instance in matching_template.override_by_filter
                    if instance.filter_name == row
                ),
                None,
            )

            # set a default value
            hash_value = DOES_NOT_EXIST
            # get the actual hash value if a match was found
            if matching_filter:
                # check if an override is present and whether that the elements filtered are visible )
                # If that is the case return a hash of all properties

                if matching_filter.is_visible == False:
                    # elements filtered are not visible
                    hash_value = SWITCHED_OFF
                elif (
                    matching_filter.are_overrides_present == False
                    and matching_filter.is_visible == True
                ):
                    # elements filtered are visible but no override is present
                    hash_value = NO_OVERRIDE
                elif (
                    matching_filter.are_overrides_present == False
                    and matching_filter.is_visible == True
                    and matching_filter.is_enabled == False
                ):
                    hash_value = FILTER_NOT_ENABLED
                else:
                    # elements filtered are visible and an override is present and the filter is enabled
                    hash_value = hash(matching_filter)

            # add to table
            if row in table_hash:
                table_hash[row].append(hash_value)
            else:
                table_hash[row] = [hash_value]

    # convert into a simplified table where:
    # column headers are view names
    # row headers are category names
    simple_table = []
    for key, value in table_hash.items():
        simple_table.append(value)

    return simple_table
