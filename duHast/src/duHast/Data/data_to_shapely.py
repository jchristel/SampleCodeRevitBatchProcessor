"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Utility functions converting data retrieved from Revit into shapely geometry and processing it.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module requires python >3.9 due to dependencies:

- numpy
- shapely

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

# these packages are not available in an iron python environment .e.g. Revit Python shell
# to avoid an exception stopping the entire package to load these are within a try catch block

import shapely.geometry as sg
import numpy as np

from duHast.Data.Objects import data_ceiling as dc
from duHast.Data.Objects import data_room as dr

from duHast.Data.Objects.Properties.Geometry import geometry_polygon

# --------------- shapely polygon creation ------------------


def get_translation_matrix(geometry_object):
    """
    Gets the rotation/ translation matrix from the geometry object

    :param geometry_object: A data geometry object instance.
    :type geometry_object: :class:`.DataGeometry`

    :return: A translation matrix.
    :rtype: numpy array
    """

    translation_matrix = []  # translation only matrix
    # note numpy creates arrays by row!
    # need to append one more row since matrix dot multiplication rule:
    # number of columns in first matrix must match number of rows in second matrix (point later on)
    for vector in geometry_object.rotation_coord:
        vector.append(0.0)
        translation_matrix.append(vector)
    rotation_matrix = geometry_object.translation_coord  # rotation matrix
    # adding extra row here
    rotation_matrix.append(1.0)
    translation_matrix.append(rotation_matrix)
    # build combined rotation and translation matrix
    combined_matrix = np.array(translation_matrix)
    # transpose matrix (translation matrix in json file is stored by columns not by rows!)
    combined_matrix = np.transpose(combined_matrix)
    return combined_matrix


def get_outer_loop_as_shapely_points(geometry_object, translation_matrix):
    """
    Returns the boundary loop of an object as list of shapely points.

    Points are translated with passed in matrix.
    Any loops containing less then 3 points will be ignored. (Empty list will be returned)

    :param geometry_object: A data geometry object instance.
    :type geometry_object: :class:`.DataGeometry`
    :param translation_matrix: A translation matrix.
    :type translation_matrix: numpy array

    :return: List of shapely points defining a polygon. (Empty list will be returned if less then 3 points in loop.)
    :rtype: List[shapely.point]
    """

    single_polygon_loop = []
    if geometry_object.data_type == geometry_polygon.DataPolygon.data_type:
        for point_double in geometry_object.outer_loop:
            # need to add 1 to list for matrix multiplication
            # number of columns in first matrix (translation) must match number of rows in second matrix (point)
            translated_point = np.dot(
                translation_matrix,
                [point_double[0], point_double[1], point_double[2], 1.0],
            )
            p = sg.Point(translated_point[0], translated_point[1], translated_point[2])
            single_polygon_loop.append(p)
    # ignore any poly loops with less then 3 sides (less then 3 points)
    if len(single_polygon_loop) > 2:
        return single_polygon_loop
    else:
        return []


def get_inner_loops_as_shapely_points(geometry_object, translation_matrix):
    """
    Returns the inner loops (holes) of an object as list of lists of shapely points.

    Points are translated with passed in matrix.
    Any inner loops containing less then 3 points will be ignored. (Empty list will be returned)

    :param geoObject: A data geometry object instance.
    :type geoObject: :class:`.DataGeometry`
    :param translationM: A translation matrix.
    :type translationM: numpy array

    :return: List of lists of shapely points defining a polygon.
    :rtype: list [list[shapely.point]]
    """

    shapely_points = []
    # get inner loops
    if len(geometry_object.inner_loops) > 0:
        # there might be more then one inner loop
        for inner_loop in geometry_object.inner_loops:
            single_polygon_loop = []
            for point_double in inner_loop:
                # need to add 1 to list for matrix multiplication
                # number of columns in first matrix (translation) must match number of rows in second matrix (point)
                translated_point = np.dot(
                    translation_matrix,
                    [point_double[0], point_double[1], point_double[2], 1.0],
                )
                p = sg.Point(
                    translated_point[0], translated_point[1], translated_point[2]
                )
                single_polygon_loop.append(p)
            # ignore any poly loops with less then 3 sides ( less then 3 points)
            if len(single_polygon_loop) > 2:
                shapely_points.append(single_polygon_loop)
    return shapely_points


