"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Module containing view templates to hash tables functions.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- reads json files containing view template data and converts them to a combined json file containing a flattened 3D  array presenting hash tables
- exports json files to parquet format
"""

import os
import pandas as pd

# import common library
import settings as settings  # sets up all commonly used variables and path locations!

import duHast.Utilities.Objects.result as res
from duHast.Utilities.files_get import (
    get_files_single_directory,
    get_file_name_without_ext,
)
from duHast.Utilities.files_io import (
    file_delete
)
from duHast.Revit.Views.Reporting.views_data_3d_hash_report import (
    convert_vt_data_to_3d_flattened,
)
from duHast.Utilities.files_json import write_json_to_file


def combine_vt_reports(directory_path):
    """
    Combines json formatted view template data files into a json formatted hash table for import into power bi.

    :param directory_path: Fully qualified directory path to where view template data files are stored
    :type directory_path: str
    :return:
        Result class instance.

        - result.status False if an exception occurred, otherwise True.
        - result.message will contain processing messages.
        - result.result empty list

        On exception:

        - result.status (bool) will be False.
        - result.message will contain the exception message.
        - result.result will be an empty list

    :rtype: :class:`.Result`
    """

    result = res.Result()
    try:
        # get files
        json_files = get_files_single_directory(
            folder_path=directory_path,
            file_prefix="",
            file_suffix=settings.REPORT_EXTENSION_VIEW_TEMPLATE_OVERRIDES,
            file_extension=settings.REPORT_FILE_NAME_EXTENSION,
        )

        # filter files to the ones specified in settings
        filtered_files = []
        for file_path in json_files:
            file_name = get_file_name_without_ext(file_path)
            if file_name in settings.VIEW_TEMPLATE_FILE_LIST:
                filtered_files.append(file_path)

        result.append_message(
            "Found {} files: {}".format(len(filtered_files), filtered_files)
        )

        # check if any valid files left
        if len(filtered_files) > 0:
            # convert view template data to hash table
            data_result = convert_vt_data_to_3d_flattened(
                json_files=filtered_files, progress_call_back=None
            )
            result.update(data_result)
            # check if conversion process was successful
            if data_result.status:
                # combined report file names
                combined_report_file_name_categories = os.path.join(
                    directory_path,
                    settings.COMBINED_REPORT_NAME_VIEW_TEMPLATE_OVERRIDES,
                )
                combined_report_file_name_filters = os.path.join(
                    directory_path,
                    settings.COMBINED_REPORT_NAME_VIEW_TEMPLATE_FILTER_OVERRIDES
                )
                # write data to file
                # categories
                write_data_categories_result = write_json_to_file(
                    data_result.result[0], combined_report_file_name_categories
                )
                result.update(write_data_categories_result)
                # filters
                write_data_filters_result = write_json_to_file(
                    data_result.result[1], combined_report_file_name_filters
                )
                result.update(write_data_filters_result)
                # check write outcomes
                if write_data_categories_result.status == False:
                    raise ValueError(write_data_categories_result.message)
                if write_data_filters_result.status == False:
                    raise ValueError(write_data_filters_result.message)
            else:
                raise ValueError(data_result.message)

        else:
            raise ValueError(
                "No matching view template data files found in: {}".format(
                    directory_path
                )
            )
    except Exception as e:
        result.update_sep(
            False, "Failed to create hash table files of view templates: {}".format(e)
        )
    return result

def convert_vt_reports_to_parquet(directory_path):
    '''
    Converts large view template hash files in .json format into smaller parquet files.

    :param directory_path: Fully qualified directory path containing hash table files.
    :type directory_path: str
    :return:
        Result class instance.

        - result.status False if an exception occurred, otherwise True.
        - result.message will contain processing messages.
        - result.result empty list

        On exception:

        - result.status (bool) will be False.
        - result.message will contain the exception message.
        - result.result will be an empty list

    :rtype: :class:`.Result`
    '''

    result = res.Result()
    try:
        # get files
        json_files = get_files_single_directory(
            folder_path=directory_path,
            file_prefix=settings.VIEW_TEMPLATE_HASH_FILE_PREFIX,
            file_suffix=settings.VIEW_TEMPLATE_HASH_FILE_SUFFIX,
            file_extension=settings.REPORT_JSON_FILE_EXTENSION,
        )
        if(len(json_files)>0):
            for j_file in json_files:
                df = pd.read_json(j_file)
                file_name = get_file_name_without_ext(j_file)
                parquet_output_path = os.path.join(directory_path, file_name+".parquet")
                df.to_parquet(parquet_output_path, engine="fastparquet")
                result.append_message("Converted file: {} to: {}".format(j_file, parquet_output_path))
        else:
            raise ValueError(
                "No matching view template data files found in: {}".format(
                    directory_path
                )
            )
    except Exception as e:
        result.update_sep(
            False, "Failed to convert json files to parquet files: {}".format(e)
        )
    return result

def delete_hash_table_vt_json_reports(directory_path):
    '''
    Deletes json formatted view template hash table files.

    :param directory_path: Fully qualified directory path containing hash table files.
    :type directory_path: str
    :return:
        Result class instance.

        - result.status False if an exception occurred, otherwise True.
        - result.message will contain processing messages.
        - result.result empty list

        On exception:

        - result.status (bool) will be False.
        - result.message will contain the exception message.
        - result.result will be an empty list

    :rtype: :class:`.Result`
    '''
    result = res.Result()
    try:
        # get files
        json_files = get_files_single_directory(
            folder_path=directory_path,
            file_prefix=settings.VIEW_TEMPLATE_HASH_FILE_PREFIX,
            file_suffix=settings.VIEW_TEMPLATE_HASH_FILE_SUFFIX,
            file_extension=settings.REPORT_JSON_FILE_EXTENSION,
        )
        if(len(json_files)>0):
            for j_file in json_files:
                flag_delete =file_delete(j_file)
                result.append_message("Deleted file: {} with status: {}".format(j_file, flag_delete))
        else:
            raise ValueError(
                "No matching view template hash json files found in: {}".format(
                    directory_path
                )
            )
    except Exception as e:
        result.update_sep(
            False, "Failed to delete json view template hash files: {}".format(e)
        )
    return result