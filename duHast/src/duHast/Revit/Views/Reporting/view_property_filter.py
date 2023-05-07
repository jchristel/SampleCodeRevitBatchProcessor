'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains the view property data filter.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''
#
#License:
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


def filter_data_by_properties(data, headers, sheet_properties, default_headers):
    '''
    Filters view data by supplied property names.
    Data gets filtered twice: property needs to exist in headers list as well as in sheet properties list.

    :param data: List of sheet properties to be kept.
    :type data: list of list of str
    :param headers: Filter: list of headers representing property names.
    :type headers: list of str
    :param sheet_properties: list of optional view properties to be extracted from data
    :type sheet_properties: list of str
    :param default_headers: list of view properties always extracted from data
    :type default_headers: list of str
    :return: List of sheet properties matching filters.
    :rtype: list of list of str
    '''

    # add default headers to properties to be filtered first
    data_index_list= [iter for iter in range(len(default_headers))]
    # build index pointer list of data to be kept
    for f in sheet_properties:
        if (f in headers):
            data_index_list.append(headers.index(f))
    # filter data out
    new_data = []
    for d in data:
        data_row = []
        for i in data_index_list:
            data_row.append(d[i])
        new_data.append(data_row)
    return new_data