def build_shapely_polygon(shapely_polygons):
    """
    Creates shapely polygon with nested polygons from list of shapely polygons past in.

    Assumptions is: first polygon describes the boundary loop and any subsequent polygons are describing\
         holes within the boundary 

    :param shapely_polygons: list of shapely polygons
    :type shapely_polygons: list[shapely.polygon]

    :return: A shapely polygon.
    :rtype: shapely.polygon
    """

    # convert to shapely
    poly = None
    # check if we got multiple polygons
    if len(shapely_polygons) == 1:
        # single exterior boundary ... no holes
        poly = sg.Polygon(shapely_polygons[0])
    elif len(shapely_polygons) > 1:
        # got holes...
        # set up interior holes to be added to polygon
        # (remember exterior point order is ccw, holes cw else
        # holes may not appear as holes.)
        interiors = {}
        for i in range(1, len(shapely_polygons)):
            interiors[i - 1] = shapely_polygons[i]
        i_p = {k: sg.Polygon(v) for k, v in interiors.items()}
        # create polygon with holes
        poly = sg.Polygon(
            shapely_polygons[0],
            [
                poly.exterior.coords
                for poly in i_p.values()
                if poly.within(sg.Polygon(shapely_polygons[0])) is True
            ],
        )
    return poly


def get_shapely_polygons_from_data_instance(data_instance):
    """
    Returns a list of of shapely polygons from data instances past in.

    Polygons may contain holes

    :param data_instance: _description_
    :type data_instance: A class with .geometry property returning a :class:`.DataGeometry` instance.

    :return: A list of shapely polygons.
    :rtype: list [shapely.polygon]
    """

    all_polygons = []
    # loop over data geometry and convert into shapely polygons

    for geometry_object in data_instance.polygon:
        if geometry_object.data_type == geometry_polygon.DataPolygon.data_type:
            translation_matrix = get_translation_matrix(geometry_object)
            shape_shapely = []
            outer_loop = get_outer_loop_as_shapely_points(
                geometry_object, translation_matrix
            )
            shape_shapely.append(outer_loop)
            if len(outer_loop) > 0:
                inner_loops = get_inner_loops_as_shapely_points(
                    geometry_object, translation_matrix
                )
                if len(inner_loops) > 0:
                    for l in inner_loops:
                        shape_shapely.append(l)
            poly = build_shapely_polygon(shape_shapely)
            all_polygons.append(poly)
        else:
            print("Not a polygon data instance: {}".format(geometry_object))
    return all_polygons


# --------------- end generics ------------------

#: List of available geometry (from revit to shapely ) converters
GEOMETRY_CONVERTER = {
    dr.DataRoom.data_type: get_shapely_polygons_from_data_instance,
    dc.DataCeiling.data_type: get_shapely_polygons_from_data_instance,
}


def get_shapely_polygons_from_geo_object(geometry_objects, data_type):
    """
    Converts polygon points from DataGeometry instances to shapely polygon instances and returns them as a dictionary where:

    - key is the geometry objects id
    - value is a list of shapely polygons

    :param geometry_objects: A list of instances of the the same type (i.e DataRoom)
    :type geometry_objects: list[data object]
    :param data_type: string human readable identifying the data type ( each Data... class has this as a static field: dr.DataRoom.dataType)
    :type data_type: str

    :return: A dictionary.
    :rtype: {int:[shapely.polygon]}
    """

    multi_polygons = {}
    for i in range(len(geometry_objects)):
        multi_polygons[geometry_objects[i].instance_properties.id] = []
        poly = GEOMETRY_CONVERTER[data_type](geometry_objects[i])
        for p in poly:
            if p != None:
                multi_polygons[geometry_objects[i].instance_properties.id].append(p)
    return multi_polygons
