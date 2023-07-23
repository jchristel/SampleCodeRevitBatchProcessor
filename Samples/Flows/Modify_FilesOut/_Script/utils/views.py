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
# BSD License
# Copyright © 2023, Jan Christel
# All rights reserved.

# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

# - Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# - Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# - Neither the name of Jan Christel nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
#
# This software is provided by Jan Christel "as is" and any express or implied warranties, including, but not limited to, the implied warranties of merchantability and fitness for a particular purpose are disclaimed. 
# In no event shall Jan Christel be liable for any direct, indirect, incidental, special, exemplary, or consequential damages (including, but not limited to, procurement of substitute goods or services; loss of use, data, or profits; 
# or business interruption) however caused and on any theory of liability, whether in contract, strict liability, or tort (including negligence or otherwise) arising in any way out of the use of this software, even if advised of the possibility of such damage.
#
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
