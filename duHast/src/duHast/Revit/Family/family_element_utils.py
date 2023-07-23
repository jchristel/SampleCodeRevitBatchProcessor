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
# BSD License
# Copyright © 2023, Jan Christel
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
