"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains the Revit view template data to 3D hash report functionality.
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
from duHast.Revit.Views.Reporting.views_data_report import read_view_data_from_file
from duHast.Utilities.files_get import (
    get_file_name_without_ext,
)
from duHast.Revit.Views.Reporting.views_data_3d_hash_report_utilities import (
    _get_hash_headers,
    _get_hash_rows_categories,
    _get_hash_rows_filters,
    _get_hash_for_category_overrides,
    _get_hash_for_filter_overrides,
)
from duHast.Revit.Views.Reporting.view_reports_json_props import PROP_FILE_NAME

from duHast.Revit.Views.Reporting.Objects.json_conversion_storage import (
    JSONThreeDStorage,
)


def _load_json_data(files, progress_call_back=None):
    """
    Reads view template data from files into a dictionary.

    :param files: List of fully qualified file path to json files containing view template data.
    :type files: [str]
    :param progress_call_back: A call back function accepting as arguments the number of the current file processed and the number of overall files to be processed, defaults to None
    :type progress_call_back: func(counter, overall_counter), optional
    :return: A dictionary where key is the file name without extension and value is a list of view settings
    :rtype: {str: [:class:`.ViewGraphicsSettings`]}
    """

    json_data = {}
    counter = 0
    for file_path in files:
        file_name = get_file_name_without_ext(file_path=file_path)
        json_single_data = read_view_data_from_file(file_path=file_path)
        json_data[file_name] = json_single_data
        counter = counter + 1
        if progress_call_back is not None:
            progress_call_back(counter, len(files))
    return json_data


def _get_category_hash_table_data_by_file(view_settings, progress_call_back=None):
    """
    Returns a dictionary of partly populated JSONThreeDStorage objects.

    - column headers ( template names)
    - row headers ( category names)
    - hash table ( category overwrites )

    :param view_settings: A dictionary where key is the file name without extension and value is a list of view settings
    :type view_settings: {str: [:class:`.ViewGraphicsSettings`]}
    :param progress_call_back: A call back function accepting as arguments the number of the current file processed and the number of overall files to be processed, defaults to None
    :type progress_call_back: func(counter, overall_counter), optional
    :return: A dictionary where key is the file name without extension and value is an instance of a custom storage object
    :rtype: {str: [:class:`.JSONThreeDStorage`]}
    """

    dic_tables_by_file = {}
    counter = 0
    for key, vt_setting in view_settings.items():
        column_headers = _get_hash_headers(vt_setting)
        row_headers = _get_hash_rows_categories(vt_setting)
        row_headers_filters = _get_hash_rows_filters(vt_setting)
        hash_table_category_overrides = _get_hash_for_category_overrides(
            headers=column_headers, row_headers=row_headers, views_settings=vt_setting
        )
        hash_table_filter_overrides = _get_hash_for_filter_overrides(
            headers=column_headers,
            row_headers=row_headers_filters,
            views_settings=vt_setting,
        )
        storage = JSONThreeDStorage()
        storage.column_headers = column_headers
        storage.row_headers = row_headers
        storage.row_headers_filters = row_headers_filters
        storage.hash_table = hash_table_category_overrides
        storage.hash_table_filters = hash_table_filter_overrides
        dic_tables_by_file[key] = storage
        counter = counter + 1
        if progress_call_back is not None:
            progress_call_back(counter, len(view_settings))

    return dic_tables_by_file


