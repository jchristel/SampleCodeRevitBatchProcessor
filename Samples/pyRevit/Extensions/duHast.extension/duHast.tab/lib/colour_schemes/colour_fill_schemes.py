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


from duHast.Utilities.Objects.result import Result

from Autodesk.Revit.DB import ElementClassFilter, FilteredElementCollector, ColorFillScheme

def get_all_colour_schemes(doc):
    """Returns a list of available colour schemes."""
    color_fill_schemes = FilteredElementCollector(doc).OfClass(ColorFillScheme)
    return color_fill_schemes


def get_colour_fill_scheme_from_area_scheme(doc, area_scheme):
    """Returns a colour fill scheme from an area scheme."""
    
    # set up an element filter to find the dependent elements
    dependent_element_filter = ElementClassFilter(ColorFillScheme)

    # get alll area fill schemes
    dependent_element_ids = area_scheme.GetDependentElements(dependent_element_filter)

    # get the area fill schemes from the ids
    colour_fill_schemes = []

    if(dependent_element_ids is None):
        colour_fill_schemes

    # loop over the dependent element ids and get the colour fill schemes
    for dependent_element_id in dependent_element_ids:
        colour_fill_scheme = doc.GetElement(dependent_element_id)
        if colour_fill_scheme is not None:
            colour_fill_schemes.append(colour_fill_scheme)
    
    return colour_fill_schemes