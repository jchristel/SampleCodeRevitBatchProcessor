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

import json

from PushIt_old.Objects.settings_names import SettingsNames
from PushIt_old.settings import DU_HAST_SETTINGS_DIRECTORY_NAME
from duHast.Utilities.Objects.result import Result
from duHast.Utilities.Objects.base import Base
from duHast.Utilities.files_json import read_json_data_from_file, write_json_to_file
from duHast.Utilities.directory_io import create_target_directory, directory_exists
from duHast.Utilities.files_io import get_directory_path_from_file_path
from duHast.Utilities.utility import get_local_app_data_path


class Settings(Base):
    def __init__(self, j=None, settings_file_path=None):
        """
        Implementation of a settings class.

        :param j: JSON string or dictionary to parse settings from.
        :type j: str, dict, optional
        :raises TypeError: "Input must be a JSON string or a dictionary."
        """

        # ini super class to allow multi inheritance in children!
        super(Settings, self).__init__()

        # Set the settings file path
        self._settings_file_path = settings_file_path

        # Set default values
        self._rooms_data_file_path = None

        # the revit family categories into which data can be pushed
        # default is Walls
        self._push_it_revit_target_categories = ["Walls"]

        # last selected column filter
        self._last_column_filter = None

        # last column filter value
        self._last_column_filter_value = None

        #  directory path to where custom room shapes are to be stored
        self._custom_room_shapes_directory = None

        # Check if a JSON string / dictionary is provided
        if j:
            if isinstance(j, str):
                self._ini_from_file_data(j)
            elif not isinstance(j, dict):
                raise TypeError("Input must be a JSON string or a dictionary.")

        # check if settings file path is provided
        if self._settings_file_path is None:
            raise ValueError("Settings file path must be provided.")

    @property
    def rooms_data_file_path(self):
        """Read-only property to access the parsed JSON data."""
        return self._rooms_data_file_path

    @rooms_data_file_path.setter
    def rooms_data_file_path(self, value):
        if not (isinstance(value, str)):
            raise ValueError(
                "Value must be of type str, got {} instead.".format(type(value))
            )

        # only update if value has changed
        if value != self._rooms_data_file_path:
            self._rooms_data_file_path = value

    @property
    def push_it_revit_target_categories(self):
        """Read-only property to access the parsed JSON data."""
        return self._push_it_revit_target_categories

    @push_it_revit_target_categories.setter
    def push_it_revit_target_categories(self, value):
        if not (isinstance(value, list)):
            raise ValueError(
                "Value must be of type list, got {} instead.".format(type(value))
            )

        # only update if value has changed
        if sorted(value) != sorted(self._push_it_revit_target_categories):
            self._push_it_revit_target_categories = value

    @property
    def last_column_filter(self):
        """Read-only property to access the parsed JSON data."""
        return self._last_column_filter

    @last_column_filter.setter
    def last_column_filter(self, value):
        if not (isinstance(value, str)):
            raise ValueError(
                "Value must be of type str, got {} instead.".format(type(value))
            )

        # only update if value has changed
        if value != self._last_column_filter:
            self._last_column_filter = value

    @property
    def last_column_filter_value(self):
        """Read-only property to access the parsed JSON data."""
        return self._last_column_filter_value

    @last_column_filter_value.setter
    def last_column_filter_value(self, value):
        if not (isinstance(value, str)):
            raise ValueError(
                "Value must be of type str, got {} instead.".format(type(value))
            )

        # only update if value has changed
        if value != self._last_column_filter_value:
            self._last_column_filter_value = value

    @property
    def custom_room_shapes_directory(self):
        """Read-only property to access the parsed JSON data."""
        return self._custom_room_shapes_directory

    @custom_room_shapes_directory.setter
    def custom_room_shapes_directory(self, value):
        if not (isinstance(value, str)):
            raise ValueError(
                "Value must be of type str, got {} instead.".format(type(value))
            )

        # only update if value has changed
        if value != self._custom_room_shapes_directory:
            self._custom_room_shapes_directory = value

    def _ini_from_file_data(self, data):
        """
        Initialise the settings from a dictionary.

        :param data: The dictionary to initialise the settings from.
        :type data: dict
        :raises ValueError: "JSON must contain 'rooms_data_file_path' key(s)."
        :raises ValueError: "JSON must contain 'custom_room_shapes_directory' key(s)."
        :raises ValueError: "JSON must contain 'push_it_revit_target_categories' key(s)."
        :raises ValueError: "JSON must contain 'last_column_filter' key(s)."
        :raises ValueError: "JSON must contain 'last_column_filter_value' key(s)."
        :raises ValueError: "Expected rooms_data_file_path as str, got {} instead".
        :raises ValueError: "Expected custom_room_shapes_directory as str, got {} instead".
        :raises ValueError: "Expected push_it_revit_target_categories as list, got {} instead".
        :raises ValueError: "Expected last_column_filter as str, got {} instead".
        :raises ValueError: "Expected last_column_filter_value as str, got {} instead".
        :raises Exception: "Settings failed to initialise with: {}".
        """

        try:
            if isinstance(data, str):
                # Parse the JSON string
                data_json = json.loads(data)
            elif not isinstance(data, dict):
                raise TypeError("Input must be a JSON string or a dictionary.")
            else:
                data_json = data

            # Validate presence of required keys
            if SettingsNames.ROOMS_DATA_FILE_PATH.value not in data_json:
                raise ValueError("JSON must contain 'rooms_data_file_path' key(s).")

            if SettingsNames.CUSTOM_ROOM_SHAPES_DIRECTORY.value not in data_json:
                raise ValueError(
                    "JSON must contain 'custom_room_shapes_directory' key(s)."
                )

            if SettingsNames.PUSH_IT_REVIT_TARGET_CATEGORIES.value not in data_json:
                raise ValueError(
                    "JSON must contain 'push_it_revit_target_categories' key(s)."
                )

            if SettingsNames.LAST_COLUMN_FILTER.value not in data_json:
                raise ValueError("JSON must contain 'last_column_filter' key(s).")

            if SettingsNames.LAST_COLUMN_FILTER_VALUE.value not in data_json:
                raise ValueError("JSON must contain 'last_column_filter_value' key(s).")

            # Parse the JSON data
            try:
                self._rooms_data_file_path = data_json.get(
                    SettingsNames.ROOMS_DATA_FILE_PATH.value, self._rooms_data_file_path
                )
                if not (
                    isinstance(self._rooms_data_file_path, str)
                    or self._rooms_data_file_path is None
                ):
                    raise ValueError(
                        "Expected rooms_data_file_path as str, got {} instead".format(
                            type(self._rooms_data_file_path)
                        )
                    )

                self._custom_room_shapes_directory = data_json.get(
                    SettingsNames.CUSTOM_ROOM_SHAPES_DIRECTORY.value,
                    self._custom_room_shapes_directory,
                )
                if not (
                    isinstance(self._custom_room_shapes_directory, str)
                    or self._custom_room_shapes_directory is None
                ):
                    raise ValueError(
                        "Expected custom_room_shapes_directory as str, got {} instead".format(
                            type(self._custom_room_shapes_directory)
                        )
                    )

                self._push_it_revit_target_categories = data_json.get(
                    SettingsNames.PUSH_IT_REVIT_TARGET_CATEGORIES.value,
                    self._push_it_revit_target_categories,
                )
                if not (isinstance(self._push_it_revit_target_categories, list)):
                    raise ValueError(
                        "Expected push_it_revit_target_categories as list, got {} instead".format(
                            type(self._push_it_revit_target_categories)
                        )
                    )

                self._last_column_filter = data_json.get(
                    SettingsNames.LAST_COLUMN_FILTER.value, self._last_column_filter
                )
                if not (
                    isinstance(self._last_column_filter, str)
                    or self._last_column_filter is None
                ):
                    raise ValueError(
                        "Expected last_column_filter as str, got {} instead".format(
                            type(self._last_column_filter)
                        )
                    )

                self._last_column_filter_value = data_json.get(
                    SettingsNames.LAST_COLUMN_FILTER_VALUE.value,
                    self._last_column_filter_value,
                )
                if not (
                    isinstance(self._last_column_filter_value, str)
                    or self._last_column_filter_value is None
                ):
                    raise ValueError(
                        "Expected last_column_filter_value as str, got {} instead".format(
                            type(self._last_column_filter_value)
                        )
                    )
            except Exception as e:
                raise type(e)("Settings failed to initialise with: {}".format(e))
        except Exception as e:
            raise type(e)("{}".format(e))

    def load_settings(self):
        """
        Load the settings from the settings file.
        """

        read_result = read_json_data_from_file(self._settings_file_path)
        # can fail if first time running the app
        if read_result.status is False:
            # use default settings
            return None

        data = read_result.result[0]
        # initialise the settings
        self._ini_from_file_data(data)

    def save_settings(self):
        """
        Save the settings to the settings file.
        """

        return_value = Result()
        # check if the settings directory exists
        if not directory_exists(
            get_directory_path_from_file_path(self._settings_file_path)
        ):

            # create the settings directory
            if (
                create_target_directory(
                    get_local_app_data_path(), DU_HAST_SETTINGS_DIRECTORY_NAME
                )
                is False
            ):
                return_value.update_sep(False, "Failed to create settings directory.")
                return return_value

        # create a dictionary with the settings data
        # rather then using the class since it has properties I don't want to save
        settings_data = {
            SettingsNames.ROOMS_DATA_FILE_PATH.value: self._rooms_data_file_path,
            SettingsNames.CUSTOM_ROOM_SHAPES_DIRECTORY.value: self._custom_room_shapes_directory,
            SettingsNames.PUSH_IT_REVIT_TARGET_CATEGORIES.value: self._push_it_revit_target_categories,
            SettingsNames.LAST_COLUMN_FILTER.value: self._last_column_filter,
            SettingsNames.LAST_COLUMN_FILTER_VALUE.value: self._last_column_filter_value,
            # Add other settings here
        }

        # save json settings to file
        write_result = write_json_to_file(settings_data, self._settings_file_path)

        # return the outcome of the operation
        return write_result
