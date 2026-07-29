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