def _map_hash_values_to_range(hash_data_by_file, progress_call_back=None):
    """
    Hash values returned from view templates have a really large range. This function maps them to their index in a sorted list.
    Note -1,0,1 are left unchanged.
    Hash tables for category and filter overrides will be updated with mapped values.

    :param hash_data_by_file: A dictionary where key is the file name without extension and value is an instance of a custom storage object
    :type hash_data_by_file: {str: [:class:`.JSONThreeDStorage`]}
    :param progress_call_back: A call back function accepting as arguments the number of the current file processed and the number of overall files to be processed, defaults to None
    :type progress_call_back: func(counter, overall_counter), optional
    :return: Passed in dictionary with updated hash tables.
    :rtype: {str: [:class:`.JSONThreeDStorage`]}
    """

    hash_mapper_categories = []
    hash_mapper_filters = []
    try:
        # build a unique list of all hash values
        for key, hash_data in hash_data_by_file.items():
            for entry in hash_data.hash_table:
                hash_mapper_categories = sorted(
                    list(set(hash_mapper_categories) | set(entry))
                )
            for entry in hash_data.hash_table_filters:
                hash_mapper_filters = sorted(
                    list(set(hash_mapper_filters) | set(entry))
                )

        # note 0, 1, -1 are special values and can not need to be changed!!
        # remove them from the sorted list and then re-insert them at the beginning
        if -1 in hash_mapper_categories:
            index = hash_mapper_categories.index(-1)
            hash_mapper_categories.pop(index)
        if 0 in hash_mapper_categories:
            index = hash_mapper_categories.index(0)
            hash_mapper_categories.pop(index)
        if 1 in hash_mapper_categories:
            index = hash_mapper_categories.index(1)
            hash_mapper_categories.pop(index)

        hash_mapper_categories.insert(0, -1)
        hash_mapper_categories.insert(0, 0)
        hash_mapper_categories.insert(0, 1)

        if -1 in hash_mapper_filters:
            index = hash_mapper_filters.index(-1)
            hash_mapper_filters.pop(index)
        if 0 in hash_mapper_filters:
            index = hash_mapper_filters.index(0)
            hash_mapper_filters.pop(index)
        if 1 in hash_mapper_filters:
            index = hash_mapper_filters.index(1)
            hash_mapper_filters.pop(index)

        hash_mapper_filters.insert(0, -1)
        hash_mapper_filters.insert(0, 0)
        hash_mapper_filters.insert(0, 1)

        # loop over current hash values and replace with index of value in mapper list
        # preserve -1, 0, 1 values

        call_back_progress_counter = 0
        for key, hash_data in hash_data_by_file.items():
            # update categories hash table
            mapped_hash_table_categories = []
            try:
                for row in hash_data.hash_table:
                    new_row = []
                    for entry in row:
                        if entry > 1 or entry < -1:
                            mapped_index = hash_mapper_categories.index(entry)
                            new_row.append(mapped_index)
                        else:
                            new_row.append(entry)
                    mapped_hash_table_categories.append(new_row)
                # overwrite existing hash table
                hash_data.hash_table = mapped_hash_table_categories
            except Exception as e:
                raise ValueError("Failed to match category hash: {}".format(e))
            # update filters hash table
            mapped_hash_table_filters = []
            try:
                for row in hash_data.hash_table_filters:
                    new_row = []
                    for entry in row:
                        if entry > 1 or entry < -1:
                            mapped_index = hash_mapper_filters.index(entry)
                            new_row.append(mapped_index)
                        else:
                            new_row.append(entry)
                    mapped_hash_table_filters.append(new_row)
                # overwrite existing hash table
                hash_data.hash_table_filters = mapped_hash_table_filters
            except Exception as e:
                raise ValueError("Failed to match filter hash: {}".format(e))
            # update call back
            call_back_progress_counter = call_back_progress_counter + 1
            if progress_call_back is not None:
                progress_call_back(call_back_progress_counter, len(hash_data_by_file))
    except Exception as e:
        raise ValueError("Failed to map values to range: {}".format(e))
    return hash_data_by_file


def _merge_column_headers(hash_data_by_file):
    """
    Builds a unique list of column headers ( view template names )
    This list is the same for filter and category overrides.

    :param hash_data_by_file: A dictionary where key is the file name without extension and value is an instance of a custom storage object
    :type hash_data_by_file: {str: [:class:`.JSONThreeDStorage`]}
    :return: Passed in dictionary with updated merged column list.
    :rtype: {str: [:class:`.JSONThreeDStorage`]}
    """

    try:
        data = []
        # build list with unique entries
        for key, vt_setting in hash_data_by_file.items():
            data = sorted(list(set(data) | set(vt_setting.column_headers)))

        # this list is common for all files...update them
        for key, vt_setting in hash_data_by_file.items():
            vt_setting.merged_column_headers = data

        return hash_data_by_file

    except Exception as e:
        raise ValueError(
            "Failed to merge column headers (view template names): {}".format(e)
        )


