"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to CAD link geometry.
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

from duHast.Revit.Links.cad_links import get_all_cad_link_instances


def get_cad_import_instance_geometry(import_instance):
    """
    Returns a list of geometry elements from an import instance
    :param import_instance: A import instance
    :type import_instance: AutoDesk.Revit.DB.ImportInstance
    :return: A list of geometry objects. Can return an empty list!
    :rtype: [Autodesk.Revit.DB GeometryObject]
    """

    geo = []
    # default geometry option
    opt = rdb.Options()
    geo_elem_level1 = import_instance.get_Geometry(opt)
    if geo_elem_level1 != None:
        for geo_instance in geo_elem_level1:
            if geo_instance != None:
                geo_elem_level2 = geo_instance.GetInstanceGeometry()
                if geo_elem_level2 != None:
                    for item in geo_elem_level2:
                        geo.append(item)
    return geo


def get_all_cad_import_instances_geometry(doc):
    """
    Returns a list of geometry elements from all import instances in the document.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A list of geometry objects. Can return an empty list!
    :rtype: [Autodesk.Revit.DB GeometryObject]
    """
    instances_geometry = []
    all_import_instances = get_all_cad_link_instances(doc)
    for import_instance in all_import_instances:
        geometry_instances = get_cad_import_instance_geometry(import_instance)
        if len(geometry_instances) > 0:
            instances_geometry += geometry_instances
    return instances_geometry
