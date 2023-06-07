"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains the view property utilities.
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

def convert_view_data_to_list(view_data, headers):
    """
    Converts a list of dictionaries of view properties names and values to a list of properties only.

    :param view_data: List of dictionaries representing view properties
    :type view_data: [{}]
    :param headers: list of properties
    :type headers: [str]
    :return: A list of lists of view property values.
    :rtype: [[str]]
    """

    data = []
    for view_d in view_data:
        data_row = []
        for header in headers:
            if header in view_d:
                data_row.append(view_d[header])
            else:
                data_row.append("Property does not exist on element.")
        data.append(data_row)
    return data