def _merge_row_headers(hash_data_by_file):
    """
    Builds a unique list of row headers for  object categories names and filter names.

    :param hash_data_by_file: A dictionary where key is the file name without extension and value is an instance of a custom storage object
    :type hash_data_by_file: {str: [:class:`.JSONThreeDStorage`]}
    :return: Passed in dictionary with updated merged row list.
    :rtype: {str: [:class:`.JSONThreeDStorage`]}
    """

    try:
        data_category_names = []
        data_filter_names = []
        # build list with unique entries for category names
        for key, vt_setting in hash_data_by_file.items():
            data_category_names = sorted(
                list(set(data_category_names) | set(vt_setting.row_headers))
            )

        # build list with unique entries for filter names
        for key, vt_setting in hash_data_by_file.items():
            data_filter_names = sorted(
                list(set(data_filter_names) | set(vt_setting.row_headers_filters))
            )

        # these lists are common for all files...update them
        for key, vt_setting in hash_data_by_file.items():
            vt_setting.merged_row_headers = data_category_names
            vt_setting.merged_row_headers_filters = data_filter_names

        return hash_data_by_file

    except Exception as e:
        raise ValueError(
            "Failed to merge row headers (object category names): {}".format(e)
        )


# ---------------------------- padded default array -------------------------


def _get_padded_default_array(
    merged_row_headers,
    merged_column_headers,
):
    """
    Builds an 2d array where column number equals the number of unique view templates (merged column header)
    and row number equals number of unique object category names. All values are set to -1.

    :param merged_row_headers: A list containing row headers
    :type merged_row_headers: [str]
    :param merged_column_headers: A list containing column headers
    :type merged_column_headers: [str]
    :return: A 2D array where all values are -1.
    :rtype: [[],[],...]
    """

    # Create a new padded 2D array
    padded_array = [
        [-1 for entry in merged_column_headers] for entry in merged_row_headers
    ]
    return padded_array


def _assign_padded_default_array(hash_data_by_file, progress_call_back=None):
    """
    Assigns a padded 2D array to storage class property

    :param hash_data_by_file: A dictionary where key is the file name without extension and value is an instance of a custom storage object
    :type hash_data_by_file: {str: [:class:`.JSONThreeDStorage`]}
    :param progress_call_back: A call back function accepting as arguments the number of the current file processed and the number of overall files to be processed, defaults to None
    :type progress_call_back: func(counter, overall_counter), optional
    :return:
        Result class instance.
        - .status True if padded array was successfully assigned. Otherwise False.
        - .message will contain array size.
    :rtype: :class:`.Result`
    """

    result = res.Result()
    try:
        call_back_progress_counter = 0
        # build default hash tables where all values are -1 for categories and filters
        for key, hash_by_file in hash_data_by_file.items():
            padded_array_categories = _get_padded_default_array(
                merged_column_headers=hash_by_file.merged_column_headers,
                merged_row_headers=hash_by_file.merged_row_headers,
            )
            padded_array_filters = _get_padded_default_array(
                merged_column_headers=hash_by_file.merged_column_headers,
                merged_row_headers=hash_by_file.merged_row_headers_filters,
            )
            hash_data_by_file[key].padded_default_hash_table = padded_array_categories
            hash_data_by_file[
                key
            ].padded_default_hash_table_filters = padded_array_filters
            result.append_message(
                "{}: Created padded categories default value array of size {} by {}".format(
                    key, len(padded_array_categories), len(padded_array_categories[0])
                )
            )
            result.append_message(
                "{}: Created padded filters default value array of size {} by {}".format(
                    key, len(padded_array_filters), len(padded_array_filters[0])
                )
            )
            call_back_progress_counter = call_back_progress_counter + 1
            if progress_call_back is not None:
                progress_call_back(call_back_progress_counter, len(hash_data_by_file))
        result.result.append(hash_data_by_file)
    except Exception as e:
        result.update_sep(
            False, "Failed to assigned padded default array with: {}".format(e)
        )
    return result


# ---------------------------- row indices ---------------------------------


