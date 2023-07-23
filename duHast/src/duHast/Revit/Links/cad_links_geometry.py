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
