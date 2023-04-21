'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Revit line line styles helper functions. 
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

import clr
clr.AddReference("System.Core")
from System import Linq
clr.ImportExtensions(Linq)

import Autodesk.Revit.DB as rdb
from duHast.APISamples.Common import delete as rDel


def delete_line_styles_starts_with(doc, starts_with):
    '''
    Deletes all line styles where the name starts with provided string
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param starts_with: Filter: style name needs to start with this string to be deleted.
    :type starts_with: str
    :return: 
        Result class instance.
        - .result = True if all views where deleted. Otherwise False.
        - .message will contain deletion status.
    :rtype: :class:`.Result`
    '''

    lc = doc.Settings.Categories[rdb.BuiltInCategory.OST_Lines]
    ids = list(c.Id for c in lc.SubCategories if c.Name.StartsWith(starts_with)).ToList[rdb.ElementId]()
    result = rDel.delete_by_element_ids(doc,ids, 'Delete line styles where name starts with: ' + str(starts_with),'line styles starting with: ' + str(starts_with))
    return result


def get_all_line_style_ids(doc):
    '''
    Gets all line styles ids in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A list of all line style ids.
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    lc = doc.Settings.Categories[rdb.BuiltInCategory.OST_Lines]
    ids = list(c.Id for c in lc.SubCategories).ToList[rdb.ElementId]()
    return ids