def _assign_row_indices_pointer(hash_data_by_file, progress_call_back=None):
    """
    Creates row and index pointers per file which map the file specific rows and column to the overall padded array rows and columns.

    :param hash_data_by_file: A dictionary where key is the file name without extension and value is an instance of a custom storage object
    :type hash_data_by_file: {str: [:class:`.JSONThreeDStorage`]}
    :param progress_call_back: A call back function accepting as arguments the number of the current file processed and the number of overall files to be processed, defaults to None
    :type progress_call_back: func(counter, overall_counter), optional
    :return:
        Result class instance.
        - .status True if row and column index pointers where successfully assigned. Otherwise False.
        - .message will contain array size.
    :rtype: :class:`.Result`
    """

    result = res.Result()
    try:
        call_back_progress_counter = 0
        # build row and column indices list for mapping of value hash table entries to default hash table
        for key, hash_by_file in hash_data_by_file.items():
            # Find the indices for row and column headers in the merged headers
            row_indices_categories_all = [
                hash_by_file.merged_row_headers.index(row)
                for row in hash_by_file.row_headers
            ]
            row_indices_filters_all = [
                hash_by_file.merged_row_headers_filters.index(row)
                for row in hash_by_file.row_headers_filters
            ]
            # column header indices are the same for filters and categories
            column_indices_all = [
                hash_by_file.merged_column_headers.index(col)
                for col in hash_by_file.column_headers
            ]

            hash_data_by_file[key].row_indices = row_indices_categories_all
            hash_data_by_file[key].row_indices_filters = row_indices_filters_all
            hash_data_by_file[key].column_indices = column_indices_all
            result.append_message(
                "{}: Created categories row: {} , filters row {} and column: {} indices mapper.".format(
                    key,
                    len(row_indices_categories_all),
                    len(row_indices_filters_all),
                    len(column_indices_all),
                )
            )
            call_back_progress_counter = call_back_progress_counter + 1
            if progress_call_back is not None:
                progress_call_back(call_back_progress_counter, len(hash_data_by_file))
        result.result.append(hash_data_by_file)
    except Exception as e:
        result.update_sep(
            False, "Failed to assigned row and column index pointers with: {}".format(e)
        )
    return result


def _update_default_array_values(row_indices, col_indices, default_array, value_array):
    """
    Updates the default padded arrays with hash values from file specific array using row and column index pointers.

    :param row_indices: Row index mapper from file specific array to default array.
    :type row_indices: [int]
    :param col_indices: _Column index mapper from file specific array to default array.
    :type col_indices: [int]
    :param default_array: The default 2D array
    :type default_array: [[int],[int],]
    :param value_array: The file specific 2D array
    :type value_array: [[int],[int],]
    :return: Default array updated with file specific array values.
    :rtype: [[int],[int],]
    """

    # Fill in the values from array_model_a
    for i, row_index in enumerate(row_indices):
        for j, col_index in enumerate(col_indices):
            default_array[row_index][col_index] = value_array[i][j]
    return default_array


def _assign_default_array_values(hash_data_by_file, progress_call_back=None):
    """
    Assigns file specific array values to default arrays for categories and filters by file.

    :param hash_data_by_file: A dictionary where key is the file name without extension and value is an instance of a custom storage object
    :type hash_data_by_file: {str: [:class:`.JSONThreeDStorage`]}
    :param progress_call_back: A call back function accepting as arguments the number of the current file processed and the number of overall files to be processed, defaults to None
    :type progress_call_back: func(counter, overall_counter), optional
    :return:
        Result class instance.
        - .status True if default arrays where successfully updated with values from file specific arrays. Otherwise False.
        - .message will contain array size.
    :rtype: :class:`.Result`
    """

    result = res.Result()
    try:
        call_back_progress_counter = 0
        # update the default hash table for each file with values from the value hash table from the same file
        for key, hash_by_file in hash_data_by_file.items():
            updated_array_categories = _update_default_array_values(
                row_indices=hash_by_file.row_indices,
                col_indices=hash_by_file.column_indices,
                default_array=hash_by_file.padded_default_hash_table,
                value_array=hash_by_file.hash_table,
            )

            updated_array_filters = _update_default_array_values(
                row_indices=hash_by_file.row_indices_filters,
                col_indices=hash_by_file.column_indices,
                default_array=hash_by_file.padded_default_hash_table_filters,
                value_array=hash_by_file.hash_table_filters,
            )

            hash_by_file.padded_value_hash_table = updated_array_categories
            hash_by_file.padded_value_hash_table_filters = updated_array_filters

            result.append_message(
                "{}: Updated padded category default value array with values of size {} by {}".format(
                    key,
                    len(updated_array_categories),
                    len(updated_array_categories[0]),
                )
            )

            result.append_message(
                "{}: Updated padded filter default value array with values of size {} by {}".format(
                    key,
                    len(updated_array_filters),
                    len(updated_array_filters[0]),
                )
            )

            call_back_progress_counter = call_back_progress_counter + 1
            if progress_call_back is not None:
                progress_call_back(call_back_progress_counter, len(hash_data_by_file))
        result.result.append(hash_data_by_file)
    except Exception as e:
        result.update_sep(
            False,
            "Failed to assigned file specific array values to default array: {}".format(
                e
            ),
        )
    return result


