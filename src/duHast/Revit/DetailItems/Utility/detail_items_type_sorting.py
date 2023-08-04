"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a Revit detail items utility functions. 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
#
# License:
#
#
# Revit Batch Processor Sample Code
#
# Copyright (c) 2021  Jan Christel
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


def build_detail_type_ids_dictionary(collector):
    """
    Returns the dictionary keys is autodesk.revit.db element type as string and values are available type ids.

    :param collector: A filtered element collector containing detail component types.
    :type collector: Autodesk.Revit.DB.FilteredElementCollector

    :return: Dictionary where key is the element type as string and value is a list of all type ids belonging to the element type.
    :rtype: dic{str:list[Autodesk.Revit.DB.ElementId]}
    """

    dic = {}
    for c in collector:
        if dic.has_key(str(c.GetType())):
            if c.Id not in dic[str(c.GetType())]:
                dic[str(c.GetType())].append(c.Id)
        else:
            dic[str(c.GetType())] = [c.Id]
    return dic


def build_dependent_elements_dictionary(doc, collector):
    """
    Returns the dictionary keys is autodesk.revit.db element type as string and values are elements of that type.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param collector: A filtered element collector containing elements.
    :type collector: Autodesk.Revit.DB.FilteredElementCollector

    :return: Dictionary where key is the element type as string and value is a list of all elements belonging to the element type.
    :rtype: dic{str:list[Autodesk.Revit.DB.Element]}
    """

    dic = {}
    for c in collector:
        el = doc.GetElement(c)
        if dic.has_key(str(el.GetType())):
            if c not in dic[str(el.GetType())]:
                dic[str(el.GetType())].append(c)
        else:
            dic[str(el.GetType())] = [c]
    return dic
