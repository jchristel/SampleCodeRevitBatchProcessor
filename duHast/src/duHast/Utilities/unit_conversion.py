"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of unit conversion functions
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


def convert_imperial_feet_to_metric_mm(value):
    """
    Converts feet and inches to mm
    :param value: The value in feet to be converted
    :type value: float
    :return: The converted value
    :rtype: float
    """

    return value * 304.8


def convert_imperial_square_feet_to_metric_square_metre(value):
    """
    Converts square feet and inches to square m

    :param value: The value in square feet to be converted
    :type value: float
    :return: The converted value
    :rtype: float
    """

    return value * 0.092903


def convert_imperial_cubic_feet_to_metric_cubic_metre(value):
    """
    Converts cubic feet and inches to cubic m

    :param value: The value in cubic feet to be converted
    :type value: float
    :return: The converted value
    :rtype: float
    """

    return value * 0.02831685
