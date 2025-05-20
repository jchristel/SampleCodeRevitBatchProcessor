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
#


from duHast.Utilities.Objects.base import Base

from duHast.Revit.ColourFillSchemes.Reporting.colour_fill_scheme_defaults import (
    COLOUR_FILL_SCHEME_CSV_PROPERTY_INDEX,
    PROPERTY_FILL_SCHEME_NAME,
    PROPERTY_AREA_SCHEME_NAME,
    PROPERTY_PARAMETER_VALUE,
    PROPERTY_STORAGE_TYPE,
    PROPERTY_FILL_PATTERN_ID,
    PROPERTY_IS_IN_USE,
    PROPERTY_IS_VISIBLE,
    PROPERTY_COLOUR_RED,
    PROPERTY_COLOUR_GREEN,
    PROPERTY_COLOUR_BLUE,
)

class ColourFillStorage(Base):
    """
    A class to store colour fill information for objects.
    """

    def __init__(self):

        # ini super class to allow multi inheritance in children!
        super(ColourFillStorage, self).__init__()

        self.fill_scheme_name = ""
        self.area_scheme_name = ""
        self.parameter_value = ""
        self.fill_pattern_id = -1
        self.is_in_use=True
        self.is_visible=True
        self.storage_type=0
        self.colour_red=0
        self.colour_green=0
        self.colour_blue=0

    
    def import_from_data_row(self, data_row):
        """
        Imports data from a data row into the ColourFillStorage object.

        :param data_row: The data row to import from.
        :type data_row: list
        :raises TypeError: If data_row is not a list.
        :raises ValueError: If data_row does not have the correct number of elements.
        :raises TypeError: If data_row is not a list of strings.

        :return: None
        :rtype: None
        """

        # type checking:
        if not isinstance(data_row, list):
            raise TypeError("data_row must be of type list. Got {}".format(type(data_row)))

        if len(data_row) != len(COLOUR_FILL_SCHEME_CSV_PROPERTY_INDEX):
            raise ValueError("data_row must have {} elements. Got {}".format(len(COLOUR_FILL_SCHEME_CSV_PROPERTY_INDEX), len(data_row)))
        
        # check if the data_row is a list of strings
        if not all(isinstance(item, str) for item in data_row):
            raise TypeError("data_row must be a list of strings. Got {}".format(type(data_row)))
        
        # populate the properties from the data_row
        self.fill_scheme_name =data_row[COLOUR_FILL_SCHEME_CSV_PROPERTY_INDEX[PROPERTY_FILL_SCHEME_NAME]]
        self.area_scheme_name =data_row[COLOUR_FILL_SCHEME_CSV_PROPERTY_INDEX[PROPERTY_AREA_SCHEME_NAME]]
        self.parameter_value =data_row[COLOUR_FILL_SCHEME_CSV_PROPERTY_INDEX[PROPERTY_PARAMETER_VALUE]]
        self.storage_type = int(data_row[COLOUR_FILL_SCHEME_CSV_PROPERTY_INDEX[PROPERTY_STORAGE_TYPE]])
        self.fill_pattern_id = int(data_row[COLOUR_FILL_SCHEME_CSV_PROPERTY_INDEX[PROPERTY_FILL_PATTERN_ID]])
        self.is_in_use = bool(data_row[COLOUR_FILL_SCHEME_CSV_PROPERTY_INDEX[PROPERTY_IS_IN_USE]])
        self.is_visible = bool(data_row[COLOUR_FILL_SCHEME_CSV_PROPERTY_INDEX[PROPERTY_IS_VISIBLE]])
        self.colour_red = int(data_row[COLOUR_FILL_SCHEME_CSV_PROPERTY_INDEX[PROPERTY_COLOUR_RED]])
        self.colour_green = int(data_row[COLOUR_FILL_SCHEME_CSV_PROPERTY_INDEX[PROPERTY_COLOUR_GREEN]])
        self.colour_blue = int(data_row[COLOUR_FILL_SCHEME_CSV_PROPERTY_INDEX[PROPERTY_COLOUR_BLUE]])


    def get_report_headers(self):
        """
        Returns the headers for the report.
        
        :return: A list of headers.
        :rtype: list
        """
        return [
            "Fill Scheme Name",
            "Area Scheme Name", 
            "Parameter Value",
            "Parameter Storage Type",
            "Fill Pattern ID", 
            "Is In Use", 
            "Is Visible", 
            "Colour Red", 
            "Colour Green", 
            "Colour Blue"
        ]
    
    def get_report_data(self):
        """
        Returns the data for the report.
        
        :return: A list of data.
        :rtype: list
        """

        # get the value of the entry as a string depending on the storage type
        entry_value = "None"

        if self.storage_type == 0:
            entry_value = "None"
        elif self.storage_type == 1:
            entry_value = str(self.parameter_value)
        elif self.storage_type == 2:
            entry_value = str(self.parameter_value)
        elif self.storage_type == 3:
            entry_value = self.parameter_value
        elif self.storage_type == 4:
            entry_value = str(self.parameter_value.IntegerValue)


        return [
            self.fill_scheme_name,
            self.area_scheme_name,
            entry_value,
            str(self.storage_type),
            str(self.fill_pattern_id),
            str(self.is_in_use),
            str(self.is_visible),
            str(self.colour_red),
            str(self.colour_green),
            str(self.colour_blue)
        ]