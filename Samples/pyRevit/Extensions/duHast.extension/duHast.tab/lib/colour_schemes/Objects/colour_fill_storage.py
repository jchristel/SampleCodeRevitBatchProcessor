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
        self.colour_red=0
        self.colour_green=0
        self.colour_blue=0

    
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
        return [
            self.fill_scheme_name,
            self.area_scheme_name,
            self.parameter_value,
            str(self.fill_pattern_id),
            str(self.is_in_use),
            str(self.is_visible),
            str(self.colour_red),
            str(self.colour_green),
            str(self.colour_blue)
        ]