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

from Autodesk.Revit.DB import ElementId


from duHast.Revit.ColourFillSchemes.Objects.colour_fill_storage import ColourFillStorage
from duHast.Revit.ColourFillSchemes.colour_fill_scheme_entry import get_entry_value_storage_type


def get_report_data_of_colour_fill_scheme(doc, colour_fill_scheme):

    """
    Retrieves the report data from a given colour fill scheme.

    :param colour_fill_scheme: The colour fill scheme element from which to retrieve report data.
    :type colour_fill_scheme: Autodesk.Revit.DB.ColorFillScheme
    
    :return: A dictionary containing the report data.
    :rtype: dict
    """

    # get the report data
    report_data = []

    # get the area scheme id
    area_scheme_id = colour_fill_scheme.AreaSchemeId
    
    area_scheme_name = "Colour By Room Property"
    if area_scheme_id.Equals(ElementId.InvalidElementId) == False:
        # get the area scheme name
        area_scheme = doc.GetElement(area_scheme_id)
        area_scheme_name = area_scheme.Name 
    
    # get all entries in the colour fill scheme
    entries = colour_fill_scheme.GetEntries()

    # loop over the entries and get the report data
    for entry in entries:
        entry_data = ColourFillStorage()
        entry_data.fill_scheme_name = colour_fill_scheme.Name
        entry_data.area_scheme_name = area_scheme_name

        # get the value and storage type of the entry
        value_type = get_entry_value_storage_type(entry)
        entry_data.parameter_value = value_type[0]
        entry_data.storage_type = value_type[1]

        entry_data.fill_pattern_id = entry.FillPatternId.IntegerValue
        entry_data.is_in_use = entry.IsInUse
        entry_data.is_visible = entry.IsVisible
        entry_data.colour_red = entry.Color.Red
        entry_data.colour_green = entry.Color.Green
        entry_data.colour_blue = entry.Color.Blue
        report_data.append(entry_data)

        
    return report_data