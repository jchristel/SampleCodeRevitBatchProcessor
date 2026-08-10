"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A matrix class.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Supports matrices from 1 x 1 up to 4 x 4.


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
import copy

from duHast.Utilities.Objects.base import Base
from duHast.Geometry.geometry_property_names import GeometryPropertyNames
from duHast.Geometry.Exceptions.incompatible_matrix_dimension import (
    IncompatibleMatrixDimensions,
)
from duHast.Utilities.compare import is_close


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
        :raises TypeError: Thrown if row is not an integer and no json is provided
        :raises TypeError: Thrown if cols is not an integer and no json is provided
        :raises ValueError: Thrown if matrix size exceeds 4 x 4 or is rows or columns is less than 1
        :raises ValueError: Thrown if elements provided do not match rows and cols count
        """

        super(Matrix, self).__init__()

        if j is not None:
            self._init_from_json(j)
        else:
            self._validate_dimensions(rows, cols)

            self._rows = rows
            self._columns = cols

            if elements is None:
                self._data = [
                    [0.0 for _ in range(self._columns)] for _ in range(self._rows)
                ]
            else:
                # make sure elements are of the right type and size
                self._validate_elements(elements)

    def _init_from_json(self, json_string):
        """
        Initialise class using the past in json string.

        :param json_string: A json formatted settings string or dictionary.
        :type json_string: str or dic
        :raises ValueError: Input must be a JSON string or a dictionary
        """

        try:
            if isinstance(json_string, str):
                json_string = json.loads(json_string)
            elif not isinstance(json_string, dict):
                raise TypeError("Input must be a JSON string or a dictionary.")

            rows = json_string.get(GeometryPropertyNames.ROWS, 0)
            columns = json_string.get(GeometryPropertyNames.COLUMNS, 0)

            # the same checks the direct constructor applies. Without them json could
            # build matrices the class does not support at all - a 0 x 0 from missing
            # keys, or anything larger than the 4 x 4 limit.
            self._validate_dimensions(rows, columns)

            self._rows = rows
            self._columns = columns

            elements_from_json = json_string.get(
                GeometryPropertyNames.DATA,
                [[0.0 for _ in range(self._columns)] for _ in range(self._rows)],
            )
            self._validate_elements(
                elements_from_json
            )  # Validate after loading from JSON
        except Exception as e:
            raise ValueError("Invalid JSON input: {}".format(e))

    @staticmethod
    def _validate_dimensions(rows, cols):
        """
        Checks a row and column count is something this class supports.

        Shared by both construction paths, so json cannot build a matrix the direct
        constructor would refuse.

        :param rows: Number of rows.
        :type rows: int
        :param cols: Number of columns.
        :type cols: int
        :raises TypeError: Thrown if rows or cols is not an integer.
        :raises ValueError: Thrown if either falls outside 1 to 4.
        """

        if not isinstance(rows, int):
            raise TypeError(
                "rows must be of type int, got {} instead.".format(type(rows))
            )
        if not isinstance(cols, int):
            raise TypeError(
                "cols must be of type int, got {} instead.".format(type(cols))
            )
        if rows < 1 or cols < 1 or rows > 4 or cols > 4:
            raise ValueError("Matrix dimensions must be between 1 and 4.")

    def _validate_elements(self, elements):
        """Validate that the elements are all floats."""
        if len(elements) != self._rows or any(
            len(row) != self._columns for row in elements
        ):
            raise ValueError("Elements must match the specified dimensions.")

        for row in elements:
            for value in row:
                if not isinstance(value, (float, int)):  # Allow both float and int
                    raise TypeError("All elements must be of type float or int.")

        # a COPY, not the list which was passed in. Storing the caller's list left them
        # holding a live reference into the matrix, so changing their own list after
        # construction silently rewrote it - from outside the class entirely, past the
        # validation above and past __setitem__. One row deep is enough, the values
        # themselves being numbers.
        self._data = [list(row) for row in elements]

    @property
    def rows(self):
        """Read-only property for the number of rows."""
        return self._rows

    @property
    def columns(self):
        """Read-only property for the number of columns."""
        return self._columns

    @property
    def data(self):
        """Read-only property for the matrix data."""
        return copy.deepcopy(self._data)

    def __getitem__(self, idx):
        return self._data[idx]

    def __setitem__(self, idx, value):
        if len(value) != self.columns:
            raise ValueError("Row must have exactly {} elements.".format(self.columns))
        # copied for the same reason as in _validate_elements: assigning the caller's
        # list would hand them a live reference into the matrix through this door
        self._data[idx] = list(value)

    def __add__(self, other):
        if not isinstance(other, Matrix):
            raise TypeError(
                "other must be of type matrix, got {} instead.".format(other)
            )
        elif self.rows != other.rows or self.columns != other.columns:
            raise IncompatibleMatrixDimensions(
                "Can only add another matrix with the same dimensions.", other
            )
        return Matrix(
            self.rows,
            self.columns,
            [
                [self._data[i][j] + other[i][j] for j in range(self.columns)]
                for i in range(self.rows)
            ],
        )

    def __str__(self):
        return "\n".join(["\t".join(map(str, row)) for row in self._data])

    def __eq__(self, other):
        if not isinstance(other, Matrix):
            return NotImplemented

        if self.rows != other.rows or self.columns != other.columns:
            return False

        return all(
            is_close(self._data[i][j], other[i][j])
            for i in range(self.rows)
            for j in range(self.columns)
        )

    def __ne__(self, other):
        return not (self == other)

    def __hash__(self):
        # the element values are deliberately left out. __eq__ compares them with a
        # tolerance, so two matrices can be equal while their elements differ, and a
        # hash built from those elements lets a set keep two entries which compare
        # equal to each other. The shape is exact under __eq__, so it can take part.
        return hash((type(self).__name__, self.rows, self.columns))