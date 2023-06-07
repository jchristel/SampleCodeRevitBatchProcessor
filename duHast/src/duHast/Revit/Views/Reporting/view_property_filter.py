"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains the view property data filter.
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


def filter_data_by_properties(data, headers, properties, default_headers):
    """
    Filters view data by supplied property names.
    Data gets filtered twice: property needs to exist in headers list as well as in properties list.

    :param data: List of sheet properties to be kept.
    :type data: list of list of str
    :param headers: Filter: list of headers representing property names.
    :type headers: list of str
    :param properties: list of optional properties to be extracted from data
    :type properties: list of str
    :param default_headers: list of view properties always extracted from data
    :type default_headers: list of str
    :return: List of sheet properties matching filters.
    :rtype: list of list of str
    """

    # filter data out
    new_data = []
    for d in data:
        data_row = {}
        for default_head in default_headers:
            if default_head in d:
                data_row[default_head] = d[default_head]
            else:
                data_row[default_head] = "default property does not exist on element"
        for prop in properties:
            if prop in d:
                data_row[prop] = d[prop]
            else:
                data_row[prop] = "property does not exist on element"
        new_data.append(data_row)
    return new_data
