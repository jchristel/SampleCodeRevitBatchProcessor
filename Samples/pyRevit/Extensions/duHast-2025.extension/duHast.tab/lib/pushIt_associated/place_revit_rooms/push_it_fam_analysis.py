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

from System.Linq import Enumerable
from System import Int64 # revit element Id expects 64 bit integer

from duHast.Utilities.Objects.result import Result

from Autodesk.Revit.DB import ElementId,GeometryElement,GeometryInstance, Options,Solid, ViewDetailLevel



def get_centroid_from_solid(geom_solid):
    """
    Get the centroid of a solid in Revit.
    :param geom_solid: The solid to get the centroid from
    :type geom_solid: Autodesk.Revit.DB.Solid
    :return: The centroid of the solid
    :rtype: list
    """

    centroids = []
    try:
        # get the centroid of the solid
        centroid=geom_solid.ComputeCentroid()
        centroids.append(centroid)
        return centroids
    except Exception as e:
        return []


def process_geo_instance(geo_instance):
    """
    Process a geometry instance and return the centroid of the solid.
    
    :param geo_instance: The geometry instance
    :type geo_instance: Autodesk.Revit.DB.GeometryInstance
    :return: The centroid of the solid
    :rtype: Autodesk.Revit.DB.XYZ
    """
    
    centroids = []
    
    geom_el = geo_instance.GetInstanceGeometry()
    
    if isinstance(geom_el, Solid):
        centroids.extend(get_centroid_from_solid(geom_el))
    elif isinstance(geom_el, GeometryInstance):
        centroids.extend(process_geo_instance(geom_el))
    elif isinstance(geom_el, GeometryElement):
        centroids.extend(process_geo_element(geom_el))
    else:
        pass
    return centroids


def  process_geo_element(geom_el):

    centroids = []
    
    # this can be an enumerator but also just a basic geometry primitive (curve)
    if hasattr(geom_el, "GetEnumerator"):

        # if it has an enumerator, we can iterate over it
        enumerator = geom_el.GetEnumerator()

        while enumerator.MoveNext():

            nested_geom_el = enumerator.Current
        
            if isinstance(nested_geom_el, Solid):
                centroids.extend(get_centroid_from_solid(nested_geom_el))
            elif isinstance(nested_geom_el, GeometryInstance):
                centroids.extend(process_geo_instance(nested_geom_el))
            elif isinstance(geom_el, GeometryElement):
                centroids.extend(process_geo_element(nested_geom_el))
            else:
                pass
    elif isinstance(geom_el, Solid):
        centroids.extend(get_centroid_from_solid(geom_el))
    else:
        pass
        # anything else gets ignored

    return centroids


def get_family_centroid(doc, family_instance):
    """
    Get the centroid of a family instance in Revit based on family geometry. If that fails, it will use the insertion point of the family instance.
    
    :param doc: The Revit document
    :type doc: Autodesk.Revit.DB.Document
    :param family_instance: The push it family instance
    :type family_instance: Autodesk.Revit.DB.FamilyInstance
    :return: The centroid of the family instance
    :rtype: Autodesk.Revit.DB.XYZ
    """
    
    return_value = Result()
    
    try:
        # get the actual family instance
        revit_family_instance = doc.GetElement(ElementId(Int64(family_instance.revit_element_id_integer_value)))

        # get the geometry of the family instance
        opt = Options()
        opt.ComputeReferences = True
        opt.IncludeNonVisibleObjects = True
        opt.DetailLevel = ViewDetailLevel.Medium
        geom_element = revit_family_instance.get_Geometry(opt)

        # set up the centroid container
        centroids = []

        return_value.append_message("Processing geometry elements: {} {}".format(geom_element, type(geom_element)))

        for geom_el in geom_element:
            # if solid process directly
            if isinstance(geom_el, Solid):
                return_value.append_message("Processing a solid")
                centroids.extend(get_centroid_from_solid(geom_el))
            # if geometry instance process recursively
            elif isinstance(geom_el, GeometryInstance):
                return_value.append_message("Processing geometry instance")
                centroids.extend(process_geo_instance( geom_el))
            elif isinstance(geom_el, GeometryElement):
                return_value.append_message("Processing geometry element")
                centroids.extend(process_geo_element(geom_el))
            else:
                return_value.append_message("ignoring geometry element of type: {}".format(type(geom_el)))
                pass
               

        # get the average of the centroids
        if len(centroids) > 1:
            x = sum([centroid.X for centroid in centroids]) / len(centroids)
            y = sum([centroid.Y for centroid in centroids]) / len(centroids)
            z = sum([centroid.Z for centroid in centroids]) / len(centroids)
            family_instance.set_centroid(x,y,z)
        elif len(centroids) == 1:
            family_instance.set_centroid(centroids[0].X, centroids[0].Y, centroids[0].Z)
        else:
            # ok no centroids found...go with insertion point
            family_instance.set_centroid(revit_family_instance.Location.Point.X, revit_family_instance.Location.Point.Y, revit_family_instance.Location.Point.Z)
        
        return_value.result=[family_instance]

    except Exception as e:
        return_value.update_sep(False, "in get_family_centroid: {}".format(e))
    
    return return_value


def get_push_it_families_centroid(doc, push_it_families):
    """
    Get the centroid of pushIt families in Revit.
    
    :param doc: The Revit document
    :type doc: Autodesk.Revit.DB.Document
    :param push_it_families: The pushIt families
    :type push_it_families: list
    
    :return: Result class instance.
    
        - `result.status` (bool): True if all families were updated successfully, otherwise False.
        - `result.message` (str): Confirmation of successful update.
        - `result.result` (list): List of updated family instances.
    On exception:
        - `result.status` (bool): False.
        - `result.message` (str): Generic exception message.
        - `result.result` (list): Empty.
    :rtype: :class:`.Result`
    """

    return_value = Result()
    updated_families = []
    try:
        # loop over families and attempt to get the centroid of the extrusion
        for family in push_it_families:
            family_instance_update_result = get_family_centroid(doc, family)
            if family_instance_update_result.status:
                updated_families.append(family_instance_update_result.result[0])
                return_value.append_message("Centroid of family instance {}".format(family.get_ui_name()))
            else:
                return_value.update_sep(False, "Failed to get centroid of family instance: {}".format(family_instance_update_result.message))

        return_value.result = updated_families

    except Exception as e:
        return_value.update_sep(False, "Failed to get centroids of pushIt families: {}".format(e))

    return return_value