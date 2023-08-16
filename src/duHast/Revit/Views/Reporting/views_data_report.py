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

from duHast.Revit.Views.Utility.data_view import get_view_settings
from duHast.Revit.Views.Objects.view_graphics_settings import ViewGraphicsSettings
from duHast.Utilities.files_json import write_json_to_file, read_json_data_from_file


PROP_FILE_NAME = "file_name"
PROP_VIEW_DATA = "view_data"


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


def _get_hashes_overrides_categories(headers, rows, views_settings):
    
    # loop over header and get the respective view override setting
    # loop over rows and get the hash of the row value
    # return the hash table
    
    pass


def _get_hashes_overrides_filters(headers, rows, views_settings):
    pass


def _combine_hash_tables(table_category, table_filter):
    pass


def get_views_graphics_settings_hash_data(doc, views):
    """
    _summary_

    :param doc: _description_
    :type doc: _type_
    :param views: _description_
    :type views: _type_
    :return: _description_
    :rtype: _type_
    """

    # get settings objects
    views_settings = [] = get_views_graphic_settings_data(doc, views)

    # convert category overrides into hash table where:
    # rows are categories / sub categories
    # headers are template names
    headers = _get_hash_headers(views_settings)
    rows = _get_hash_rows_categories(views_settings)
    hash_table_categories = _get_hashes_overrides_categories(
        headers, rows, views_settings
    )

    # convert filter overrides into hash table
    # # rows are filters
    # headers are template names
    rows = _get_hash_rows_filters(views_settings)
    hash_table_filters = _get_hashes_overrides_filters(headers, rows, views_settings)

    # combine hash table of categories and filters into one
    combined_table = _combine_hash_tables(
        table_category=hash_table_categories, table_filter=hash_table_filters
    )
    return combined_table


def get_views_graphic_settings_data(doc, views):
    """
    Gets view data graphic settings from the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param views: Views of which to report graphical overrides on. (View must support graphical overrides, otherwise an exception will be thrown!)
    :type views: [Autodesk.Revit.DB.View]
    :return: list of ViewGraphicsSettings instances
    :rtype: [:class:`.ViewGraphicsSettings`]
    """

    views_settings = []

    # loop over past in views and retrieve settings
    for view in views:
        view_setting = get_view_settings(
            doc=doc,
            view=view,
        )
        views_settings.append(view_setting)

    return views_settings


def write_graphics_settings_report(revit_file_name, file_path, data):
    """
    Write view graphic settings to file.

    :param revit_file_name: The revit file name (without path or file extension)
    :type revit_file_name: str
    :param file_path: Fully qualified file path
    :type file_path: str
    :param data: json dictionary to be written to file
    :type data: {str:Any}

    :return:
        Result class instance.

        - result.status False if file failed to write, otherwise True.
        - result.message will contain file name of file written.
        - result.result: empty list

        On exception:

        - result.status (bool) will be False.
        - result.message will contain the exception message.
        - result.result: will be an empty list

    :rtype: :class:`.Result`
    """

    # wrap data to include file name
    json_data = {PROP_FILE_NAME: revit_file_name, PROP_VIEW_DATA: data}

    result = write_json_to_file(json_data=json_data, data_output_file_path=file_path)
    return result


def read_view_data_from_file(file_path):
    """
    Reads a view data report file into a list of view graphic setting instances

    :param file_path: Fully qualified file path of report file.
    :type file_path: str
    :raises ValueError: If data node is missing from file

    :return: list of settings if files was read successfully otherwise an exception will be raised.
    :rtype: :class:`.ViewGraphicsSettings`
    """

    data_views = []
    # read json file
    data_read = read_json_data_from_file(file_path=file_path)
    # check it got the required property node
    if (PROP_VIEW_DATA) in data_read:
        # convert node entries into class instances
        for entry in data_read[PROP_VIEW_DATA]:
            data_view = ViewGraphicsSettings(entry)
            data_views.append(data_view)
    else:
        # missing node...raise an exception
        raise ValueError("Data does not contain a {} node".format(PROP_VIEW_DATA))

    return data_views
