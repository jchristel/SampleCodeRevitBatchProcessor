"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains the Revit view report functionality.
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

import os

from duHast.Revit.Views.Reporting.views_data_report import (
    get_views_graphic_settings_data,
)
from duHast.Utilities.files_csv import write_report_data_as_csv
from duHast.Utilities.Objects import result as res

from duHast.Revit.Views.Reporting.view_reports_json_props import PROP_FILE_NAME, PROP_VIEW_DATA
from duHast.Utilities.files_json import write_json_to_file

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
    Headers are the template names

    :param views_settings: _description_
    :type views_settings: _type_
    """
    headers = []
    for setting in views_settings:
        headers.append(setting.view_name)
    return headers


def _get_hash_rows_categories(views_settings):
    """
    Rows are the category names

    :param views_settings: _description_
    :type views_settings: _type_
    """
    rows = []
    for override in views_settings[0].override_by_category:
        rows.append(override.main_category_name + " :: " + override.sub_category_name)
    return rows


def _get_hash_rows_filters(views_settings):
    """
    Rows are all unique filter names

    :param views_settings: _description_
    :type views_settings: _type_
    """

    rows = []
    for setting in views_settings:
        for override in setting.override_by_filter:
            if override.filter_name not in rows:
                rows.append(override.filter_name)
    return rows


def _convert_hash_dic_to_table(hash_dic, headers, row_headers):
    # convert into a simplified table where:
    # column headers are view names
    # row headers are category names

    simple_table = []
    headers.insert(0, "-")
    simple_table.append(headers)

    for row_header in row_headers:
        try:
            row = hash_dic[row_header]
            row.insert(0, row_header)
            simple_table.append(row)
        except Exception as e:
            print("exception: {}".format(e))

    return simple_table


def _get_hashes_overrides_categories(headers, row_headers, views_settings):
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
                
                if(matching_category.is_visible == False):
                    # category is not visible
                    hash_value = SWITCHED_OFF
                elif(matching_category.are_overrides_present == False and matching_category.is_visible == True):
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
    simple_table = _convert_hash_dic_to_table(
        hash_dic=table_hash, headers=headers, row_headers=row_headers
    )

    return simple_table


def _get_hashes_overrides_filters(headers, row_headers, views_settings):
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
                elif(matching_filter.are_overrides_present == False and matching_filter.is_visible == True):
                    # elements filtered are visible but no override is present
                    hash_value = NO_OVERRIDE
                elif(matching_filter.are_overrides_present == False and matching_filter.is_visible == True and matching_filter.is_enabled == False):
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
    simple_table = _convert_hash_dic_to_table(
        hash_dic=table_hash, headers=headers, row_headers=row_headers
    )

    return simple_table


def get_views_graphics_settings_hash_data(doc, views, views_settings=None):
    """
    _summary_

    :param doc: _description_
    :type doc: _type_
    :param views: _description_
    :type views: _type_
    :param views_settings: _description_, defaults to None
    :type views_settings: _type_, optional
    :return: _description_
    :rtype: _type_
    """

    # check if any view settings where past in, if not get them
    if views_settings == None:
        # get settings objects
        views_settings = get_views_graphic_settings_data(doc, views)

    # convert category overrides into hash table where:
    # rows are categories / sub categories
    # headers are template names
    headers = _get_hash_headers(views_settings)
    # copy headers list since the original headers list gets manipulated in get hashes overrides!
    headers_filters = list(headers)

    row_categories = _get_hash_rows_categories(views_settings)
    hash_table_categories = _get_hashes_overrides_categories(
        headers, row_categories, views_settings
    )

    # convert filter overrides into hash table
    # # rows are filters
    # headers are template names
    row_filters = _get_hash_rows_filters(views_settings)
    hash_table_filters = _get_hashes_overrides_filters(
        headers_filters, row_filters, views_settings
    )

    return hash_table_categories, hash_table_filters


def write_graphics_settings_hash_csv_report(
    revit_file_name, directory_path, data_category, data_filter
):
    """
    _summary_

    :param revit_file_name: _description_
    :type revit_file_name: _type_
    :param directory_path: _description_
    :type directory_path: _type_
    :param data_category: _description_
    :type data_category: _type_
    :param data_filter: _description_
    :type data_filter: _type_
    :return: _description_
    :rtype: _type_
    """

    result = res.Result()
    file_path_category = os.path.join(
        directory_path, revit_file_name + "_category_hash.csv"
    )
    file_path_filter = os.path.join(
        directory_path, revit_file_name + "_filter_hash.csv"
    )
    # write out files
    try:
        write_report_data_as_csv(
            file_name=file_path_category, header=[], data=data_category
        )
        result.update_sep(
            True, "Hash category data written to file: {}".format(file_path_category)
        )
        write_report_data_as_csv(
            file_name=file_path_filter, header=[], data=data_filter
        )
        result.update_sep(
            True, "Hash filter data written to file: {}".format(file_path_filter)
        )
    except Exception as e:
        result.update_sep(
            False, "Failed to write data to file with exception: {}".format(e)
        )
    return result

def write_graphics_settings_hash_json_report(
    revit_file_name, directory_path, data_category, data_filter
):
    '''
    _summary_

    :param revit_file_name: _description_
    :type revit_file_name: _type_
    :param directory_path: _description_
    :type directory_path: _type_
    :param data_category: _description_
    :type data_category: _type_
    :param data_filter: _description_
    :type data_filter: _type_
    :return: _description_
    :rtype: _type_
    '''

    result = res.Result()
    file_path_category = os.path.join(
        directory_path, revit_file_name + "_category_hash.json"
    )
    file_path_filter = os.path.join(
        directory_path, revit_file_name + "_filter_hash.json"
    )

    json_data_category = {PROP_FILE_NAME: revit_file_name, PROP_VIEW_DATA: data_category}
    json_data_filter = {PROP_FILE_NAME: revit_file_name, PROP_VIEW_DATA: data_filter}

    # write out files
    try:
        result_category = write_json_to_file(json_data=json_data_category, data_output_file_path=file_path_category)
        result.update_sep(
            result_category.status, "Hash category data written to json file: {}".format(file_path_category)
        )
        result_filter = write_json_to_file(json_data=json_data_filter, data_output_file_path=file_path_filter)
        result.update_sep(
            result_filter.status, "Hash filter data written to json file: {}".format(file_path_filter)
        )
    except Exception as e:
        result.update_sep(
            False, "Failed to write data to file with exception: {}".format(e)
        )
    return result