def _built_threeD_array(hash_data_by_file):
    """
    Combine 2D default hash arrays from all files into single 3D hash array.

    :param hash_data_by_file: A dictionary where key is the file name without extension and value is an instance of a custom storage object
    :type hash_data_by_file: {str: [:class:`.JSONThreeDStorage`]}
    :return:
        Result class instance.
        - .status True if 3D array was successfully created. Otherwise False.
        - .message will contain array size.
        -. result will contain the 3D array for categories as first value in list and the 3D array for filters as the second value in list
    :rtype: :class:`.Result`
    """

    result = res.Result()
    try:
        array_3d_categories = []

        z_value_categories = 0
        x_value_categories = 0
        y_value_categories = 0

        array_3d_filters = []
        z_value_filters = 0
        x_value_filters = 0
        y_value_filters = 0

        for key, hash_by_file in hash_data_by_file.items():
            # categories
            array_3d_categories.append(hash_by_file.padded_value_hash_table)
            x_value_categories = len(hash_by_file.padded_value_hash_table)
            y_value_categories = len(hash_by_file.padded_value_hash_table[0])
            z_value_categories = z_value_categories + 1
            # filters
            array_3d_filters.append(hash_by_file.padded_value_hash_table_filters)
            x_value_filters = len(hash_by_file.padded_value_hash_table_filters)
            y_value_filters = len(hash_by_file.padded_value_hash_table_filters[0])
            z_value_filters = z_value_filters + 1

        result.append_message(
            "Built 3D category array of size: number of files: {} , by number of categories: {} , by number of view templates: {}".format(
                z_value_categories, x_value_categories, y_value_categories
            )
        )
        result.append_message(
            "Built 3D filter array of size: number of files: {} , by number of filters: {} , by number of view templates: {}".format(
                z_value_filters, x_value_filters, y_value_filters
            )
        )

        result.result.append(array_3d_categories)
        result.result.append(array_3d_filters)
    except Exception as e:
        result.update_sep(False, "Failed to build 3D array: {}".format(e))
    return result


def _flatten_category_threeD_array(
    array_3d, sample_storage, model_names, hash_data_by_file, progress_call_back=None
):
    """
    Flattens the 3D array build from hash tables from each file into a json structure easily read by power bi.

    :param array_3d: A 3D array.
    :type array_3d: [[[]]]
    :param sample_storage: Storage instance used to map view template names and category names using merged lists.
    :type sample_storage: :class:`.JSONThreeDStorage`
    :param model_names: List of all model names of which view template data is included in 3D hash array.
    :type model_names: [str]
    :param hash_data_by_file: A dictionary where key is the file name without extension and value is an instance of a custom storage object
    :type hash_data_by_file: {str: [:class:`.JSONThreeDStorage`]}
    :param progress_call_back: A call back function accepting as arguments the number of the current file processed and the number of overall files to be processed, defaults to None
    :type progress_call_back: func(counter, overall_counter), optional
    :return:
        Result class instance.
        - .status True if 3D array was successfully created. Otherwise False.
        - .message will contain array size.
        -. result will contain the flatten array as first value in list
    :rtype: :class:`.Result`
    """

    result = res.Result()
    try:
        call_back_progress_counter = 0
        # flatten 3D hash data for power bi
        flattened_data = []
        for model_name, layer in enumerate(array_3d):
            for category, row in enumerate(layer):
                for view_template, hash_value in enumerate(row):
                    flattened_data.append(
                        {
                            "view_template": sample_storage.merged_column_headers[
                                view_template
                            ],
                            "category": sample_storage.merged_row_headers[category],
                            "model_name": model_names[model_name],
                            "hash_value": hash_value,
                        }
                    )
            call_back_progress_counter = call_back_progress_counter + 1
            if progress_call_back is not None:
                progress_call_back(call_back_progress_counter, len(hash_data_by_file))
        result.result.append(flattened_data)
    except Exception as e:
        result.update_sep(False, "Failed to flatten 3D array: {}".format(e))
    return result


