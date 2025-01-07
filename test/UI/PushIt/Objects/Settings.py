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

from duHast.Utilities.Objects.base import Base
from PushIt.Objects.settings_names import SettingsNames
from duHast.Utilities.files_json import read_json_data_from_file, write_json_to_file


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
        self._push_it_revit_target_categories = None

        # last selected column filter
        self._last_column_filter = None

        # last column filter value
        self._last_column_filter_value = None

        #  directory path to where custom room shapes are to be stored
        self._custom_room_shapes_directory = None

        # Check if a JSON string / dictionary is provided
        if j:
            if isinstance(j, str):
                # Parse the JSON string
                j = json.loads(j)
            elif not isinstance(j, dict):
                raise TypeError("Input must be a JSON string or a dictionary.")

            # Validate presence of required keys
            if SettingsNames.ROOMS_DATA_FILE_PATH.value not in j:
                raise ValueError("JSON must contain 'rooms_data_file_path' key(s).")

            if SettingsNames.CUSTOM_ROOM_SHAPES_DIRECTORY.value not in j:
                raise ValueError(
                    "JSON must contain 'custom_room_shapes_directory' key(s)."
                )

            if SettingsNames.PUSH_IT_REVIT_TARGET_CATEGORIES.value not in j:
                raise ValueError(
                    "JSON must contain 'push_it_revit_target_categories' key(s)."
                )

            if SettingsNames.LAST_COLUMN_FILTER.value not in j:
                raise ValueError("JSON must contain 'last_column_filter' key(s).")

            if SettingsNames.LAST_COLUMN_FILTER_VALUE.value not in j:
                raise ValueError("JSON must contain 'last_column_filter_value' key(s).")

            # Parse the JSON data
            try:
                self._rooms_data_file_path = j.get(
                    SettingsNames.ROOMS_DATA_FILE_PATH.value, self._rooms_data_file_path
                )
                if not (isinstance(self._rooms_data_file_path, str)):
                    raise ValueError(
                        "Expected rooms_data_file_path as str, got {} instead".format(
                            type(self._rooms_data_file_path)
                        )
                    )

                self._custom_room_shapes_directory = j.get(
                    SettingsNames.CUSTOM_ROOM_SHAPES_DIRECTORY.value,
                    self._custom_room_shapes_directory,
                )
                if not (isinstance(self._custom_room_shapes_directory, str)):
                    raise ValueError(
                        "Expected custom_room_shapes_directory as str, got {} instead".format(
                            type(self._custom_room_shapes_directory)
                        )
                    )

                self._push_it_revit_target_categories = j.get(
                    SettingsNames.PUSH_IT_REVIT_TARGET_CATEGORIES.value,
                    self._push_it_revit_target_categories,
                )
                if not (isinstance(self._push_it_revit_target_categories, list)):
                    raise ValueError(
                        "Expected push_it_revit_target_categories as list, got {} instead".format(
                            type(self._push_it_revit_target_categories)
                        )
                    )

                self._last_column_filter = j.get(
                    SettingsNames.LAST_COLUMN_FILTER.value, self._last_column_filter
                )
                if not (isinstance(self._last_column_filter, str)):
                    raise ValueError(
                        "Expected last_column_filter as str, got {} instead".format(
                            type(self._last_column_filter)
                        )
                    )

                self._last_column_filter_value = j.get(
                    SettingsNames.LAST_COLUMN_FILTER_VALUE.value,
                    self._last_column_filter_value,
                )
                if not (isinstance(self._last_column_filter_value, str)):
                    raise ValueError(
                        "Expected last_column_filter_value as str, got {} instead".format(
                            type(self._last_column_filter_value)
                        )
                    )

            except Exception as e:
                raise type(e)("Settings failed to initialise with: {}".format(e))

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
        self._last_column_filter_value = value
    
    def load_settings(self):
        try:
            read_result = read_json_data_from_file(self._settings_file_path)
            if read_result.status is False:
                print(
                    "failed to read settings file: {} with: {}".format(
                        self._settings_file_path, read_result.message
                    )
                )
                return None
            data = read_result.result[0]
        except FileNotFoundError:
            pass
