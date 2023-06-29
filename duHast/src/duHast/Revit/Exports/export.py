"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of functions around exporting from Revit to varies file formats.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
#
# License:
#
#
# Revit Batch Processor Sample Code
#
# Copyright (c) 2020  Jan Christel
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

#
# doSomethingWithViewName method will accept view name as arg only
def build_export_file_name_from_view(view_name, view_filter_rule, file_extension):
    """
    Function modifying the past in view name and returns a file name.

    :param view_name: The view name to be used as file name.
    :type view_name: str
    :param view_filter_rule: A prefix which will be removed from the view name.
    :type view_filter_rule: str
    :param file_extension: The file extension to be used. Format is '.something'
    :type file_extension: str
    :return: A file name.
    :rtype: str
    """

    # check if file extension is not none
    if file_extension is None:
        file_extension = ".tbc"
    # check the filter rule
    if view_filter_rule is None:
        new_file_name = view_name + file_extension
    else:
        new_file_name = view_name[len(view_filter_rule) :] + file_extension
        new_file_name = new_file_name.strip()
    return new_file_name