def _flatten_filter_threeD_array(
    array_3d, sample_storage, model_names, hash_data_by_file, progress_call_back=None
):
    """
    Flattens the 3D array build from hash tables from each file into a json structure easily read by power bi.

    :param array_3d: A 3D array.
    :type array_3d: [[[]]]
    :param sample_storage: Storage instance used to map view template names and category names using merged lists.
    :type sample_storage: :class:`.JSONThreeDStorage`
    :param model_names: List of all model names of which view template data is included in 3D hash array.
    :type model_names: [str]
    :param hash_data_by_file: A dictionary where key is the file name without extension and value is an instance of a custom storage object
    :type hash_data_by_file: {str: [:class:`.JSONThreeDStorage`]}
    :param progress_call_back: A call back function accepting as arguments the number of the current file processed and the number of overall files to be processed, defaults to None
    :type progress_call_back: func(counter, overall_counter), optional
    :return:
        Result class instance.
        - .status True if 3D array was successfully created. Otherwise False.
        - .message will contain array size.
        -. result will contain the flatten array as first value in list
    :rtype: :class:`.Result`
    """

    result = res.Result()
    try:
        call_back_progress_counter = 0
        # flatten 3D hash data for power bi
        flattened_data = []
        for model_name, layer in enumerate(array_3d):
            for filter, row in enumerate(layer):
                for view_template, hash_value in enumerate(row):
                    flattened_data.append(
                        {
                            "view_template": sample_storage.merged_column_headers[
                                view_template
                            ],
                            "filter": sample_storage.merged_row_headers_filters[filter],
                            "model_name": model_names[model_name],
                            "hash_value": hash_value,
                        }
                    )
            call_back_progress_counter = call_back_progress_counter + 1
            if progress_call_back is not None:
                progress_call_back(call_back_progress_counter, len(hash_data_by_file))
        result.result.append(flattened_data)
    except Exception as e:
        result.update_sep(False, "Failed to flatten 3D array: {}".format(e))
    return result


