"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of functions around data storage in Revit.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Data storage can be used to project wide settings not associated with a specific element. 

Obsolete in Revit 2025 ... 
"""

#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2025, Jan Christel
# All rights reserved.

from duHast.Revit.Common.element_id import get_el_id_int

from Autodesk.Revit.DB import FilteredElementCollector


def get_built_in_parameter_double_by_element_id(doc, built_in_category, built_in_parameter):
    """
    Returns the value of a built in double parameter for every instance of a category.

    An element without the parameter, or one whose value cannot be read, is left out of the result (absent is not zero).

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param built_in_category: The category of interest.
    :type built_in_category: Autodesk.Revit.DB.BuiltInCategory
    :param built_in_parameter: The parameter to read, e.g. FLOOR_HEIGHTABOVELEVEL_PARAM.
    :type built_in_parameter: Autodesk.Revit.DB.BuiltInParameter

    :return: Element id (int) mapped to the parameter value in Revit internal units.
    :rtype: dict
    """

    values = {}
    collector = FilteredElementCollector(doc).OfCategory(built_in_category).WhereElementIsNotElementType()
    for element in collector:
        try:
            parameter = element.get_Parameter(built_in_parameter)
            if parameter is None:
                continue
            values[get_el_id_int(element.Id)] = float(parameter.AsDouble())
        except Exception:
            # one unreadable element costs its own value and not the run
            continue
    return values
