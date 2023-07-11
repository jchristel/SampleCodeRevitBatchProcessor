"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a view related helper functions.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- delete views not required to be retained
- delete sheets not required to be retained

"""

#!/usr/bin/python
# -*- coding: utf-8 -*-
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

# --------------------------
# Imports
# --------------------------

import clr

from duHast.Utilities.Objects import result as res
from duHast.Revit.Views.views import get_views_in_model
from duHast.Revit.Views.delete import delete_views, delete_sheets
from duHast.Revit.Views.sheets import get_all_sheets

import Autodesk.Revit.DB as rdb


def modify_views(doc, view_data, revit_file_name):
    """
    Deletes views no longer required.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param view_data: _description_
    :type view_data: _type_
    :param revit_file_name: _description_
    :type revit_file_name: _type_

    :return: _description_
    :rtype: _type_
    """
    return_value = res.Result()
    match = False
    for file_name, view_rules in view_data:
        if revit_file_name.startswith(file_name):
            # default view filter (returning true for any view past in)
            def view_filter(view):
                return True

            # get views in model
            collector_views = get_views_in_model(doc, view_filter)
            rdb.FilteredElementCollector(doc).OfClass(rdb.View)
            return_value = delete_views(doc, view_rules, collector_views)
            match = True
            break
    if match == False:
        return_value.update_sep(False, "No view filter rule(s) for this file found!")
    return return_value


def modify_sheets(doc, sheets, revit_file_name):
    """
    Deletes sheets no longer required.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param sheets: _description_
    :type sheets: _type_
    :param revit_file_name: _description_
    :type revit_file_name: _type_

    :return: _description_
    :rtype: _type_
    """

    return_value = res.Result()
    match = False
    for file_name, sheet_rules in sheets:
        if revit_file_name.startswith(file_name):
            collectorSheets = get_all_sheets(doc)
            return_value = delete_sheets(doc, sheet_rules, collectorSheets)
            match = True
            break
    if match == False:
        return_value.update_sep(False, "No sheet filter rule(s) for this file found!")
    return return_value