def convert_vt_data_to_3d_flattened(json_files, progress_call_back=None):
    """
    Converts view template graphic overrides data stored in files into flattened json formatted hash table array for import to power bi.

    :param json_files: List of files containing view template data of Revit project files. ( One json file per Revit project file)
    :type json_files: [str]
    :param progress_call_back: A call back function accepting as arguments the number of the current file processed and the number of overall files to be processed, defaults to None
    :type progress_call_back: func(counter, overall_counter), optional

    :return:
        Result class instance.
        - .status True if flattened array was successfully created. Otherwise False.
        - .message will contain array size.
        -. result will contain the flatten array as first value in list
    :rtype: :class:`.Result`
    """

    result = res.Result()
    try:
        # load json data from all files
        json_data_loaded = _load_json_data(
            files=json_files, progress_call_back=progress_call_back
        )
        result.append_message(
            "Loaded json data from {} files.".format(len(json_data_loaded))
        )

        # get hash tables, row and column data, key is the file name
        hash_data_by_file = _get_category_hash_table_data_by_file(
            json_data_loaded, progress_call_back=progress_call_back
        )

        # map hash values to a range
        hash_data_by_file = _map_hash_values_to_range(hash_data_by_file)

        # merge row and column headers into unique value lists and store them in each storage instance
        hash_data_by_file = _merge_column_headers(hash_data_by_file=hash_data_by_file)
        hash_data_by_file = _merge_row_headers(hash_data_by_file=hash_data_by_file)

        for key, entry in hash_data_by_file.items():
            result.append_message(
                "{}: number of merged column headers: {} , merged category row headers: {} and number of merged filter row headers: {}".format(
                    key,
                    len(entry.merged_column_headers),
                    len(entry.merged_row_headers),
                    len(entry.merged_row_headers_filters),
                )
            )

        # assign padded default hash table
        assign_padded_default_hash_table_status = _assign_padded_default_array(
            hash_data_by_file=hash_data_by_file, progress_call_back=progress_call_back
        )
        result.update(assign_padded_default_hash_table_status)
        # check if all is ok
        if assign_padded_default_hash_table_status.status:
            # get the updated storage items
            hash_data_by_file = assign_padded_default_hash_table_status.result[0]
            # get row and column indices mapping to padded hash table from value table
            row_indices_status = _assign_row_indices_pointer(
                hash_data_by_file, progress_call_back=progress_call_back
            )
            result.update(row_indices_status)
            # check if all is ok
            if row_indices_status.status:
                # get the updated storage items
                hash_data_by_file = row_indices_status.result[0]
                # update the padded hash table of default values with values from the actual hash table mapped to columns and rows
                assign_default_array_values_status = _assign_default_array_values(
                    hash_data_by_file, progress_call_back=progress_call_back
                )
                result.update(assign_default_array_values_status)
                # check if all is ok
                if assign_default_array_values_status.status:
                    # get the updated storage items
                    hash_data_by_file = assign_default_array_values_status.result[0]

                    # build an 3D array from padded hash value tables
                    array_3d_status = _built_threeD_array(hash_data_by_file)
                    # check if all is ok
                    if array_3d_status.status:
                        # get the 3D array
                        array_3d_categories = array_3d_status.result[0]
                        array_3d_filters = array_3d_status.result[1]

                        # Get an arbitrary key-value pair using the dictionary's iterator
                        # since all storage instance store the same merged rows and column headers lists
                        first_key, first_value = next(iter(hash_data_by_file.items()))

                        # built a list of model names from the keys of the hash data dictionary
                        model_names = list(hash_data_by_file.keys())

                        # flatten the category 3D array for power bi
                        flatten_category_array_status = _flatten_category_threeD_array(
                            array_3d=array_3d_categories,
                            sample_storage=first_value,
                            model_names=model_names,
                            hash_data_by_file=hash_data_by_file,
                            progress_call_back=progress_call_back,
                        )
                        result.update(flatten_category_array_status)

                        # flatten the filter 3D array for power bi
                        flatten_filter_array_status = _flatten_filter_threeD_array(
                            array_3d=array_3d_filters,
                            sample_storage=first_value,
                            model_names=model_names,
                            hash_data_by_file=hash_data_by_file,
                            progress_call_back=progress_call_back,
                        )
                        result.update(flatten_filter_array_status)

                        # check if all is ok
                        if (
                            flatten_category_array_status.status
                            and flatten_filter_array_status.status
                        ):
                            # get the flattened 3D arrays
                            result.result = [
                                flatten_category_array_status.result[0],
                                flatten_filter_array_status.result[0],
                            ]
                        else:
                            raise ValueError(
                                "Failed to flatten 3D arrays: {} and {}".format(
                                    flatten_category_array_status.message,
                                    flatten_filter_array_status.message,
                                )
                            )
                    else:
                        raise ValueError(
                            "Failed to build 3D arrays: {}".format(
                                array_3d_status.message
                            )
                        )
                else:
                    raise ValueError(
                        "Failed to update values in default hash table with values from source table: {}".format(
                            assign_default_array_values_status.message
                        )
                    )
            else:
                raise ValueError(
                    "Failed to assign row and column indices: {}".format(
                        row_indices_status.message
                    )
                )
        else:
            raise ValueError(
                "Failed to assign padded default hash table: {}".format(
                    assign_padded_default_hash_table_status.message
                )
            )
    except Exception as e:
        result.update_sep(
            status=False,
            message="Failed to build flattened 3D array with: {}".format(e),
        )
    return result
