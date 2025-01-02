import json

from duHast.Utilities.Objects.base import Base
from PushIt.Objects.settings_names import SettingsNames

class Settings(Base):
    def __init__(self, j=None):
        """
        Implementation of a settings.

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
            if (
                SettingsNames.LIBRARY_PATH.value not in j
            ):
                raise ValueError("JSON must contain 'library_path' key(s).")
            
            try:
                self._library_path = j.get(SettingsNames.LIBRARY_PATH.value, self._library_path)
                if not (isinstance(self._library_path, str)):
                    raise ValueError("Expected library_path as str, got {} instead".format(type(self._library_path)))
            except Exception as e:
                raise type(e)("Settings failed to initialise with: {}".format(e))

    @property
    def library_path(self):
        """Read-only property to access the parsed JSON data."""
        return self._library_path
    
    @library_path.setter
    def library_path(self, value):
        if not(isinstance (value,str)):
            raise ValueError("Value must be of type str, got {} instead.".format(type(value)))
        self._library_path = value