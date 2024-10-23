"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A matrix class.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Supports matrices up to 4 x 4.


"""

#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2024, Jan Christel
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
from duHast.Utilities.Objects.base import Base
from duHast.Geometry.geometry_property_names import GeometryPropertyNames


class Matrix(Base):
    def __init__(self, rows=None, cols=None, elements=None, j=None):
        """
        A basic matrix class. Matrices up to size of 4x4 are supported only.

        :param rows: Number of rows, defaults to None
        :type rows: int, optional
        :param cols: Number of columns, defaults to None
        :type cols: int, optional
        :param elements: The matrix, defaults to None
        :type elements: [[float]], optional
        :param j: A json formatted settings string or dictionary, defaults to None
        :type j: str or dic, optional
        :raises TypeError: _description_
        :raises TypeError: _description_
        :raises ValueError: _description_
        :raises ValueError: _description_
        """

        # ini super
        super(Matrix, self).__init__()

        if j is not None:
            self._init_from_json(j)
        else:
            # type checking
            if isinstance(rows, int) == False:
                raise TypeError(
                    "rows must be of type int, got {} instead.".format(type(rows))
                )
            if isinstance(cols, int) == False:
                raise TypeError(
                    "cols must be of type int, got {} instead.".format(type(cols))
                )

            # check matrix size
            if rows < 1 or cols < 1 or rows > 4 or cols > 4:
                raise ValueError("Matrix dimensions must be between 1 and 4.")

            # store rows and columns
            self.rows = rows
            self.columns = cols

            if elements is None:
                # Initialize with zeros if no elements are provided
                self.data = [
                    [0.0 for _ in range(self.columns)] for _ in range(self.rows)
                ]
            else:
                # Ensure the provided elements match the specified dimensions
                if len(elements) != self.rows or any(
                    len(row) != self.columns for row in elements
                ):
                    raise ValueError("Elements must match the specified dimensions.")

                # store elements
                self.data = elements

    def _init_from_json(self, json_string):
        """
        Initialise class using the past in json string.

        :param json_string: A json formatted settings string or dictionary.
        :type json_string: str or dic
        :raises ValueError: _description_
        :raises ValueError: _description_
        :raises ValueError: _description_
        """

        try:
            # check type of json_string
            if isinstance(json_string, str):
                # Parse the JSON string
                json_string = json.loads(json_string)
            elif not isinstance(j, dict):
                raise TypeError("Input must be a JSON string or a dictionary.")

            # attempt to populate from json
            try:
                self.rows = json_string.get(GeometryPropertyNames.ROWS.value, 0)
                self.columns = json_string.get(GeometryPropertyNames.COLUMNS.value, 0)

                # populate data
                self.data = json_string.get(
                    GeometryPropertyNames.DATA.value,
                    [[0.0 for _ in range(self.columns)] for _ in range(self.rows)],
                )
            except Exception as e:
                raise ValueError(
                    "Node {} failed to initialise with: {}".format(self.data_type, e)
                )
        except (json.JSONDecodeError, ValueError) as e:
            raise ValueError("Invalid JSON input: {}".format(e))

    def __getitem__(self, idx):
        return self.data[idx]

    def __setitem__(self, idx, value):
        if len(value) != self.columns:
            raise ValueError("Row must have exactly {} elements.".format(self.columns))
        self.data[idx] = value

    def __add__(self, other):
        if (
            not isinstance(other, Matrix)
            or self.rows != other.rows
            or self.columns != other.columns
        ):
            raise ValueError("Can only add another matrix with the same dimensions.")
        return Matrix(
            self.rows,
            self.columns,
            [
                [self.data[i][j] + other[i][j] for j in range(self.columns)]
                for i in range(self.rows)
            ],
        )

    def __str__(self):
        return "\n".join(["\t".join(map(str, row)) for row in self.data])
