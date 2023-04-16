'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of functions around exporting from Revit to varies file formats.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''
#
#License:
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
def build_export_file_name_from_view(viewName, viewFilterRule, fileExtension):
    '''
    Function modifying the past in view name and returns a file name.

    :param viewName: The view name to be used as file name.
    :type viewName: str
    :param viewFilterRule: A prefix which will be removed from the view name.
    :type viewFilterRule: str
    :param fileExtension: The file extension to be used. Format is '.something'
    :type fileExtension: str
    :return: A file name.
    :rtype: str
    '''

    # check if file extension is not none
    if (fileExtension is None):
        fileExtension = '.tbc'
    # check the filter rule
    if (viewFilterRule is None):
        newFileName = viewName + fileExtension
    else:
        newFileName = viewName[len(viewFilterRule):] + fileExtension
        newFileName = newFileName.strip()
    return newFileName



