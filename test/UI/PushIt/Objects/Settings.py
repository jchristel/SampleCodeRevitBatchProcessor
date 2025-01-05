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


class Settings(Base):
    def __init__(self, j=None):
        """
        Implementation of a settings class.

        :param j: JSON string or dictionary to parse settings from.
        :type j: str, dict, optional
        :raises TypeError: "Input must be a JSON string or a dictionary."
        """

        # ini super class to allow multi inheritance in children!
        super(Settings, self).__init__()

        self._library_path = None

        # Check if a JSON string / dictionary is provided
        if j:
            if isinstance(j, str):
                # Parse the JSON string
                j = json.loads(j)
            elif not isinstance(j, dict):
                raise TypeError("Input must be a JSON string or a dictionary.")

            # Validate presence of required keys
            if SettingsNames.LIBRARY_PATH.value not in j:
                raise ValueError("JSON must contain 'library_path' key(s).")

            try:
                self._library_path = j.get(
                    SettingsNames.LIBRARY_PATH.value, self._library_path
                )
                if not (isinstance(self._library_path, str)):
                    raise ValueError(
                        "Expected library_path as str, got {} instead".format(
                            type(self._library_path)
                        )
                    )
            except Exception as e:
                raise type(e)("Settings failed to initialise with: {}".format(e))

    @property
    def library_path(self):
        """Read-only property to access the parsed JSON data."""
        return self._library_path

    @library_path.setter
    def library_path(self, value):
        if not (isinstance(value, str)):
            raise ValueError(
                "Value must be of type str, got {} instead.".format(type(value))
            )
        self._library_path = value
