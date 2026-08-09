"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Polygon geometry data storage class.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A polygon consists, as a minimum, of an outer loop, but may also have any number of inner loops. Those inner loops describe holes in the surface the outer loop decribes.

Loops are made up of a number of 2D points.


"""

#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2023, Jan Christel
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

import json
from duHast.Data.Objects.Collectors.Properties.Geometry import geometry_base
from duHast.Data.Objects.Collectors.Properties.data_property_names import DataPropertyNames
from duHast.Geometry.geometry_property_names import GeometryPropertyNames
from duHast.Geometry.point_2 import Point2


def loop_point_from_json(point):
    """
    Normalises a single loop point read from json into a list of doubles.

    Two shapes exist in the wild. Every exporter writes loop points as [x, y] lists,
    via get_point_as_doubles, and that is also the shape data_to_shapely reads back
    out - it indexes point[0] and point[1] and tests len(point) to spot 2D points.
    A Point2, on the other hand, serialises to an {"x": , "y": } dictionary.

    Both are accepted here and both come back as [x, y], because a polygon that has
    been through json has to hand downstream code the same type an exported one does.
    Returning Point2 instances - as this used to - produced polygons that no consumer
    in the library could read.

    :param point: A single loop point as either [x, y] or {"x": , "y": }.
    :type point: list | tuple | dict

    :return: The point as [x, y].
    :rtype: list[float]
    """

    if isinstance(point, dict):
        if (
            GeometryPropertyNames.X not in point
            or GeometryPropertyNames.Y not in point
        ):
            raise ValueError("Loop point dictionary must contain 'x' and 'y' keys.")
        return [
            float(point[GeometryPropertyNames.X]),
            float(point[GeometryPropertyNames.Y]),
        ]

    if isinstance(point, (list, tuple)):
        if len(point) < 2:
            raise ValueError(
                "Loop point needs at least an x and a y value, got {} value(s).".format(
                    len(point)
                )
            )
        # anything beyond x and y is dropped: these polygons are 2D by definition
        return [float(point[0]), float(point[1])]

    raise TypeError(
        "Loop point must be a list, tuple or dictionary. Got {} instead.".format(
            type(point)
        )
    )


def loop_as_tuple(loop):
    """
    Converts a single loop into a nested tuple so that it can take part in a hash.

    Loops are lists of points, and points are themselves lists, neither of which is
    hashable. Both point shapes the class can hold are handled: the [x, y] lists the
    exporters and json produce, and the Point2 instances add_point_to_outer_loop takes.

    :param loop: A loop as a list of points.
    :type loop: list

    :return: The loop as a tuple of (x, y) tuples.
    :rtype: tuple
    """

    points = []
    for point in loop:
        if hasattr(point, GeometryPropertyNames.X) and hasattr(
            point, GeometryPropertyNames.Y
        ):
            points.append((point.x, point.y))
        else:
            points.append(tuple(point))
    return tuple(points)


class DataGeometryPolygon2(geometry_base.DataGeometryBase):
    data_type = "polygon"

    def __init__(self, j=None):
        """
        Class constructor for a 2d polygon.

        :param j:  json formatted dictionary of this class, defaults to {}
        :type j: dict, optional
        """

        # store data type  in base class and pass on json string!!!
        super(DataGeometryPolygon2, self).__init__(DataGeometryPolygon2.data_type, j)

        # set default values
        self.outer_loop = []
        self.inner_loops = []

        json_var = None
        # check if any data was past in with constructor!
        if j is not None:
            # check type of data that came in:
            if isinstance(j, str):
                # a string
                json_var = json.loads(j)
            elif isinstance(j, dict):
                # no action required
                json_var = j.copy()
            else:
                raise TypeError(
                    "Argument j supplied must be of type string or type dictionary. Got {} instead.".format(
                        type(j)
                    )
                )

            # attempt to populate from json
            try:
                # get outer points loop
                outer_loop = json_var.get(DataPropertyNames.OUTER_LOOP, [])

                # need a minimum of 3 points to form a polygon
                if len(outer_loop) >= 3:
                    for p in outer_loop:
                        self.outer_loop.append(loop_point_from_json(p))
                elif 3 > len(outer_loop) > 0:
                    # not enough points
                    raise ValueError(
                        "outer loop data needs to contain at least 3 points"
                    )
                else:
                    # a polygon must contain at least an outer loop...
                    raise ValueError("Json did not contain any outer loop data")

                # get inner loops
                inner_loops = json_var.get(DataPropertyNames.INNER_LOOPS, [])
                if len(inner_loops) > 0:
                    for loop in inner_loops:
                        loop_points = []
                        for p in loop:
                            loop_points.append(loop_point_from_json(p))
                        self.inner_loops.append(loop_points)

            except Exception as e:
                msg = "Node {} failed to initialise with: {}".format(self.data_type, e)
                raise type(e)(msg)

    def add_point_to_outer_loop(self, point):
        """
        Adds a point to the outer loop.

        :param point: Point2 instance to add to the outer loop
        :type point: Point2
        :raises TypeError: if the point is not an instance of Point2
        """

        if not isinstance(point, Point2):
            raise TypeError("Point must be an instance of Point2.")
        self.outer_loop.append(point)

    def add_inner_loop(self, loop):
        """
        Adds a new inner loop to the inner loops list.

        :param loop: List of Point2 instances representing an inner loop
        :type loop: list[Point2]
        :raises ValueError: if the loop does not contain at least 3 points
        :raises TypeError: if any element in the loop is not an instance of Point2
        """

        if len(loop) < 3:
            raise ValueError("An inner loop must contain at least 3 points.")
        if not all(isinstance(point, Point2) for point in loop):
            raise TypeError("All points in the loop must be instances of Point2.")
        self.inner_loops.append(loop)

    def __eq__(self, other):
        if not isinstance(other, DataGeometryPolygon2):
            return NotImplemented
        return (
            self.outer_loop == other.outer_loop
            and self.inner_loops == other.inner_loops
        )

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        # built from the same two properties __eq__ compares, so that equal polygons
        # hash equal. Both are nested lists, so they have to be converted to tuples:
        # hashing them directly raised a TypeError for every polygon.
        return hash(
            (
                loop_as_tuple(self.outer_loop),
                tuple(loop_as_tuple(loop) for loop in self.inner_loops),
            )
        )