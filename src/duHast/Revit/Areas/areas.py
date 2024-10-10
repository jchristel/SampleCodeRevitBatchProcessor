"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Revit areas helper functions.
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


from Autodesk.Revit.DB import (
    BuiltInCategory,
    ElementClassFilter,
    FilteredElementCollector,
    ViewPlan,
)


def get_areas_by_scheme_name(doc, scheme_name):
    """
    Retrieves a list of areas that belong to a specific area scheme.

    Args:
        doc (Revit document): The Revit document from which to retrieve the areas.
        scheme_name (str): The name of the area scheme to filter the areas by.

    Returns:
        list: A list of areas that belong to the specified area scheme.
    """
    return_value = []
    areas = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Areas)
    for area in areas:
        if area.AreaScheme.Name == scheme_name:
            return_value.append(area)
    return return_value


def get_area_schemes(doc):
    """
    Retrieves all area schemes in Autodesk Revit.

    Args:
        doc (Revit Document): The Revit document in which to search for area schemes.

    Returns:
        area_schemes: A collection of area schemes in the Revit document.
    """
    area_schemes = FilteredElementCollector(doc).OfCategory(
        BuiltInCategory.OST_AreaSchemes
    )
    return area_schemes


def get_area_scheme_by_name(doc, area_scheme_name):
    """
    Retrieves an area scheme by its name in Autodesk Revit.

    Args:
        doc (Revit Document): The Revit document in which to search for the area scheme.
        area_scheme_name (str): The name of the area scheme to retrieve.

    Returns:
        AreaScheme: The area scheme with the specified name, or None if no match is found.
    """
    return_value = None
    area_schemes = get_area_schemes(doc=doc)
    if any(area_schemes):
        for area_scheme in area_schemes:
            if area_scheme.Name == area_scheme_name:
                return area_scheme
    return return_value


def get_views_by_area_scheme_name(doc, area_scheme_name):
    """
    Retrieves all views associated with a given area scheme name in Autodesk Revit.

    Args:
        doc (Revit Document): The Revit document in which to search for views.
        area_scheme_name (str): The name of the area scheme to filter views by.

    Returns:
        list: A list of ViewPlan objects that are associated with the given area scheme name.
    """
    return_value = []
    area_scheme = get_area_scheme_by_name(doc, area_scheme_name)
    if area_scheme:
        filter = ElementClassFilter(ViewPlan)
        dependent_element_ids = area_scheme.GetDependentElements(filter)
        for id in dependent_element_ids:
            element = doc.GetElement(id)
            return_value.append(element)
    return return_value

