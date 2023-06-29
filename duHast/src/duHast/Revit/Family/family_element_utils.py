"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Revit families helper functions retrieving elements from a family.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
#
# License:
#
#
# Revit Batch Processor Sample Code
#
# Copyright (c) 2023  Jan Christel
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#


import Autodesk.Revit.DB as rdb

LINE_NAMES = [
    "Model Lines",  # 3D families
    "Symbolic Lines",  # 3D families
    "Line",  # annotation (tag) families
]


def get_all_generic_forms_in_family(doc):
    """
    Filters all generic forms (3D extrusions) in family.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A collector of Autodesk.Revit.DB.GenericForm.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    """

    col = rdb.FilteredElementCollector(doc).OfClass(rdb.GenericForm)
    return col


def get_all_curve_based_elements_in_family(doc):
    """
    Filters all curve based elements in family.
    These are:
        - Symbolic Lines
        - Model Lines
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A list of Autodesk.Revit.DB.CurveElement.
    :rtype: list Autodesk.Revit.DB.CurveElement
    """

    elements = []
    col = rdb.FilteredElementCollector(doc).OfClass(rdb.CurveElement)
    for c in col:
        if rdb.Element.Name.GetValue(c) in LINE_NAMES:
            elements.append(c)
    return elements


def get_all_model_text_elements_in_family(doc):
    """
    Filters all model text elements in family.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A collector of Autodesk.Revit.DB.ModelText.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    """

    col = rdb.FilteredElementCollector(doc).OfClass(rdb.ModelText)
    return col


def get_all_reference_planes_in_family(doc):
    """
    Filters all reference planes in family.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A collector of Autodesk.Revit.DB.ReferencePlane.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    """

    col = rdb.FilteredElementCollector(doc).OfClass(rdb.ReferencePlane)
    return col
