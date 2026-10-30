"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Helper functions for Revit spaces. Mirrors Rooms.rooms API usage.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

import clr

clr.AddReference("System.Core")
from System import Linq

clr.ImportExtensions(Linq)
import System

from Autodesk.Revit.DB import (
    BuiltInCategory,
    FilteredElementCollector,
)


def get_all_spaces(doc):
    """
    Gets a list of spaces from the model using built in category.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: All the spaces in the model as a list.
    :rtype: List Autodesk.Revit.DB.SpatialElement (Space)
    """

    try:
        return FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_MEPSpaces).ToList()
    except Exception:
        # Fallback: return empty list if category not available in the Revit version
        return []


def get_all_spaces_raising_on_failure(doc):
    """
    Gets a list of all spaces from the model. Unlike :func:`get_all_spaces` a failure to collect is NOT swallowed: it raises.

    Use this where 'the model has no spaces' and 'the collector failed' must not look the same.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: All spaces in the model.
    :rtype: list[Autodesk.Revit.DB.Mechanical.Space]
    """

    return list(FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_MEPSpaces).ToElements())
