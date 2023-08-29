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
    get_files_single_directory,
    get_file_name_without_ext,
)
from duHast.Revit.Views.Reporting.views_data_hash_report import (
    _get_hash_headers,
    _get_hash_rows_categories,
    _get_hash_for_category_overrides,
)
from duHast.Revit.Views.Reporting.view_reports_json_props import PROP_FILE_NAME

from duHast.Revit.Views.Reporting.Objects.json_conversion_storage import (
    JSONThreeDStorage,
)


def _load_json_data(files):
    json_data = {}
    for file_path in files:
        file_name = get_file_name_without_ext(file_path=file_path)
        json_single_data = read_view_data_from_file(file_path=file_path)
        json_data[file_name] = json_single_data
    return json_data


def _get_hash_table_data_by_file(view_settings):
    dic_tables_by_file = {}
    for key, vt_setting in view_settings.items():
        column_headers = _get_hash_headers(vt_setting)
        row_headers = _get_hash_rows_categories(vt_setting)
        hash_table = _get_hash_for_category_overrides(
            headers=column_headers, row_headers=row_headers, views_settings=vt_setting
        )
        storage = JSONThreeDStorage()
        storage.column_headers = column_headers
        storage.row_headers = row_headers
        storage.hash_table = hash_table
        dic_tables_by_file[key] = storage

    return dic_tables_by_file


def _merge_column_headers(view_settings):
    """_summary_

    Args:
        view_settings (_type_): _description_
        index (_type_): 0 is column header, 1 is row header

    Returns:
        _type_: _description_
    """
    data = []
    for key, vt_setting in view_settings.items():
        data = sorted(list(set(data) | set(vt_setting.column_headers)))

    for key, vt_setting in view_settings.items():
        vt_setting.merged_column_headers = data


def _merge_row_headers(view_settings):
    """_summary_

    Args:
        view_settings (_type_): _description_
        index (_type_): 0 is column header, 1 is row header

    Returns:
        _type_: _description_
    """
    data = []
    for key, vt_setting in view_settings.items():
        data = sorted(list(set(data) | set(vt_setting.row_headers)))

    for key, vt_setting in view_settings.items():
        vt_setting.merged_row_headers = data


def _get_padded_default_array(
    merged_row_headers,
    merged_column_headers,
):
    # Create a new padded 2D array
    padded_array = [
        [-1 for entry in merged_column_headers] for entry in merged_row_headers
    ]
    return padded_array


def _update_default_array_values(row_indices, col_indices, default_array, value_array):
    # Fill in the values from array_model_a
    for i, row_index in enumerate(row_indices):
        for j, col_index in enumerate(col_indices):
            default_array[row_index][col_index] = value_array[i][j]
    return default_array


def convert_vt_data_to_3d_flattened(directory_path):
    result = res.Result()
    try:
        # get all files containing view template files in a given directory
        json_files = get_files_single_directory(
            folder_path=directory_path,
            file_prefix="",
            file_suffix="VT_Overrides",
            file_extension=".csv",
        )
        result.append_message("Found {} files: {}".format(len(json_files), json_files))

        # load json data from all files found
        json_data_loaded = _load_json_data(json_files)
        result.append_message(
            "Loaded json data from {} files.".format(len(json_data_loaded))
        )

        # get hash tables, row and column data, key is the file name
        hash_data_by_file = _get_hash_table_data_by_file(json_data_loaded)

        # merge row and column headers into unique value lists and store them in each storage instance
        _merge_column_headers(view_settings=hash_data_by_file)
        _merge_row_headers(view_settings=hash_data_by_file)
        for key, entry in hash_data_by_file.items():
            result.append_message(
                "{}: number of merged column headers: {} and merged row headers: {}".format(
                    key, len(entry.merged_column_headers), len(entry.merged_row_headers)
                )
            )

        # build default hash tables where all values are -1
        for key, hash_by_file in hash_data_by_file.items():
            padded_array = _get_padded_default_array(
                merged_column_headers=hash_by_file.merged_column_headers, merged_row_headers=hash_by_file.merged_row_headers
            )
            hash_data_by_file[key].padded_default_hash_table = padded_array
            result.append_message("{}: Created padded default value array of size {} by {}".format(key, len(padded_array), len(padded_array[0])))
        
        # build row and column indices list for mapping of value hash table entries to default hash table
        for key, hash_by_file in hash_data_by_file.items():
            # Find the indices for row and column headers in the merged headers
            row_indices_all = [hash_by_file.merged_row_headers.index(row) for row in hash_by_file.row_headers]
            column_indices_all = [hash_by_file.merged_column_headers.index(col) for col in hash_by_file.column_headers]
            
            hash_data_by_file[key].row_indices=row_indices_all
            hash_data_by_file[key].column_indices=column_indices_all
            result.append_message("{}: Created row: {} and column: {} indices mapper.".format(key, len(row_indices_all), len(column_indices_all)))
        
        # update the default hash table for each file with values from the value hash table from the same file
        for key, hash_by_file in hash_data_by_file.items():
            updated_array = _update_default_array_values(
                row_indices=hash_by_file.row_indices, 
                col_indices=hash_by_file.column_indices, 
                default_array=hash_by_file.padded_default_hash_table, 
                value_array=hash_by_file.hash_table
            )
            hash_by_file.padded_value_hash_table = updated_array
            result.append_message("{}: Updated padded default value array with values of size {} by {}".format(key, len(updated_array), len(updated_array[0])))
        
        # build an 3D array from padded hash value tables
        array_3d = []
        z_value = 0
        x_value = 0
        y_value = 0
        for key, hash_by_file in hash_data_by_file.items():
            array_3d.append(hash_by_file.padded_value_hash_table)
            x_value = len(hash_by_file.padded_value_hash_table)
            y_value = len(hash_by_file.padded_value_hash_table[0])
            z_value = z_value + 1
        result.append_message("Built 3D array of size: number of files: {} , by number of categories: {} , by number of view templates: {}".format(z_value,x_value,y_value))
        
        # Get an arbitrary key-value pair using the dictionary's iterator
        # since all storage instance store the same merged rows and column headers lists
        first_key, first_value = next(iter(hash_data_by_file.items()))
        
        # built a list of model names from the keys of the hash data dictionary
        model_names = list(hash_data_by_file.keys())
        
        # flatten 3D hash data for power bi
        flattened_data=[]
        for model_name, layer in enumerate(array_3d):
            for category, row in enumerate(layer):
                for view_template, hash_value in enumerate(row):
                    flattened_data.append(
                        {
                            "view_template": first_value.merged_column_headers[view_template],
                            "category": first_value.merged_row_headers[category],
                            "model_name": model_names[model_name],
                            "hash_value": hash_value,
                        }
                    )
        result.append_message("Flattened array: {} entries.".format(len(flattened_data)))
        result.result.append(flattened_data)
    except Exception as e:
        result.update_sep(status=False, message="Failed to build flattened 3D array with: {}".format(e))
    return result