"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Geometry data storage class.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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
from duHast.Data.Objects.Collectors import data_base
from duHast.Data.Objects.Collectors.Properties.data_property_names import DataPropertyNames
from duHast.Geometry.point_3 import Point3
from duHast.Geometry.matrix import Matrix

class DataGeometryBase(data_base.DataBase):
    def __init__(self, data_type, j=None, **kwargs):
        """
        Class constructor

        :param j:  json formatted dictionary of this class, defaults to {}
        :type j: dict, optional
        """
        
        # store data type  in base class
        super(DataGeometryBase, self).__init__(data_type=data_type, j=j, **kwargs)

        # set default values
        # translation as per shared coordinates in revit file
        self.translation_coord = Point3(0.0, 0.0, 0.0)
        # rotation as per shared coordinates in revit file ( default )
        self.rotation_coord = Matrix(rows=3, cols=3)

        json_var=None
        # check if any data was past in with constructor!
        if j is not None:
            # check type of data that came in:
            if isinstance(j, str):
                # a string
                json_var = json.loads(j)
            elif isinstance(j, dict):
                # make a copy
                json_var=j.copy()
            else:
                raise TypeError(
                    "Argument j supplied must be of type string or type dictionary. Got {} instead.".format(
                        type(j)
                    )
                )

            # attempt to populate from json
            try:
                translation_coord = json_var.get(
                    DataPropertyNames.TRANSLATION_COORDINATES, None
                )
                # check if we got None back...if so use what is the default
                # since a point can be initialized with None
                if translation_coord is not None:
                    self.translation_coord = self._translation_from_json(
                        translation_coord
                    )

                rotation_coord = json_var.get(
                    DataPropertyNames.ROTATION_COORDINATES, None
                )
                # check if we got None back...if so use what is the default
                if rotation_coord is not None:
                    self.rotation_coord = self._rotation_from_json(rotation_coord)

            except Exception as e:
                raise type(e)(
                    "Node {} failed to initialise with: {}".format(self.data_type, e)
                )

    @staticmethod
    def _translation_from_json(value):
        """
        Builds the translation point from json.

        Accepts the dictionary a Point3 serialises to, and the bare [x, y] or
        [x, y, z] list older exports wrote here. Data holding the list form could not
        be read back at all until now, since Point3 is built from a dictionary.

        :param value: The stored translation.
        :type value: dict | list | tuple

        :return: The translation as a point.
        :rtype: :class:`.Point3`
        """

        if isinstance(value, dict):
            return Point3(j=value)

        if isinstance(value, (list, tuple)):
            if len(value) < 2:
                raise ValueError(
                    "Translation needs at least an x and a y value, got {}.".format(
                        len(value)
                    )
                )
            # older exports dropped z, so it defaults rather than failing
            return Point3(
                x=float(value[0]),
                y=float(value[1]),
                z=float(value[2]) if len(value) > 2 else 0.0,
            )

        raise TypeError(
            "Translation must be a dictionary, list or tuple. Got {} instead.".format(
                type(value)
            )
        )

    @staticmethod
    def _rotation_from_json(value):
        """
        Builds the rotation matrix from json.

        Accepts the dictionary a Matrix serialises to, and the list of rows older
        exports wrote here. Data holding the list form could not be read back at all
        until now, since Matrix is built from a dictionary. Rows of two are accepted
        as well as three, because exports made while the z component was being dropped
        hold a 3 x 2.

        :param value: The stored rotation.
        :type value: dict | list | tuple

        :return: The rotation as a matrix.
        :rtype: :class:`.Matrix`
        """

        if isinstance(value, dict):
            return Matrix(j=value)

        if isinstance(value, (list, tuple)):
            if len(value) == 0 or not isinstance(value[0], (list, tuple)):
                raise ValueError(
                    "Rotation as a list must hold one list per row, got {}.".format(
                        value
                    )
                )
            return Matrix(
                rows=len(value),
                cols=len(value[0]),
                elements=[list(row) for row in value],
            )

        raise TypeError(
            "Rotation must be a dictionary, list or tuple. Got {} instead.".format(
                type(value)
            )
        )

    def __eq__(self, other):
        if not isinstance(other, DataGeometryBase):
            return NotImplemented
        return (
            self.translation_coord == other.translation_coord
            and self.rotation_coord == other.rotation_coord
        )

    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __hash__(self):
        return hash((self.translation_coord, self.rotation_coord))
